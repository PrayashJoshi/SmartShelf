from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from pipelines.user_pipeline import UserPipeline
from typing import List
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)

router = APIRouter()


class User(BaseModel):
    name: str
    email: str
    password: str
    date: str = datetime.now().strftime("%Y-%m-%d")


class MonthlyStat(BaseModel):
    signup_date: str
    year: str
    signups: int


@router.get("/monthly_signups", response_model=List[MonthlyStat])
async def get_monthly_users():
    try:
        pipeline = UserPipeline()
        return pipeline.get_monthly_signups()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error fetching monthly signups")


@router.post("/add_user")
async def add_user(user: User) -> str | dict:
    try:
        pipeline = UserPipeline()
        return pipeline.get_monthly_signups()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not add new user")


@router.get("/verify")
async def verify_user(email: str, password: str):
    try:
        pipeline = UserPipeline()
        return pipeline.verify_credentials(email, password)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not verify")


@router.put("/update")
async def update_user(id: int, user: User):
    try:
        pipeline = UserPipeline()
        return pipeline.update_credentials(id, user)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not update user")
