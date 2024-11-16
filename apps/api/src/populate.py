from typing import List
import requests
import sqlite3
import csv
import os
from dotenv import load_dotenv
from enum import Enum
import ast
import logging

def populate():
  load_dotenv()

  logger = logging.getLogger('')
  logging.basicConfig(format='%(levelname)s:\t  %(message)s',level=logging.DEBUG)

  def category_helper(row: List[str]) -> str:
    if (row.find('main-dish') > 0):
      return 'Main'
    elif (row.find('side-dishes') > 0):
      return 'Side'
    elif (row.find('desserts') > 0):
      return 'Dessert'
    elif (row.find('appetizers') > 0):
      return 'Appetizer'
    elif (row.find('beverages') > 0):
      return 'Beverage'
    else:
      return 'Etc'

  def nutrient_info_helper(nutrients):
    fact_info = {
      'calories':0,
      'carbs':0,
      'fat':0,
      'protein':0
    }
    for nutrient in nutrients:
      if nutrient['nutrientId'] == 1003:
        fact_info['protein'] = nutrient['value']
      if nutrient['nutrientId'] == 1004:
        fact_info['fat'] = nutrient['value']
      if nutrient['nutrientId'] == 1005:
        fact_info['carbs'] = nutrient['value']
      if nutrient['nutrientId'] == 1008:
        fact_info['calories'] = nutrient['value']
    return fact_info
  '''
  Populate Data To Database

  Data found in foodRecipes.csv pulled from Food.com
  '''
  with open('src/test.csv', newline='') as csvfile:
    conn = sqlite3.connect("smartshelf.db")
    cursor = conn.cursor()

    logger.info("Initializing Database")

    cursor.executescript(
      '''
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
          cooking_time INTEGER,
          url TEXT
      );
      
      CREATE TABLE IF NOT EXISTS NutritionFact (
          nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          calories REAL,
          fat REAL,
          carbs REAL,
          protein REAL
      );

      CREATE TABLE IF NOT EXISTS Ingredient (
          ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          recipe_id INTEGER,
          nutrition_id INTEGER,
          FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
          FOREIGN KEY (nutrition_id) REFERENCES NutritionFact(nutrition_id)
      );

      CREATE TABLE IF NOT EXISTS GroceryItem (
          grocery_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS Receipt (
          receipt_id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          price FLOAT NOT NULL,
      );

      '''
    )

    '''
    0 - title
    2 - minutes
    5 - tag
    6 - nutrition
    10 - ingredients

    Labels:
      Main-Dish (main-dish)
      Side-Dish (side-dishes)
      Desserts
      Appetizers
      Beverages
      Etc
    '''
    data= csv.reader(csvfile)
    cursor.execute('DELETE FROM Recipe;')
    cursor.execute('DELETE FROM NutritionFact;')
    next(data)

    res = cursor.execute("SELECT COUNT(*) from User")
    count = res.fetchone()

    logger.info('Attempting To Populate User Table')
    if (count[0] == 0):
      try:
        cursor.executescript(
          '''
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
          '''
        )
        logger.debug('User Table Population Complete')
      except:
        logger.error('SQL STATEMENT IN User FAILED TO EXECUTE')


    row_id = 0
    for row in data:
      category = category_helper(row[5])
      title = " ".join(row[0].split()).title()
      logger.debug(f"Insert {title}")
      cursor.execute("INSERT INTO Recipe (name, category, cooking_time, url) VALUES (?, ?, ?, ?)", [title, category, row[2], "-".join(row[0].split())+f"-{row[1]}"])
      for ingredient in ast.literal_eval(row[10]):
        res = requests.post(f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv('NUTRITION_KEY')}", json={'query':f'{ingredient}'})
        nutrition_info = res.json()
        found = False
        # search raw ingredients
        for food in nutrition_info['foods']:
          if food['dataType'] == "Foundation":
            found = True
            nutrients = food['foodNutrients']
            info = nutrient_info_helper(nutrients)
            logger.info(f"Insert {ingredient}: {info}")
            cursor.execute("INSERT INTO NutritionFact (name, calories, fat, carbs, protein) VALUES (?, ?, ?, ?, ?)",
                          [ingredient.title(), info['calories'], info['fat'], info['carbs'], info['protein']])
            break
        # pull first manufactured ingredient
        if not found:
          food = nutrition_info['foods'][0]
          nutrients = food['foodNutrients']
          info = nutrient_info_helper(nutrients)
          logger.info(f"Insert {ingredient}: {info}")
          cursor.execute("INSERT INTO NutritionFact (name, calories, fat, carbs, protein) VALUES (?, ?, ?, ?, ?)", 
                          [ingredient.title(), info['calories'], info['fat'], info['carbs'], info['protein']])
        
        # cursor.execute("INSERT INTO Ingredient (name, recipe_id, nutrition_id) VALUES (?, ?, ?)", 
        #                 [ingredient.title(), row_id, 0])

      row_id += 1

    conn.commit()
    conn.close()
