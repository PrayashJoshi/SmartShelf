import sqlite3
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from pipelines.kroger_api_utils import KrogerAPI, KrogerProduct, KrogerAPIError
from errors import DatabaseError
import shortuuid

logger = logging.getLogger(__name__)


@dataclass
class IngredientDetail:
    ingredient_id: int
    name: str
    quantity: float
    measurement_unit: str
    recipe_id: int
    calories: int
    protein: int
    fat: int
    carbs: int


@dataclass
class IngredientPartial:
    name: str
    quantity: float
    measurement_unit: str


@dataclass
class RecipeDetail:
    name: str
    category: float
    cuisine_type: str
    cooking_time: int
    difficulty_level: int
    ingredients: List[IngredientPartial]


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


class IngredientPipeline:
    """Recipes + Ingredients"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        location_id: str,
        db_path: str = "smartshelf.db",
    ):
        self.api = KrogerAPI(client_id, client_secret)
        self.location_id = location_id
        self.db_path = db_path
        self.api.get_access_token()  # Ensure token is ready
        logger.info(f"Initialized IngredientPipeline with location_id: {location_id}")

    def _get_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")

    def find_kroger_product(
        self, ingredient: IngredientDetail
    ) -> Optional[KrogerProduct]:
        """Search for Kroger product matching ingredient"""
        try:
            products = self.api.search_products(
                ingredient=ingredient.name, location_id=self.location_id, limit=1
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
            cursor.execute(
                """
                SELECT product_id FROM KrogerProduct
                WHERE name = ? AND brand = ?
                """,
                (product.name, product.brand),
            )
            existing = cursor.fetchone()
            if existing:
                return existing["product_id"]
            # Insert new product
            cursor.execute(
                """
                INSERT INTO KrogerProduct (name, description, price, brand, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    product.name,
                    product.description,
                    product.price,
                    product.brand,
                    product.category,
                ),
            )
            product_id = cursor.lastrowid
            conn.commit()
            return product_id
        finally:
            conn.close()

    def link_ingredient_to_product(
        self, ingredient: IngredientDetail, kroger_product_id: int
    ) -> bool:
        """Create grocery item linking ingredient to Kroger product"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if link exists
            cursor.execute(
                """
                SELECT item_id FROM GroceryItem
                WHERE ingredient_id = ? AND kroger_product = ?
                """,
                (ingredient.ingredient_id, kroger_product_id),
            )
            if not cursor.fetchone():
                # Create new link
                cursor.execute(
                    """
                    INSERT INTO GroceryItem (name, nutrition_id, ingredient_id, kroger_product)
                    SELECT ?, nf.nutrition_id, ?, ? FROM NutritionFact nf
                    WHERE nf.name = ?
                    """,
                    (ingredient.name, ingredient.ingredient_id,
                     kroger_product_id, ingredient.name),
                )
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
                "processed_at": datetime.now().isoformat(),
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

    def check_populated(self):
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            res = cursor.execute(
                """
                SELECT 1 FROM Ingredient;
                """
            )
            results = [dict(row) for row in res.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Database error fetching recipes: {e}")
            raise DatabaseError(f"Failed to fetch recipes: {str(e)}")

        pass

    def get_recipe_details_all(self) -> List[Dict]:
        """Get all recipes from database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            res = cursor.execute(
                """
                SELECT * FROM Recipe;
                """
            )
            results = [dict(row) for row in res.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Database error fetching recipes: {e}")
            raise DatabaseError(f"Failed to fetch recipes: {str(e)}")

    def get_recipe_cuisines(self) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            res = cursor.execute(
                """
                SELECT cuisine_type, Count(*) as count
                FROM Recipe
                GROUP BY cuisine_type;
                """
            )
            results = [dict(row) for row in res.fetchall()]
            print(results)
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Database error fetching recipes: {e}")
            raise DatabaseError(f"Failed to fetch recipes: {str(e)}")

    def get_recipe_details_recommended(self, user_id: int) -> List[Dict]:
        """Get all recipes from database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            res = cursor.execute(
                """
                SELECT * FROM Recipe
                WHERE NOT EXISTS (SELECT 1 FROM GroceryReceipt WHERE user_id = ?)
                ORDER BY RANDOM() LIMIT 5
                """, [user_id]
            )

            count = res.fetchone()

            if (count is None):
                res = cursor.execute(
                    """
                    SELECT r.*, gr.name as grocery_item FROM Recipe r
                    JOIN Ingredient i ON r.recipe_id = i.recipe_id
                    JOIN (SELECT * FROM GroceryReceipt ORDER BY add_date DESC) gr ON i.name LIKE gr.name
                    WHERE gr.user_id = ?
                    LIMIT 5
                    """,
                    [user_id]
                )

            results = [dict(row) for row in res.fetchall()]
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
            cursor.execute(
                """
                SELECT recipe_id, name, category, cuisine_type, cooking_time, difficulty_level
                FROM Recipe
                WHERE recipe_id = ?
                """,
                (recipe_id),
            )
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
            cursor.execute(
                """
                SELECT i.*, nf.calories, nf.fat, nf.protein, nf.carbs
                FROM Ingredient i
                JOIN GroceryItem g ON g.ingredient_id = i.ingredient_id
                JOIN NutritionFact nf ON nf.nutrition_id = g.nutrition_id
                WHERE i.recipe_id = ?;
                """,
                (recipe_id,),
            )
            results = cursor.fetchall()
            conn.close()
            return [
                IngredientDetail(
                    ingredient_id=row["ingredient_id"],
                    name=row["name"],
                    quantity=row["quantity"],
                    measurement_unit=row["measurement_unit"],
                    recipe_id=row["recipe_id"],
                    calories=row["calories"],
                    fat=row["fat"],
                    carbs=row["carbs"],
                    protein=row["protein"],
                )
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(
                f"Database error fetching ingredients for recipe {recipe_id}: {e}"
            )
            raise DatabaseError(f"Failed to fetch ingredients: {str(e)}")

    def get_shopping_list_user(self, user_id: int):
        """Get shopping list for a recipe with user"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    i.name as ingredient_name,
                    i.quantity,
                    i.measurement_unit,
                    kp.name as product_name,
                    kp.brand,
                    kp.price,
                    kp.category
                FROM ShoppingList li
                JOIN GroceryItem gi ON li.grocery_id = gi.item_id
                JOIN Ingredient i ON i.ingredient_id = gi.ingredient_id
                JOIN KrogerProduct kp ON kp.product_id = gi.kroger_product
                WHERE li.user_id = ?;
                """,
                [user_id],
            )
            results = cursor.fetchall()
            conn.close()
            return [
                ShoppingListItem(
                    ingredient_name=row["ingredient_name"],
                    quantity=row["quantity"],
                    measurement_unit=row["measurement_unit"],
                    product_name=row["product_name"],
                    brand=row["brand"],
                    price=row["price"],
                    category=row["category"],
                )
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(
                f"Database error fetching shopping list for user {user_id}: {e}"
            )
            raise DatabaseError(f"Failed to fetch shopping list: {str(e)}")

    def get_shopping_list(self, recipe_id: int) -> List[ShoppingListItem]:
        """Get shopping list for a recipe"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
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
                """,
                (recipe_id,),
            )
            results = cursor.fetchall()
            conn.close()
            return [
                ShoppingListItem(
                    ingredient_name=row["ingredient_name"],
                    quantity=row["quantity"],
                    measurement_unit=row["measurement_unit"],
                    product_name=row["product_name"],
                    brand=row["brand"],
                    price=row["price"],
                    category=row["category"],
                )
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(
                f"Database error fetching shopping list for recipe {recipe_id}: {e}"
            )
            raise DatabaseError(f"Failed to fetch shopping list: {str(e)}")

    def add_recipe_detail(self, recipe: RecipeDetail):
        """Add recipe to database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Recipe
                (name, category, cuisine_type, cooking_time, difficulty_level)
                VALUES (?, ?, ?, ?, ?)
                """,
                [recipe.name, recipe.category, recipe.cuisine_type,
                 recipe.cooking_time, recipe.difficulty_level]
            )
            conn.commit()
            conn.close()
            recipe_id = cursor.lastrowid
            self._add_ingredient_detail(recipe.ingredients, recipe_id)

            return recipe_id
        except sqlite3.Error as e:
            logger.error(f"Database error adding recipe {recipe.name}: {e}")
            raise DatabaseError(f"Failed to fetch recipe: {str(e)}")

    def _add_ingredient_detail(self, ingredients: List[IngredientPartial], recipe_id: int):
        """Add recipe to database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            for ingredient in ingredients:
                cursor.execute(
                    """
                    INSERT INTO Ingredient
                    (name, quantity, measurement_unit, recipe_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    [ingredient.name, ingredient.quantity,
                     ingredient.measurement_unit, recipe_id]
                )
                conn.commit()
            conn.close()
            for ingredient in ingredients:
                product = self.find_kroger_product(ingredient.name)
                self.save_kroger_product(product)
            logger.info(f"Added {ingredient.name}")
        except sqlite3.Error as e:
            logger.error(f"Database error adding recipe {ingredient.name}: {e}")
            raise DatabaseError(f"Failed to fetch recipe: {str(e)}")

    def add_shopping_list(self, recipe_id: int, user_id: int):
        """Add grocery items list to database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            id = shortuuid.ShortUUID().random(length=32)
            cursor.execute(
                """
                INSERT INTO ShoppingList (list_id, user_id, grocery_id, created_date)
                SELECT ?, ?, gi.ingredient_id, date('now') FROM GroceryItem gi
                JOIN Ingredient i ON gi.ingredient_id = i.ingredient_id
                WHERE i.recipe_id = ?;
                """,
                [id, user_id, recipe_id]
            )
            conn.commit()
            conn.close()
            list_id = cursor.lastrowid
            return list_id
        except sqlite3.Error as e:
            logger.error(f"Database error adding to list {user_id}: {e}")
            raise DatabaseError(f"Failed to fetch recipe: {str(e)}")

    def delete_shopping_list(self, user_id: int):
        """Delete grocery items"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM ShoppingList WHERE user_id = ?
                """,
                [user_id]
            )
            conn.commit()
            conn.close()
            list_id = cursor.lastrowid
            return list_id
        except sqlite3.Error as e:
            logger.error(f"Database error deleting to list {user_id}: {e}")
            raise DatabaseError(f"Failed to fetch recipe: {str(e)}")
