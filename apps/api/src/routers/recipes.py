# src/routes/recipe_routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
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
    calories: float
    protein: float
    fat: float
    carbs: float


class ShoppingListItem(BaseModel):
    ingredient_name: str
    quantity: float
    measurement_unit: str
    product_name: str
    brand: str
    price: float
    category: str
    store_location: Optional[str]


class IdLookUps(BaseModel):
    user_id: int
    recipe_id: int


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


@router.get("/recommended/{user_id}", response_model=List[Recipe])
async def get_recipe_recommended(user_id: int):
    """Get ingredients for a specific recipe"""
    try:
        pipeline = get_ingredient_pipeline()
        return pipeline.get_recipe_details_recommended(user_id)
    except Exception as e:
        logger.error(f"Error fetching ingredients for recipe {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching ingredients")


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


@router.get("/{user_id}/shopping-list-user", response_model=List[ShoppingListItem])
async def get_shopping_list_user(user_id: int):
    """Get shopping list for a specific recipe"""
    try:
        pipeline = get_ingredient_pipeline()
        shopping_list = pipeline.get_shopping_list_user(user_id)
        return [vars(item) for item in shopping_list]
    except Exception as e:
        logger.error(f"Error generating shopping list for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating shopping list")


@router.get("/cuisines/", response_model=List[Dict])
async def get_recipes_by_cuisine():
    """Get recipes filtered by cuisine type"""
    try:
        pipeline = get_ingredient_pipeline()
        return pipeline.get_recipe_cuisines()
    except Exception as e:
        logger.error(f"Error fetching recipes for cuisines: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching recipes by cuisine")


@router.post("/add_list")
async def add_recipe_to_list(body: IdLookUps):
    try:
        pipeline = get_ingredient_pipeline()
        return pipeline.add_shopping_list(user_id=body.user_id, recipe_id=body.recipe_id)
    except Exception as e:
        logger.error(f"Error adding to ShoppingList: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding to ShoppingList")


@router.delete("/clear_list")
async def clear_list(body: IdLookUps):
    try:
        pipeline = get_ingredient_pipeline()
        return pipeline.delete_shopping_list(body.user_id)
    except Exception as e:
        logger.error(f"Error adding to ShoppingList: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting to ShoppingList")
