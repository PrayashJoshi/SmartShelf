# main.py
import sqlite3
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime
from populate import Populate
import logging
import shortuuid
from dotenv import load_dotenv

from routers import users, recipes, receipts

logger = logging.getLogger('')
logging.basicConfig(format='%(levelname)s:\t  %(message)s',
                    level=logging.DEBUG)

app = FastAPI()
app.include_router(router=users.router)
app.include_router(router=receipts.router)
app.include_router(router=recipes.router)

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function to initialize the SQLite database and create tables


@app.on_event("startup")
def init_db():
    load_dotenv()
    Populate()
