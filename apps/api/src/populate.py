import sqlite3
import csv
import logging
import os
from pipelines.nutrition_pipeline import NutritionPipeline
from pipelines.kroger_pipeline import KrogerPipeline, IngredientDetail

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)


"""
population order:
    users => recipes => ingredients => nutritionfact & krogerproduct
    => groceryitem

on insert order:
    groceryreceipt => shoppinglist => isowner

"""


class Populate:
    """Prepopulates the database with data"""

    def __init__(self):
        self.conn = sqlite3.connect("src/smartshelf.db")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        logger.info("Initializing Database")
        self.generate_schemas()
        logger.info("Beginning Population")
        self.populate()

    def __del__(self):
        self.conn.close()

    def generate_schemas(self):
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password TEXT,
                reg_date DATE,
                admin INTEGER
            );
            CREATE TABLE IF NOT EXISTS Recipe (
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                cuisine_type TEXT,
                cooking_time INTEGER,
                difficulty_level TEXT
            );
            CREATE TABLE IF NOT EXISTS NutritionFact (
                nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                guess TEXT,
                calories REAL,
                fat REAL,
                carbs REAL,
                protein REAL
            );
            CREATE TABLE IF NOT EXISTS KrogerProduct (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                brand TEXT,
                category TEXT
                );
            CREATE TABLE IF NOT EXISTS Ingredient (
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL,
                measurement_unit TEXT,
                recipe_id INTEGER,
                FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id)
            );
            CREATE TABLE IF NOT EXISTS GroceryItem (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                nutrition_id INTEGER,
                ingredient_id INTEGER,
                kroger_product INTEGER,
                FOREIGN KEY (nutrition_id) REFERENCES NutritionFact(nutrition_id),
                FOREIGN KEY (kroger_product) REFERENCES KrogerProduct(product_id),
                FOREIGN KEY (ingredient_id) REFERENCES Ingrediet(ingredient_id)
            );
            CREATE TABLE IF NOT EXISTS GroceryReceipt (
                receipt_id TEXT,
                name TEXT NOT NULL,
                price FLOAT NOT NULL,
                add_date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES User(user_id)
            );
            CREATE TABLE IF NOT EXISTS ShoppingList (
                list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_date DATE,
                status TEXT,
                total_amount REAL
            );
          """
        )
        self.conn.commit()

    def populate(self):
        """
        Populate Data To Database
        Data found in foodRecipes.csv pulled from Food.com
        """
        logger.info("Attempting To Populate Users")
        self.populate_users()
        logger.info("Attempting to Populate Recipes")
        self.populate_recipes()
        logger.info("Attempting to Populate Ingredients")
        self.populate_ingredients()
        logger.info("Attempting to Populate Nutrition Facts")
        self.populate_nutrition_facts()
        logger.info("Attempting to Populate Kroger Products + Grocery Items")
        self.populate_kroger()

    def populate_users(self):
        res = self.cursor.execute("SELECT COUNT(*) as num from User")
        count = res.fetchone()
        if count["num"] > 0:
            logger.info("Already populated")
            return
        try:
            self.cursor.executescript(
                """
              INSERT INTO User (name, email, password, reg_date, is_admin) VALUES
                ('Alice Johnson', 'alice.johnson@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '2024-05-14', 1),
                ('Bob Smith', 'bob.smith@example.com', '84b43eab377df65e0f868d1eda345794d09faeb6cf5ddaa70fb2257a29ef2e85', '2024-03-10', 0),
                ('Charlie Brown', 'charlie.brown@example.com', '6cf2cedd09facbb89bbd79ff4e03f681dc35c0cc2b2f57fb3d870c33e4bdde1c', '2024-07-19', 0),
                ('Diana Prince', 'diana.prince@example.com', '7ae09cbe43b292651c7568ae36cdfbd75bda40ae103c66c1719dcd9aa9a9f231', '2024-06-21', 0),
                ('Ethan Hunt', 'ethan.hunt@example.com', '7d73efb21e0eaa0bfee5cb18e78cb5166909a7052eb553e31b57fac3ca99cc64', '2024-02-14', 0),
                ('Fiona Davis', 'fiona.davis@example.com', '5efc2b017da4f7736d192a74dde5891369e0685d4d38f2a455b6fcdab282df9c', '2024-08-01', 0),
                ('George Wilson', 'george.wilson@example.com', '67bfc0a321f2c11d9d53588f711d2191c4ab8d958a96761ced9b182934c16c01', '2024-03-15', 0),
                ('Hannah Adams', 'hannah.adams@example.com', 'e88f0ec6b2306d325c472415474d7b3739bc05335935be73f13eead95acb2ce4', '2023-04-10', 0),
                ('Ivan Rogers', 'ivan.rogers@example.com', '82215519e16be17d346d0a0aa5af0442921eceaf9c7f779dbea1304078243ec1', '2022-12-12', 0),
                ('Julia Bennett', 'julia.bennett@example.com', 'b91b4bd1dc21a6473bb0276813e861cb63b01f296b3c23a1cf7bc7f8a9b58dd1', '2023-01-17', 0),
                ('Kyle Matthews', 'kyle.matthews@example.com', '8cbb563d49f981f116e6661c9d7e6af39ff6dc37ce38033f4ceab1d19345e363', '2023-02-20', 0),
                ('Liam Carter', 'liam.carter@example.com', 'edba9579414b7f7a10746eb7b97206154f49498ffa2661f3aa477c6be87ded90', '2023-03-11', 0),
                ('Mia Torres', 'mia.torres@example.com', 'b21ccd8f4655dcbfcf9d5a717f2fdb708518fd3fdfc5d1154a74eb9ac1f0c101', '2023-05-06', 0),
                ('Noah Foster', 'noah.foster@example.com', '0b871f09788f36b4e5a9d5799f79d2c7e1f52cd1cee08948c47a5c2991f88032', '2022-11-30', 0),
                ('Olivia Brooks', 'olivia.brooks@example.com', '874b5888cec4da04c1446b7d351289cbc955fc7d53705da05ace20056f8148e0', '2023-06-01', 0),
                ('Paul Harris', 'paul.harris@example.com', '8bec0e352d22c650ca244b89bc28e3cfbc53108982dd1b933fc2220198a284a8', '2023-04-22', 0),
                ('Quinn Scott', 'quinn.scott@example.com', '585401ef6520106dd71691245290e4f33cc55d8462f14fe10195c957e9ee539c', '2023-01-09', 0),
                ('Rachel Turner', 'rachel.turner@example.com', '2634a4bc3fc88bb4e35a6b5301e147ebd3db36703a36b8447961f2cd73ba1696', '2023-07-15', 0),
                ('Sam Mitchell', 'sam.mitchell@example.com', 'a60144ddbc5ca2e4b9817ac9015f8d96b47953bc21fd8bb934e80747f929e729', '2023-03-08', 0),
                ('Tina Evans', 'tina.evans@example.com', 'dad5e49ba9e319e78f5a2b920c0a4119465bf6e50b0d5a9a86bfe273d3093cbf', '2022-12-24', 0),
                ('Uma Carter', 'uma.carter@example.com', '50e1e6d07f9c500293e039216032579c05cee83be247a4bdd8f3dc4135288cdb', '2023-05-05', 0),
                ('Victor Gray', 'victor.gray@example.com', 'be0c4bb63e52a5c384cbf1c5d44fa4b819fc09ca293a0e015f1e3096c1954b5f', '2023-02-12', 0),
                ('Wendy Reed', 'wendy.reed@example.com', '5f16a90263b5c61429bd142449e3250f8a7b6aacff9705295668ff6bcef9fd05', '2023-06-29', 0),
                ('Xander Phillips', 'xander.phillips@example.com', '04079218e68b0421ee2b12160d7b943ff6567c2f0c33715184c8abf7057f30fc', '2023-04-18', 0),
                ('Yara Collins', 'yara.collins@example.com', '265696009a6c7ae10c6c1fcd34a48a0811606a5905d1328022e60af8e937b28c', '2023-01-23', 0),
                ('Zachary Murphy', 'zachary.murphy@example.com', '1456d50c977426220cc635aa6a8f841c75be3dbb050d88c53de443194f32c0d2', '2023-07-02', 0),
                ('Ava Sanders', 'ava.sanders@example.com', 'a52acef66239ef537d0af5368c065ff8732d33b3bee6d1e5d7a858a7cc965da2', '2023-03-27', 0),
                ('Ben Hall', 'ben.hall@example.com', 'e325c62a4ecb5a22d21aee4d544fd71401e45ff8e641d70bc5ce6c23df38ee32', '2023-02-03', 0),
                ('Chloe White', 'chloe.white@example.com', '9485f3e7988da1ed9264322d221e700a9633436114189ef227b309d2b26519ed', '2023-05-09', 0),
                ('Daniel King', 'daniel.king@example.com', 'be88c1dbebf01c7186531f18350b3465dd394fb9168b81f66d6ed3c8e8815acd','2023-04-15', 0); 
                """
            )
            self.conn.commit()
            logger.debug("User Table Population Complete")
        except sqlite3.DatabaseError as e:
            logger.debug(f"SQL STATEMENT IN User FAILED TO EXECUTE: {e}")

    def populate_recipes(self):
        """
        populates prepared data for recipes
        """
        res = self.cursor.execute("SELECT COUNT(*) as num from Recipe")
        count = res.fetchone()
        if count["num"] > 0:
            logger.info("Already populated")
            return
        try:
            self.cursor.execute(
                """
                INSERT INTO Recipe (name, category, cuisine_type, cooking_time,
                                    difficulty_level) VALUES
                ('Spaghetti Carbonara', 'Main Course', 'Italian', 20, 'Easy'),
                ('Beef Stroganoff', 'Main Course', 'Russian', 30, 'Medium'),
                ('Caesar Salad', 'Appetizer', 'American', 15, 'Easy'),
                ('Pancakes', 'Breakfast', 'American', 20, 'Easy'),
                ('Paella', 'Main Course', 'Spanish', 75, 'Hard'),
                ('Ratatouille', 'Main Course', 'French', 50, 'Medium'),
                ('Fish Tacos', 'Main Course', 'Mexican', 30, 'Easy'),
                ('Pad Thai', 'Main Course', 'Thai', 30, 'Medium'),
                ('Chocolate Cake', 'Dessert', 'French', 45, 'Medium'),
                ('Mochi', 'Dessert', 'Japanese', 4, 'Easy'),
                ('Sushi Rolls', 'Appetizer', 'Japanese', 15, 'Hard'),
                ('Chocolate Chip Cookies', 'Dessert', 'American', 30, 'Easy'),
                ('Falafel Wrap', 'Snack', 'Middle Eastern', 60, 'Easy'),
                ('Ramen', 'Soup', 'Japanese', 50, 'Medium'),
                ('Shepherd''s Pie', 'Main Dish', 'British', 70, 'Medium'),
                ('Margherita Pizza', 'Main Dish', 'Italian', 80, 'Easy'),
                ('Lasagna', 'Main Dish', 'Italian', 100, 'Medium'),
                ('Chicken Satay', 'Appetizer', 'Indonesian', 35, 'Medium'),
                ('Fried Rice', 'Side Dish', 'Chinese', 25, 'Easy'),
                ('Lo Mein', 'Side Dish', 'Chinese', 20, 'Easy'),
                ('Cheesecake', 'Dessert', 'American', 4235, 'Hard'),
                ('Shakshuka', 'Breakfast', 'Middle Eastern', 30, 'Easy'),
                ('Orange Chicken', 'Main Dish', 'American', 60, 'Medium'),
                ('Egg Drop Soup', 'Soup', 'Chinese', 15, 'Easy'),
                ('Broccoli Cheddar Soup', 'Soup', 'American', 35, 'Easy'),
                ('Black Bean Burger', 'Main Dish', 'American', 12, 'Medium'),
                ('Broccoli Frittata', 'Main Dish', 'American', 30, 'Easy'),
                ('Coconut Curry', 'Main Dish', 'Thai', 30, 'Easy'),
                ('Baklava', 'Dessert', 'Middle Eastern', 135, 'Hard'),
                ('Chicken Noodle Soup', 'Soup', 'American', 40, 'Easy');
                """
            )
            self.conn.commit()
            logger.info("Recipe Table Populated")
        except sqlite3.DatabaseError as e:
            logger.debug(f"SQL STATEMENT IN User FAILED TO EXECUTE: {e}")

    def populate_ingredients(self):
        res = self.cursor.execute("SELECT COUNT(*) as num from Ingredient")
        count = res.fetchone()
        if count["num"] > 0:
            logger.info("Already populated")
            return
        try:
            with open("src/data/ingredients.csv", newline="") as csvfile:
                data = csv.reader(csvfile)
                next(data)
                for row in data:
                    self.cursor.execute(
                        """
                        INSERT INTO Ingredient (
                            name, quantity, measurement_unit, recipe_id
                        ) VALUES (?, ? ,?, ?);
                        """,
                        [row[1], row[2], row[3], row[4]],
                    )
            self.conn.commit()
            logger.info("Ingredient Table Populated")
        except sqlite3.DatabaseError as e:
            logger.debug(f"SQL STATEMENT IN User FAILED TO EXECUTE: {e}")

    def populate_nutrition_facts(self):
        res = self.cursor.execute("SELECT COUNT(*) as num from NutritionFact")
        count = res.fetchone()
        if count["num"] > 0:
            logger.info("Already populated")
            return
        try:
            res = self.cursor.execute("SELECT COUNT(*) as num from Ingredient")
            count = res.fetchone()
            if count["num"] == 0:
                raise Exception("Cannot find ingredient table")
            res = self.cursor.execute("SELECT name from Ingredient")
            pipeline = NutritionPipeline()
            for ingredient in res.fetchall():
                info = pipeline.call_api(ingredient["name"])
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO NutritionFact
                    (name, guess, calories, fat, carbs, protein)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        ingredient["name"],
                        info.name,
                        info.calories,
                        info.fat,
                        info.carbs,
                        info.protein,
                    ],
                )
                self.conn.commit()
            logger.info("Recipe Table Populated")
        except sqlite3.DatabaseError as e:
            logger.debug(f"SQL STATEMENT IN User FAILED TO EXECUTE: {e}")

    def populate_kroger(self):
        client_id = os.getenv("KROGER_CLIENT_ID")
        client_secret = os.getenv("KROGER_CLIENT_SECRET")
        location_id = os.getenv("KROGER_LOCATION_ID", "02900210")
        pipeline = KrogerPipeline(
            client_id=client_id,
            client_secret=client_secret,
            location_id=location_id
        )
        res = self.cursor.execute(
                "SELECT DISTINCT * from Ingredient WHERE name ='Cheddar Cheese';"
                )
        ingredient = res.fetchone()
        thing = IngredientDetail(ingredient["ingredient_id"],
                                 ingredient["name"],
                                 ingredient["quantity"],
                                 ingredient["measurement_unit"],
                                 ingredient["recipe_id"])
        print(thing)
        product = pipeline.find_kroger_product(thing)
        print(product)
