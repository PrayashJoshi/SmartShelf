from typing import List
import requests
import sqlite3
import csv
import os
from dotenv import load_dotenv
from enum import Enum
import ast

load_dotenv()

import logging
logger = logging.getLogger('')
logging.basicConfig(format='%(levelname)s:\t  %(message)s',level=logging.DEBUG)

'''
'''
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
          cursor.execute("INSERT INTO NutritionFact (name, calories, fat, carbs, protein, recipe_id) VALUES (?, ?, ?, ?, ?)",
                         [ingredient.title(), info['calories'], info['fat'], info['carbs'], info['protein']])
          break
      # pull first manufactured ingredient
      if not found:
        food = nutrition_info['foods'][0]
        nutrients = food['foodNutrients']
        info = nutrient_info_helper(nutrients)
        logger.info(f"Insert {ingredient}: {info}")
        cursor.execute("INSERT INTO NutritionFact (name, calories, fat, carbs, protein, recipe_id) VALUES (?, ?, ?, ?, ?)", 
                        [ingredient.title(), info['calories'], info['fat'], info['carbs'], info['protein']])
      
      cursor.execute("INSERT INTO Ingredient (name, recipe_id, nutrition_id) VALUES (?, ?, ?)", 
                      [ingredient.title(), row_id])

    row_id += 1

  conn.commit()
  conn.close()
