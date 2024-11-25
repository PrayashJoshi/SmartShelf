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

from routers import users, recipes, ingredients

logger = logging.getLogger('')
logging.basicConfig(format='%(levelname)s:\t  %(message)s',
                    level=logging.DEBUG)

app = FastAPI()
app.include_router(router=users.router)

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
    Populate()


@app.get('/recipes/')
def get_all_recipes():
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM Recipe")
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result


@app.get('/recipes/random')
def get_random_recipes():
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM Recipe ORDER BY RANDOM() LIMIT 5;")
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
def get_ingredients(recipe_name: str):
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    res = cursor.execute(f'''
                         SELECT Ingredient.*
                         FROM Recipe, Ingredient
                         WHERE Recipe.name=\'{recipe_name}\' AND
                         Recipe.recipe_id = Ingredient.recipe_id
                         ''')
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in res.fetchall()]
    conn.close()
    return result



@app.post('/check_kroger')
def kroger_product():
    # TODO: call api
    pass


'''
HTTPS requests pertaining to Receipts
'''


class ReceiptItem(BaseModel):
    name: str
    price: float


class Receipt(BaseModel):
    ingredients: List[ReceiptItem]
    date: str = datetime.now().strftime('%Y-%m-%d')
    user_id: int


@app.post('/receipts/add_receipt')
def add_receipt(receipt: Receipt):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        id = shortuuid.ShortUUID().random(length=32)
        for item in receipt.ingredients:
            print(item)
            cursor.execute(f'''
                           INSERT INTO Receipt(
                               receipt_id,
                               name,
                               price,
                               add_date,
                               user_id)
                           VALUES (
                               '{id}',
                               '{item.name}',
                               '{item.price}',
                               '{receipt.date}',
                               '{receipt.user_id}'
                               );
                           ''')

        conn.commit()
        conn.close()
        return 'ok'
    except Exception as e:
        print(e)
        return e


@app.get('/receipts/receipt_history')
def get_receipt_history(user_id: int):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        res = cursor.execute(f'''
                            SELECT receipt_id, add_date, COUNT(*) as items,
                             SUM(price) as total
                            FROM Receipt
                            WHERE Receipt.user_id == \'{user_id}\'
                            GROUP BY receipt_id
                            ORDER BY add_date DESC;
                            ''')

        column_names = [description[0] for description in cursor.description]
        result = [dict(zip(column_names, row)) for row in res.fetchall()]
        conn.close()
        return result
    except Exception as e:
        print(e)
        return e


@app.get('/receipts/price_history/{year}')
def get_price_history(year: int, user_id: int):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        res = cursor.execute(f'''
                            SELECT SUM(price) as total,
                             strftime('%m', add_date) AS month,
                             strftime('%Y', add_date) AS year
                            FROM Receipt
                            WHERE Receipt.user_id == \'{user_id}\'
                             AND year == \'{year}\'
                            GROUP BY month
                            ''')

        column_names = [description[0] for description in cursor.description]
        result = [dict(zip(column_names, row)) for row in res.fetchall()]
        conn.close()
        return result
    except Exception as e:
        print(e)
        return e


@app.get('/receipts/receipt/{receipt_id}')
def get_receipt_for_user(user_id: int, receipt_id: str):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        res = cursor.execute(f'''
                            SELECT name, price
                            FROM Receipt
                            WHERE user_id == \'{user_id}\'
                             AND receipt_id == \'{receipt_id}\';
                            ''')

        column_names = [description[0] for description in cursor.description]
        result = [dict(zip(column_names, row)) for row in res.fetchall()]
        conn.close()
        return result
    except Exception as e:
        print(e)
        return e


@app.get('/ingredients/{recipe_id}')
def get_ingredients_for_recipe(recipe_id: int):
    try:
        conn = sqlite3.connect("smartshelf.db")
        cursor = conn.cursor()
        res = cursor.execute(f'''
                            SELECT *
                            FROM Ingredient
                            WHERE recipe_id == \'{recipe_id}\';
                            ''')

        column_names = [description[0] for description in cursor.description]
        result = [dict(zip(column_names, row)) for row in res.fetchall()]
        conn.close()
        return result
    except Exception as e:
        print(e)
        return e
