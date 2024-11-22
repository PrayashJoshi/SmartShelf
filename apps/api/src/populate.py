from typing import List
import requests
import sqlite3
import csv
import os
from dotenv import load_dotenv
from enum import Enum
import ast
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)


def category_helper(row: List[str]) -> str:
    if row.find("main-dish") > 0:
        return "Main"
    elif row.find("side-dishes") > 0:
        return "Side"
    elif row.find("desserts") > 0:
        return "Dessert"
    elif row.find("appetizers") > 0:
        return "Appetizer"
    elif row.find("beverages") > 0:
        return "Beverage"
    else:
        return "Etc"


def nutrient_info_helper(nutrients):
    fact_info = {"calories": 0, "carbs": 0, "fat": 0, "protein": 0}
    for nutrient in nutrients:
        if nutrient["nutrientId"] == 1003:
            fact_info["protein"] = nutrient["value"]
        if nutrient["nutrientId"] == 1004:
            fact_info["fat"] = nutrient["value"]
        if nutrient["nutrientId"] == 1005:
            fact_info["carbs"] = nutrient["value"]
        if nutrient["nutrientId"] == 1008:
            fact_info["calories"] = nutrient["value"]

    return fact_info


def generate_schemas(cursor, conn):
    cursor.executescript(
        """
      CREATE TABLE IF NOT EXISTS User (
          user_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT UNIQUE,
          password TEXT,
          reg_date DATE
      );
      CREATE TABLE IF NOT EXISTS Recipe (
          recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          category TEXT,
          cooking_time INTEGER,
          url TEXT
      );
      CREATE TABLE IF NOT EXISTS NutritionFact (
          nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          calories REAL,
          fat REAL,
          carbs REAL,
          protein REAL
      );
      CREATE TABLE IF NOT EXISTS Ingredient (
          ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          recipe_id INTEGER,
          nutrition_id INTEGER,
          FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
          FOREIGN KEY (nutrition_id) REFERENCES NutritionFact(nutrition_id)
      );
      CREATE TABLE IF NOT EXISTS GroceryItem (
          grocery_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS Receipt (
          receipt_id TEXT,
          name TEXT NOT NULL,
          price FLOAT NOT NULL,
          add_date DATE NOT NULL,
          user_id INTEGER NOT NULL,
          FOREIGN KEY (user_id) REFERENCES User(user_id)
      );
      """
    )
    conn.commit()


