from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from pipelines.receipt_pipeline import ReceiptPipeline
from typing import List
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)

router = APIRouter(tags=["receipts"], prefix="/api/v1/receipts")


class ReceiptItem(BaseModel):
    name: str
    price: float


class Receipt(BaseModel):
    ingredients: List[ReceiptItem]
    date: str = datetime.now().strftime("%Y-%m-%d")
    user_id: int


@router.post("/add_receipt")
async def add_receipt(receipt: Receipt):
    try:
        pipeline = ReceiptPipeline()
        return pipeline.add_new_receipt(receipt)
    except Exception as e:
        logger.error(f"Error calling method {e}")


@router.get("/receipt_history")
async def get_receipt_history(user_id: int):
    try:
        pipeline = ReceiptPipeline()
        return pipeline.get_reciept_history(user_id)
    except Exception as e:
        logger.error(f"Error calling method {e}")


@router.get("/price_history")
def get_price_history(year: int, user_id: int):
    try:
        pipeline = ReceiptPipeline()
        return pipeline.get_price_history(year, user_id)
    except Exception as e:
        logger.error(f"Error calling method {e}")


@router.get("/receipt")
def get_receipt_for_user(user_id: int, receipt_id: str):
    try:
        pipeline = ReceiptPipeline()
        return pipeline.get_receipt_for_user(user_id, receipt_id)
    except Exception as e:
        logger.error(f"Error calling method {e}")
