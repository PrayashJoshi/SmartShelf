from dataclasses import dataclass
import requests
import os
import sqlite3
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)


@dataclass
class FactDetail:
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

    @classmethod
    def _return_api_response(cls, name, food_nutrients):
        found_protein = found_fat = found_carbs = found_calories = 0
        for nutrient in food_nutrients:
            if nutrient["nutrientId"] == 1003:
                found_protein = nutrient["value"]
            if nutrient["nutrientId"] == 1004:
                found_fat = nutrient["value"]
            if nutrient["nutrientId"] == 1005:
                found_carbs = nutrient["value"]
            if nutrient["nutrientId"] == 1008:
                found_calories = nutrient["value"]
        return cls(name=name, calories=found_calories, protein=found_protein,
                   fat=found_fat, carbs=found_carbs)


class NutritionPipeline:

    def __init__(self):
        self._db_path = "smartshelf.db"

    def call_api(ingredient: str):
        res = requests.post(
            f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv('NUTRITION_KEY')}",  # noqa: E501
            json={
                "query": f"{ingredient}",
                "dataType": ["Foundation"],
            },
        )
        nutrition_info = res.json()

        if len(nutrition_info["foods"]) > 0:
            # search raw ingredients
            food = nutrition_info["foods"][0]
            nutrients = food["foodNutrients"]
            return FactDetail._return_api_response(food["description"], nutrients)
        else:
            res = requests.post(
                f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv('NUTRITION_KEY')}",  # noqa: E501
                json={"query": f"{ingredient}"},
            )
            nutrition_info = res.json()
            if len(nutrition_info["foods"]) == 0:
                return FactDetail("Not Found", 0, 0, 0, 0)
            food = nutrition_info["foods"][0]
            nutrients = food["foodNutrients"]
            return FactDetail._return_api_response(food["description"], nutrients)

    def find_info(self, name: str):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            res = cursor.execute(
                """
                SELECT * FROM NutritionFact WHERE name = ?
                """,
                [name]
            )
            return res.fetchone()
        except sqlite3.DatabaseError as e:
            logger.error(f"Error finding nutrition fact {name}:{e}")
        finally:
            conn.close()

    def add_info(self, name: str):
        info = self.call_api(name)
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO NutritionFact
                (name, guess, calories, fat, carbs, protein)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    name,
                    info.name,
                    info.calories,
                    info.fat,
                    info.carbs,
                    info.protein,
                ],
            )
            conn.commit()
        except sqlite3.DatabaseError as e:
            logger.error(f"Error inserting nutrition fact {name}:{e}")
        finally:
            conn.close()