def populate_users(cursor, conn):
    res = cursor.execute("SELECT COUNT(*) from User")
    count = res.fetchone()
    if count[0] == 0:
        try:
            cursor.executescript(
                """
              INSERT INTO User (name, email, password, reg_date) VALUES
                ('Alice Johnson', 'alice.johnson@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '2024-05-14'),
                ('Bob Smith', 'bob.smith@example.com', '84b43eab377df65e0f868d1eda345794d09faeb6cf5ddaa70fb2257a29ef2e85', '2024-03-10'),
                ('Charlie Brown', 'charlie.brown@example.com', '6cf2cedd09facbb89bbd79ff4e03f681dc35c0cc2b2f57fb3d870c33e4bdde1c', '2024-07-19'),
                ('Diana Prince', 'diana.prince@example.com', '7ae09cbe43b292651c7568ae36cdfbd75bda40ae103c66c1719dcd9aa9a9f231', '2024-06-21'),
                ('Ethan Hunt', 'ethan.hunt@example.com', '7d73efb21e0eaa0bfee5cb18e78cb5166909a7052eb553e31b57fac3ca99cc64', '2024-02-14'),
                ('Fiona Davis', 'fiona.davis@example.com', '5efc2b017da4f7736d192a74dde5891369e0685d4d38f2a455b6fcdab282df9c', '2024-08-01'),
                ('George Wilson', 'george.wilson@example.com', '67bfc0a321f2c11d9d53588f711d2191c4ab8d958a96761ced9b182934c16c01', '2024-03-15'),
                ('Hannah Adams', 'hannah.adams@example.com', 'e88f0ec6b2306d325c472415474d7b3739bc05335935be73f13eead95acb2ce4', '2023-04-10'),
                ('Ivan Rogers', 'ivan.rogers@example.com', '82215519e16be17d346d0a0aa5af0442921eceaf9c7f779dbea1304078243ec1', '2022-12-12'),
                ('Julia Bennett', 'julia.bennett@example.com', 'b91b4bd1dc21a6473bb0276813e861cb63b01f296b3c23a1cf7bc7f8a9b58dd1', '2023-01-17'),
                ('Kyle Matthews', 'kyle.matthews@example.com', '8cbb563d49f981f116e6661c9d7e6af39ff6dc37ce38033f4ceab1d19345e363', '2023-02-20'),
                ('Liam Carter', 'liam.carter@example.com', 'edba9579414b7f7a10746eb7b97206154f49498ffa2661f3aa477c6be87ded90', '2023-03-11'),
                ('Mia Torres', 'mia.torres@example.com', 'b21ccd8f4655dcbfcf9d5a717f2fdb708518fd3fdfc5d1154a74eb9ac1f0c101', '2023-05-06'),
                ('Noah Foster', 'noah.foster@example.com', '0b871f09788f36b4e5a9d5799f79d2c7e1f52cd1cee08948c47a5c2991f88032', '2022-11-30'),
                ('Olivia Brooks', 'olivia.brooks@example.com', '874b5888cec4da04c1446b7d351289cbc955fc7d53705da05ace20056f8148e0', '2023-06-01'),
                ('Paul Harris', 'paul.harris@example.com', '8bec0e352d22c650ca244b89bc28e3cfbc53108982dd1b933fc2220198a284a8', '2023-04-22'),
                ('Quinn Scott', 'quinn.scott@example.com', '585401ef6520106dd71691245290e4f33cc55d8462f14fe10195c957e9ee539c', '2023-01-09'),
                ('Rachel Turner', 'rachel.turner@example.com', '2634a4bc3fc88bb4e35a6b5301e147ebd3db36703a36b8447961f2cd73ba1696', '2023-07-15'),
                ('Sam Mitchell', 'sam.mitchell@example.com', 'a60144ddbc5ca2e4b9817ac9015f8d96b47953bc21fd8bb934e80747f929e729', '2023-03-08'),
                ('Tina Evans', 'tina.evans@example.com', 'dad5e49ba9e319e78f5a2b920c0a4119465bf6e50b0d5a9a86bfe273d3093cbf', '2022-12-24'),
                ('Uma Carter', 'uma.carter@example.com', '50e1e6d07f9c500293e039216032579c05cee83be247a4bdd8f3dc4135288cdb', '2023-05-05'),
                ('Victor Gray', 'victor.gray@example.com', 'be0c4bb63e52a5c384cbf1c5d44fa4b819fc09ca293a0e015f1e3096c1954b5f', '2023-02-12'),
                ('Wendy Reed', 'wendy.reed@example.com', '5f16a90263b5c61429bd142449e3250f8a7b6aacff9705295668ff6bcef9fd05', '2023-06-29'),
                ('Xander Phillips', 'xander.phillips@example.com', '04079218e68b0421ee2b12160d7b943ff6567c2f0c33715184c8abf7057f30fc', '2023-04-18'),
                ('Yara Collins', 'yara.collins@example.com', '265696009a6c7ae10c6c1fcd34a48a0811606a5905d1328022e60af8e937b28c', '2023-01-23'),
                ('Zachary Murphy', 'zachary.murphy@example.com', '1456d50c977426220cc635aa6a8f841c75be3dbb050d88c53de443194f32c0d2', '2023-07-02'),
                ('Ava Sanders', 'ava.sanders@example.com', 'a52acef66239ef537d0af5368c065ff8732d33b3bee6d1e5d7a858a7cc965da2', '2023-03-27'),
                ('Ben Hall', 'ben.hall@example.com', 'e325c62a4ecb5a22d21aee4d544fd71401e45ff8e641d70bc5ce6c23df38ee32', '2023-02-03'),
                ('Chloe White', 'chloe.white@example.com', '9485f3e7988da1ed9264322d221e700a9633436114189ef227b309d2b26519ed', '2023-05-09'),
                ('Daniel King', 'daniel.king@example.com', 'be88c1dbebf01c7186531f18350b3465dd394fb9168b81f66d6ed3c8e8815acd','2023-04-15'); 
              """
            )
            conn.commit()
            logger.debug("User Table Population Complete")
        except Exception as e:
            print(e)
            logger.debug("SQL STATEMENT IN User FAILED TO EXECUTE")


