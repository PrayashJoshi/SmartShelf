from dataclasses import dataclass
import requests
import os


@dataclass
class FactDetail:
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float

    @classmethod
    def populate_food(cls, name, food_nutrients):
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

    @staticmethod
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
            return FactDetail.populate_food(food["description"], nutrients)
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
            return FactDetail.populate_food(food["description"], nutrients)
