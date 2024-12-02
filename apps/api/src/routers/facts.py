from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pipelines.nutrition_pipeline import NutritionPipeline
from typing import List
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)

router = APIRouter(tags=["nutrition facts"], prefix="/api/v1/facts")


@router.get("/{name}")
def get_fact(name: str):
    try:
        pipeline = NutritionPipeline()
        return pipeline.find_info(name)
    except Exception as e:
        logging.error(f"uhoh {e}")
