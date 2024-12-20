from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from pipelines.user_pipeline import UserPipeline
from typing import List
import logging

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)

router = APIRouter(tags=["users"], prefix="/api/v1/users")


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
def get_users():
    try:
        pipeline = UserPipeline()
        return pipeline.get_monthly_signups()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error fetching monthly signups")


@router.get("/minmax")
def get_minmax():
    try:
        pipeline = UserPipeline()
        return pipeline.get_max_and_min()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error fetching monthly signups")


@router.post("/op_user/")
def op_user(email: str) -> str | dict:
    try:
        pipeline = UserPipeline()
        return pipeline.op_user(email)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not op user")


@router.post("/add_user/")
def add_user(user: User) -> str | dict:
    try:
        pipeline = UserPipeline()
        return pipeline.get_monthly_signups()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not add new user")


@router.get("/verify")
def verify_user(email: str, password: str):
    try:
        pipeline = UserPipeline()
        return pipeline.verify_credentials(email, password)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not verify")


@router.put("/update")
def update_user(id: int, user: User):
    try:
        pipeline = UserPipeline()
        return pipeline.update_credentials(id, user)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error could not update user")
