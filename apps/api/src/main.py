# main.py
import sqlite3
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime 
from populate import populate 
import logging
import shortuuid

logger = logging.getLogger('')
logging.basicConfig(format='%(levelname)s:\t  %(message)s',level=logging.DEBUG)

app = FastAPI()

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
# @app.on_event("startup")
# def init_db():
#     populate()


@app.get('/recipes/')
def get_all_recipes():
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM Recipe")
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result

@app.get('/cuisine')
def get_cuisine_type(q: Union[str, None] = None):
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute(f'SELECT * FROM Recipe WHERE cuisine_type=\'{q}\'')
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result

@app.get('/recipes/{recipe_name}/ingredients')
def get_cuisine_type(recipe_name: str):
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute(f'''
                         SELECT Ingredient.* 
                         FROM Recipe, Ingredient 
                         WHERE Recipe.name=\'{recipe_name}\' AND Recipe.recipe_id = Ingredient.recipe_id
                         ''')
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result

'''
HTTPS requests pertaining to Users
'''

@app.get('/monthly_signups')
def get_users():
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute(f'''
                         SELECT strftime('%m, %Y', reg_date) AS signup_date, strftime('%Y', reg_date) AS year, Count(*) as signups 
                         FROM User GROUP BY signup_date ORDER BY year;
                         ''')

    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result

class User(BaseModel):
    name: str
    email: str 
    address: str
    date: str = datetime.now().strftime('%Y-%m-%d')

@app.post('/users/add_user/')
def add_user(user: User) -> str | dict:
    logger.info(f'Adding new user {user.name}')
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()

        cursor.execute(f'''
                        INSERT INTO User (name, email, address, reg_date) 
                        VALUES ('{user.name}', '{user.email}', '{user.address}', '{user.date}');
                        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f'Cannot add new user {e}')
        raise e
    return 'ok'

@app.get('/users/verify')
def verify_user(email: str):
    logger.info(f'Verifying email {email}')
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()

        res = cursor.execute(f'''
                        SELECT user_id, name, email from User WHERE email = '{email}';
                        ''')
        
        user = res.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        column_names = [description[0] for description in cursor.description]
        result = dict(zip(column_names, user))
        conn.close()

        return result

    except Exception as e:
        logger.error(f'Cannot verify user {e}')
        raise e

@app.post('/check_kroger')
def kroger_product():
    # TODO: call api
    pass

class ReceiptItem(BaseModel):
    name: str
    price: float
class Receipt(BaseModel):
    ingredients: List[ReceiptItem]
    date: str = datetime.now().strftime('%Y-%m-%d')

@app.post('/receipts/add_receipt')
def add_receipt(receipt: Receipt):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        id = shortuuid.ShortUUID().random(length=32)
        for item in receipt:
            cursor.execute(f'''
                           INSERT INTO Receipt(receipt_id, name, price) 
                           VALUES ('{id}', '{item.name}', '{item.price}');
                           ''')
            conn.commit()

        conn.close()
        return 'ok'
    except: 
        print("uhoh")