def populate_food(cursor, conn):
    with open("src/foodRecipes3.csv", newline="") as csvfile:
        """
        0 - title
        2 - minutes
        5 - tag
        6 - nutrition
        10 - ingredients

        Labels:
          Main-Dish (main-dish)
          Side-Dish (side-dishes)
          Desserts
          Appetizers
          Beverages
          Etc
        """
        data = csv.reader(csvfile)
        next(data)

        row_id = 1
        nutrition_id = 1
        for row in data:
            category = category_helper(row[5])
            title = " ".join(row[0].split()).title()
            logger.debug(f"Inserting New Recipe: {title}")
            cursor.execute(
                "INSERT INTO Recipe (recipe_id, name, category, cooking_time, url) VALUES (?, ?, ?, ?, ?)",  # noqa: E501
                [
                    row_id,
                    title,
                    category,
                    row[2],
                    "-".join(row[0].split()) + f"-{row[1]}",
                ],
            )
            for ingredient in ast.literal_eval(row[10]):
                res = requests.post(
                    f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv('NUTRITION_KEY')}",  # noqa: E501
                    json={
                        "query": f"{ingredient}",
                        "dataType": ["Foundation"],
                    },
                )
                nutrition_info = res.json()
                title = ''

                if (len(nutrition_info["foods"]) > 0):
                    # search raw ingredients
                    food = nutrition_info["foods"][0]
                    nutrients = food["foodNutrients"]
                    info = nutrient_info_helper(nutrients)
                    print(food["description"], ingredient)
                    title = food["description"]
                    logger.info(f"Insert {title}: {info}")
                    cursor.execute(
                        "INSERT INTO NutritionFact (name, calories, fat, carbs, protein) VALUES (?, ?, ?, ?, ?)",  # noqa: E501
                        [
                            title,
                            info["calories"],
                            info["fat"],
                            info["carbs"],
                            info["protein"],
                        ],
                    )
                else:
                    res = requests.post(
                        f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv('NUTRITION_KEY')}",  # noqa: E501
                        json={
                            "query": f"{ingredient}"
                        }
                    )
                    nutrition_info = res.json()
                    food = nutrition_info["foods"][0]
                    nutrients = food["foodNutrients"]
                    info = nutrient_info_helper(nutrients)
                    print(food["description"], ingredient)
                    title = food["description"]
                    logger.info(f"Insert {title}: {info}")
                    cursor.execute(
                        "INSERT INTO NutritionFact (name, calories, fat, carbs, protein) VALUES (?, ?, ?, ?, ?)",  # noqa: E501
                        [
                            title,
                            info["calories"],
                            info["fat"],
                            info["carbs"],
                            info["protein"],
                        ],
                    )

                cursor.execute(
                    "INSERT INTO Ingredient (name, recipe_id, nutrition_id) VALUES (?, ?, ?)",  # noqa: E501
                    [title, row_id, nutrition_id],
                )
                nutrition_id += 1
            row_id += 1
            conn.commit()
        logger.debug("Food Related Tables Populated")


def populate():
    load_dotenv()

    """
    Populate Data To Database

    Data found in foodRecipes.csv pulled from Food.com
    """
    logger.info("Initializing Database")
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()
    generate_schemas(cursor, conn)
    cursor.execute("DELETE FROM Recipe;")
    cursor.execute("DELETE FROM NutritionFact;")
    cursor.execute("DELETE FROM Ingredient;")

    logger.info("Attempting To Populate User Table")
    populate_users(cursor, conn)

    logger.info(
        "Attempting to Populate Recipe, Ingredient, and Nutrition Facts"
    )
    populate_food(cursor, conn)

    conn.close()
