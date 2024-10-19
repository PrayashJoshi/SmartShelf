# main.py
import sqlite3
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
import random
import logging
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
@app.on_event("startup")
def init_db():
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    logger.info("Initializing Database")

    # Ttables as per the relational schema
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS User (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            address TEXT,
            reg_date DATE
        );

        CREATE TABLE IF NOT EXISTS Recipe (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            cuisine_type TEXT,
            cooking_time INTEGER,
            difficulty_level TEXT
        );

        CREATE TABLE IF NOT EXISTS Ingredient (
            ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL,
            measurement_unit TEXT,
            recipe_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id)
        );

        CREATE TABLE IF NOT EXISTS NutritionFact (
            nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
            calories REAL,
            fat REAL,
            carbs REAL,
            protein REAL
        );

        CREATE TABLE IF NOT EXISTS GroceryReceipt (
            receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            total_amount REAL,
            home_store INTEGER,
            grocery_item INTEGER,
            FOREIGN KEY (home_store) REFERENCES Store(store_id),
            FOREIGN KEY (grocery_item) REFERENCES GroceryItem(item_id)
        );

        CREATE TABLE IF NOT EXISTS Store (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_location TEXT
        );

        CREATE TABLE IF NOT EXISTS GroceryItem (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nutrition_id INTEGER,
            ingredient_id INTEGER,
            kroger_product INTEGER,
            FOREIGN KEY (nutrition_id) REFERENCES NutritionFact(nutrition_id),
            FOREIGN KEY (kroger_product) REFERENCES KrogerProduct(product_id),
            FOREIGN KEY (ingredient_id) REFERENCES Ingrediet(ingredient_id)
        );

        CREATE TABLE IF NOT EXISTS KrogerProduct (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            brand TEXT,
            category TEXT
        );

        CREATE TABLE IF NOT EXISTS ShoppingList (
            list_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_date DATE,
            status TEXT,
            total_amount REAL
        );

        CREATE TABLE IF NOT EXISTS User_Is_Owner (
            receipt_id INTEGER,
            user_id INTEGER,
            list_id INTEGER,
            FOREIGN KEY (receipt_id) REFERENCES GroceryReceipt(receipt_id),
            FOREIGN KEY (user_id) REFERENCES User(user_id),
            FOREIGN KEY (list_id) REFERENCES ShoppingList(list_id)
        );

        CREATE TABLE IF NOT EXISTS Recommendation (
            user_id INTEGER,
            recipe_id INTEGER,
            preferences TEXT,
            FOREIGN KEY (user_id) REFERENCES User(user_id),
            FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id)
        );

        CREATE TABLE IF NOT EXISTS GroceryItem_ContainedIn (
            shopping_list_id INTEGER,
            receipt_id INTEGER,
            grocery_item_id INTEGER,
            FOREIGN KEY (shopping_list_id) REFERENCES ShoppingList(list_id),
            FOREIGN KEY (receipt_id) REFERENCES GroceryReceipt(receipt_id),
            FOREIGN KEY (grocery_item_id) REFERENCES GroceryItem(item_id)
        );
    ''')

    logger.info('Database Intialization Complete')

    res = cursor.execute('SELECT COUNT(*) FROM User')
    count = res.fetchone()

    logger.info('Attempting To Populate User Table')
    if (count[0] == 0):
        try:
            cursor.execute('''
                INSERT INTO User (name, email, address, reg_date) VALUES
                    ('Alice Smith', 'alice.smith@example.com', '123 Maple St, Springfield', '2023-01-15'),
                    ('Bob Johnson', 'bob.johnson@example.com', '456 Oak Ave, Springfield', '2023-02-12'),
                    ('Charlie Davis', 'charlie.davis@example.com', '789 Pine Rd, Springfield', '2023-03-08'),
                    ('Diana Moore', 'diana.moore@example.com', '234 Birch Ln, Springfield', '2023-04-02'),
                    ('Edward Lee', 'edward.lee@example.com', '567 Cedar Ct, Springfield', '2023-05-27'),
                    ('Fiona Clark', 'fiona.clark@example.com', '890 Elm St, Springfield', '2023-06-13'),
                    ('George Wright', 'george.wright@example.com', '123 Maple St, Springfield', '2023-07-05'),
                    ('Hannah Adams', 'hannah.adams@example.com', '456 Oak Ave, Springfield', '2023-07-22'),
                    ('Ian Roberts', 'ian.roberts@example.com', '789 Pine Rd, Springfield', '2023-08-10'),
                    ('Julia Thompson', 'julia.thompson@example.com', '234 Birch Ln, Springfield', '2023-09-15'),
                    ('Kevin Baker', 'kevin.baker@example.com', '567 Cedar Ct, Springfield', '2023-10-01'),
                    ('Laura Lewis', 'laura.lewis@example.com', '890 Elm St, Springfield', '2023-10-18'),
                    ('Michael Walker', 'michael.walker@example.com', '123 Maple St, Springfield', '2023-11-03'),
                    ('Natalie Perez', 'natalie.perez@example.com', '456 Oak Ave, Springfield', '2023-12-01'),
                    ('Oliver Turner', 'oliver.turner@example.com', '789 Pine Rd, Springfield', '2024-01-14'),
                    ('Paul Green', 'paul.green@example.com', '234 Birch Ln, Springfield', '2024-02-09'),
                    ('Quinn Hall', 'quinn.hall@example.com', '567 Cedar Ct, Springfield', '2024-03-04'),
                    ('Rachel Young', 'rachel.young@example.com', '890 Elm St, Springfield', '2024-04-12'),
                    ('Sam Harris', 'sam.harris@example.com', '123 Maple St, Springfield', '2024-05-07'),
                    ('Tina Scott', 'tina.scott@example.com', '456 Oak Ave, Springfield', '2024-06-18'),
                    ('Uma Kelly', 'uma.kelly@example.com', '789 Pine Rd, Springfield', '2024-07-03'),
                    ('Victor Diaz', 'victor.diaz@example.com', '234 Birch Ln, Springfield', '2024-08-25'),
                    ('Wendy King', 'wendy.king@example.com', '567 Cedar Ct, Springfield', '2024-09-13'),
                    ('Xander White', 'xander.white@example.com', '890 Elm St, Springfield', '2024-10-02'),
                    ('Yara Martinez', 'yara.martinez@example.com', '123 Maple St, Springfield', '2024-11-17'),
                    ('Zachary Phillips', 'zachary.phillips@example.com', '456 Oak Ave, Springfield', '2024-12-05'),
                    ('Angela Bennett', 'angela.bennett@example.com', '789 Pine Rd, Springfield', '2023-07-21'),
                    ('Brandon Collins', 'brandon.collins@example.com', '234 Birch Ln, Springfield', '2023-08-05'),
                    ('Claire Foster', 'claire.foster@example.com', '567 Cedar Ct, Springfield', '2023-09-10'),
                    ('David Rogers', 'david.rogers@example.com', '890 Elm St, Springfield', '2023-10-30');
            ''')

            logger.debug('User Table Population Complete')
        except:
            logger.error('SQL STATEMENT IN User FAILED TO EXECUTE')
    else:
        logger.info('User Table Already Populated')
    
    res = cursor.execute('SELECT COUNT(*) FROM Recipe')
    count = res.fetchone()

    logger.info('Attempting To Populate Recipe Table')

    '''
        Recipe List:
        https://damndelicious.net/2014/03/29/spaghetti-carbonara/
        https://www.recipetineats.com/beef-stroganoff/#wprm-recipe-container-27097
        https://www.loveandlemons.com/caesar-salad/
        https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/
        https://tastesbetterfromscratch.com/paella/
        https://www.loveandlemons.com/ratatouille-recipe/
    '''

    if (count[0] == 0):
        try:
            cursor.execute('''
            INSERT INTO Recipe (name, category, cuisine_type, cooking_time, difficulty_level) VALUES
                    ('Spaghetti Carbonara', 'Main Course', 'Italian', 20, 'Easy'),
                    ('Beef Stroganoff', 'Main Course', 'Russian', 30, 'Medium'),
                    ('Caesar Salad', 'Appetizer', 'American', 15, 'Easy'),
                    ('Pancakes', 'Breakfast', 'American', 20, 'Easy'),
                    ('Paella', 'Main Course', 'Spanish', 75, 'Hard'),
                    ('Ratatouille', 'Main Course', 'French', 50, 'Medium'),
                    ('Fish Tacos', 'Main Course', 'Mexican', 30, 'Easy'),
                    ('Pad Thai', 'Main Course', 'Thai', 35, 'Medium'),
                    ('Chocolate Cake', 'Dessert', 'French', 70, 'Medium'),
                    ('Mochi', 'Dessert', 'Japanese', 4, 'Easy');
            ''')
            logger.info('Recipe Table Populated')
        except:
            logger.error('SQL STATEMENT IN Recipe FAILED TO EXECUTE')
    else:
        logger.info('Recipe Table Already Populated')
    
    res = cursor.execute('SELECT COUNT(*) FROM Ingredient')
    count = res.fetchone()

    logger.info('Attempting To Populate Ingredient Table')
    if (count[0] == 0):
        try:
            cursor.execute('''
                INSERT INTO Ingredient (name, quantity, measurement_unit, recipe_id) VALUES
                    ('Spaghetti', 8,  'oz', 1),
                    ('Large Egg', 2,  '', 1),
                    ('Parmesan Cheese', 0.5,  'cup', 1),
                    ('Bacon', 4,  'slices', 1),
                    ('Garlic', 4,  'cloves', 1),
                    ('Parsely', 2,  'tbsp', 1),

                    ('Boneless Ribeye', 1.2,  'lb', 2),
                    ('Vegetable Oil', 2,  'tbsp', 2),
                    ('Onion', 1,  '', 2),
                    ('Mushrooms', 10,  'oz', 2),
                    ('Butter', 3,  'tbsp', 2),
                    ('Flour', 2,  'tbsp', 2),
                    ('Beef Broth', 2,  'cup', 2),
                    ('Dijon Mustard', 1,  'tbsp', 2),
                    ('Sour Cream', .66,  'cup', 2),
                           
                    ('Romaine Lettuce', 2, 'bunches', 3),
                    ('Cubed Bread', 0.5,  'cup', 3),
                    ('Caesar Dressing', 2,  'cup', 3),
                    ('Radish', 2,'', 3),
                    ('Roasted Chickpeas', 1.5,  'cup', 3),
                    ('Parmesan Cheese', 0.33,  'cup', 3),
                    ('Chives', 2,  'tbsp', 3),
                    ('Pinenuts', 2,  'tbsp', 3),

                    ('All-Purpose Flour', 1.5,  'cup', 4),
                    ('Baking Powder', 3.5,  'tsps', 4),
                    ('White Sugar', 1,  'tbsp', 4),
                    ('Salt', 0.25,  'tsps', 4),
                    ('Milk', 1.25,  'cup', 4),
                    ('Butter', 3,  'tbsp', 4),
                    ('Egg', 1,  '', 4),
                        
                    ('Extra Virgin Olive Oil', 0.25,  'cup', 5),
                    ('Onion', 1,  '', 5),
                    ('Bell Pepper', 1,  '', 5),
                    ('Garlic', 4,  'cloves', 5),
                    ('Tomato', 3,  '', 5),
                    ('Bay Leaf', 1,  '', 5),
                    ('White Wine', 0.25,  'cup', 5),
                    ('Boneless Skinless Chicken Thighs', 4,  '', 5),
                    ('Parsely', 0.25,  '', 5),
                    ('Spanish Rice', 2,  'cups', 5),
                    ('Chicken Broth', 5,  'cups', 5),
                    ('Frozen Peas', 0.5,  'cups', 5),
                    ('Jumbo Shrimp', 0.5,  'lb', 5),
                    ('Muscles', 0.5,  'lb', 5),
                    ('Calamari Ring', 8,  'oz', 5);
            ''')

            logger.debug('Ingredient Table Population Complete')
        except:
            logger.error('SQL STATEMENT IN Ingredient FAILED TO EXECUTE')

    else:
        logger.info('Ingredient Table Already Populated')

    cursor.execute('''
            INSERT INTO GroceryItem (name, nutrition_id, ingredient_id, kroger_product) VALUES 
            ('Bacon', 7, 4, 0),
            ('All-Purpose Flour', 7, 4, 0),
            ('Bay Leaf', 2, 4, 0),
            ('Beef Broth', 4, 4, 0),
            ('Butter', 9, 4, 0),
            ('Butter', 9, 11, 0),
            ('Chicken Broth', 10, 41, 0);
            '''
        )

    for _ in range(0,30):

        cursor.execute('''
                INSERT INTO GroceryReceipt (date, total_amount, home_store, grocery_item)
                VALUES (?, ?, ?, ?)
            ''', (
                (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'), 
                round(random.uniform(20, 500), 2),
                random.randint(0, 5),
                random.randint(0, 5)
            ))

        cursor.execute('''
                INSERT INTO NutritionFact (calories, fat, carbs, protein) 
                VALUES (?, ?, ?, ?)
            ''', (
                random.randint(0,1500), 
                random.randint(0,100), 
                random.randint(0,200), 
                random.randint(0,100), 
            ))
    
    cursor.execute('''
            INSERT INTO Store (store_location) 
            VALUES ('903 University City Blvd'), ('1322 S Main St');
        '''  
        )

    conn.commit()
    conn.close()


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
                        INSERT INTO User (name, email, address, reg_date) VALUES ('{user.name}', '{user.email}', '{user.address}', '{user.date}');
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