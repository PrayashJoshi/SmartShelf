# src/routes/recipe_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging
from pipelines.ingredient_pipeline import IngredientPipeline
from pipelines.kroger_api_utils import KrogerAPI
import os

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])
logger = logging.getLogger(__name__)


class Recipe(BaseModel):
    recipe_id: int
    name: str
    category: Optional[str]
    cuisine_type: Optional[str]
    cooking_time: Optional[int]
    difficulty_level: Optional[str]


class Ingredient(BaseModel):
    ingredient_id: int
    name: str
    quantity: float
    measurement_unit: str
    recipe_id: int


class ShoppingListItem(BaseModel):
    ingredient_name: str
    quantity: float
    measurement_unit: str
    product_name: str
    brand: str
    price: float
    category: str
    store_location: Optional[str]


# Dependency for IngredientPipeline
def get_ingredient_pipeline():
    client_id = os.getenv("KROGER_CLIENT_ID")
    client_secret = os.getenv("KROGER_CLIENT_SECRET")
    location_id = os.getenv("KROGER_LOCATION_ID", "70100465")

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Missing Kroger API credentials")

    return IngredientPipeline(
        client_id=client_id, client_secret=client_secret, location_id=location_id
    )


@router.get("/", response_model=List[Recipe])
async def get_all_recipes():
    """Get all available recipes"""
    try:
        pipeline = get_ingredient_pipeline()
        return pipeline.get_recipe_details_all()
    except Exception as e:
        logger.error(f"Error fetching recipes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching recipes")


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """Get details for a specific recipe"""
    try:
        pipeline = get_ingredient_pipeline()
        recipe = pipeline.get_recipe_details(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching recipe")


@router.get("/{recipe_id}/ingredients", response_model=List[Ingredient])
async def get_recipe_ingredients(recipe_id: int):
    """Get ingredients for a specific recipe"""
    try:
        pipeline = get_ingredient_pipeline()
        ingredients = pipeline.get_recipe_ingredients(recipe_id)
        return [vars(ingredient) for ingredient in ingredients]
    except Exception as e:
        logger.error(f"Error fetching ingredients for recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching ingredients")


@router.get("/{recipe_id}/shopping-list", response_model=List[ShoppingListItem])
async def get_shopping_list(recipe_id: int):
    """Get shopping list for a specific recipe"""
    try:
        pipeline = get_ingredient_pipeline()
        shopping_list = pipeline.get_shopping_list(recipe_id)
        return [vars(item) for item in shopping_list]
    except Exception as e:
        logger.error(f"Error generating shopping list for recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating shopping list")


@router.get("/cuisine/{cuisine_type}", response_model=List[Recipe])
async def get_recipes_by_cuisine(cuisine_type: str):
    """Get recipes filtered by cuisine type"""
    try:
        pipeline = get_ingredient_pipeline()
        recipes = [
            recipe
            for recipe in pipeline.get_recipe_details_all()
            if recipe["cuisine_type"].lower() == cuisine_type.lower()
        ]
        return recipes
    except Exception as e:
        logger.error(f"Error fetching recipes for cuisine {cuisine_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching recipes by cuisine")
