import sqlite3
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from .kroger_api_utils import KrogerAPI, KrogerProduct, KrogerAPIError
from errors import DatabaseError

logger = logging.getLogger(__name__)


@dataclass
class IngredientDetail:
    ingredient_id: int
    name: str
    quantity: float
    measurement_unit: str
    recipe_id: int


@dataclass
class ShoppingListItem:
    ingredient_name: str
    quantity: float
    measurement_unit: str
    product_name: str
    brand: str
    price: float
    category: str
    store_location: Optional[str] = None


class KrogerPipeline:
    def __init__(self, client_id: str, client_secret: str, location_id: str, db_path: str = "smartshelf.db"):
        self.api = KrogerAPI(client_id, client_secret)
        self.location_id = location_id
        self.db_path = db_path
        self.api.get_access_token()  # Ensure token is ready
        logger.info(f"Initialized KrogerPipeline with location_id: {location_id}")

    def _get_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")

    def find_kroger_product(self, ingredient: IngredientDetail) -> Optional[KrogerProduct]:
        """Search for Kroger product matching ingredient"""
        try:
            products = self.api.search_products(
                ingredient=ingredient.name,
                location_id=self.location_id,
                limit=1
            )
            return products[0] if products else None
        except Exception as e:
            logger.error(f"Error finding product for {ingredient.name}: {e}")
            return None

    def save_kroger_product(self, product: KrogerProduct) -> int:
        """Save Kroger product to database"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if product exists
            cursor.execute("""
                SELECT product_id FROM KrogerProduct
                WHERE name = ? AND brand = ?
            """, (product.name, product.brand))
            existing = cursor.fetchone()
            if existing:
                return existing['product_id']
            # Insert new product
            cursor.execute("""
                INSERT INTO KrogerProduct (name, description, price, brand, category)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.name,
                product.description,
                product.price,
                product.brand,
                product.category
            ))
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
        finally:
            conn.close()

    def link_ingredient_to_product(self, ingredient: IngredientDetail, kroger_product_id: int) -> bool:
        """Create grocery item linking ingredient to Kroger product"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if link exists
            cursor.execute("""
                SELECT item_id FROM GroceryItem 
                WHERE ingredient_id = ? AND kroger_product = ?
            """, (ingredient.ingredient_id, kroger_product_id))
            if not cursor.fetchone():
                # Create new link
                cursor.execute("""
                    INSERT INTO GroceryItem (name, ingredient_id, kroger_product)
                    VALUES (?, ?, ?)
                """, (ingredient.name, ingredient.ingredient_id, kroger_product_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error linking ingredient {ingredient.name}: {e}")
            return False
        finally:
            conn.close()

    def process_recipe(self, recipe_id: int, verbose: bool = False) -> Dict:
        """Process recipe and generate shopping list"""
        try:
            logger.info(f"Processing recipe {recipe_id}")
            results = {
                "recipe": None,
                "shopping_list": [],
                "total_cost": 0.0,
                "processed_at": datetime.now().isoformat()
            }
            # Get recipe details
            recipe = self.get_recipe_details(recipe_id)
            if not recipe:
                raise DatabaseError("Recipe not found")
            results["recipe"] = recipe
            # Get and process ingredients
            ingredients = self.get_recipe_ingredients(recipe_id)
            for ingredient in ingredients:
                # Find matching product
                product = self.find_kroger_product(ingredient)
                if product:
                    # Save product and create link
                    product_id = self.save_kroger_product(product)
                    self.link_ingredient_to_product(ingredient, product_id)
                else:
                    logger.warning(f"No product found for: {ingredient.name}")
            # Generate shopping list
            shopping_list = self.get_shopping_list(recipe_id)
            results["shopping_list"] = [vars(item) for item in shopping_list]
            results["total_cost"] = sum(item.price for item in shopping_list)
            if verbose:
                logger.info(f"Processed recipe: {recipe['name']}")
                logger.info(f"Found {len(shopping_list)} items")
                logger.info(f"Total cost: ${results['total_cost']:.2f}")
            return results
        except Exception as e:
            logger.error(f"Error processing recipe {recipe_id}: {e}")
            raise

    def get_recipe_details_all(self) -> List[Dict]:
        """Get all recipes from database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, name, category, cuisine_type, cooking_time, difficulty_level
                FROM Recipe
            """)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Database error fetching recipes: {e}")
            raise DatabaseError(f"Failed to fetch recipes: {str(e)}")

    def get_recipe_details(self, recipe_id: int) -> Optional[Dict]:
        """Get recipe details by ID"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, name, category, cuisine_type, cooking_time, difficulty_level
                FROM Recipe
                WHERE recipe_id = ?
            """, (recipe_id,))
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        except sqlite3.Error as e:
            logger.error(f"Database error fetching recipe {recipe_id}: {e}")
            raise DatabaseError(f"Failed to fetch recipe: {str(e)}")

    def get_recipe_ingredients(self, recipe_id: int) -> List[IngredientDetail]:
        """Get ingredients for a recipe"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ingredient_id, name, quantity, measurement_unit, recipe_id
                FROM Ingredient
                WHERE recipe_id = ?
            """, (recipe_id,))
            results = cursor.fetchall()
            conn.close()
            return [
                IngredientDetail(
                    ingredient_id=row['ingredient_id'],
                    name=row['name'],
                    quantity=row['quantity'],
                    measurement_unit=row['measurement_unit'],
                    recipe_id=row['recipe_id']
                )
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(f"Database error fetching ingredients for recipe {recipe_id}: {e}")
            raise DatabaseError(f"Failed to fetch ingredients: {str(e)}")

    def get_shopping_list(self, recipe_id: int) -> List[ShoppingListItem]:
        """Get shopping list for a recipe"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    i.name as ingredient_name,
                    i.quantity,
                    i.measurement_unit,
                    kp.name as product_name,
                    kp.brand,
                    kp.price,
                    kp.category
                FROM Ingredient i
                JOIN GroceryItem gi ON i.ingredient_id = gi.ingredient_id
                JOIN KrogerProduct kp ON gi.kroger_product = kp.product_id
                WHERE i.recipe_id = ?
            """, (recipe_id,))
            results = cursor.fetchall()
            conn.close()
            return [
                ShoppingListItem(
                    ingredient_name=row['ingredient_name'],
                    quantity=row['quantity'],
                    measurement_unit=row['measurement_unit'],
                    product_name=row['product_name'],
                    brand=row['brand'],
                    price=row['price'],
                    category=row['category']
                )
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(f"Database error fetching shopping list for recipe {recipe_id}: {e}")
            raise DatabaseError(f"Failed to fetch shopping list: {str(e)}")
