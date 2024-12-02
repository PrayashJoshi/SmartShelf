# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from populate import Populate
from dotenv import load_dotenv
from routers import users, recipes, receipts, facts

app = FastAPI()
app.include_router(router=users.router)
app.include_router(router=receipts.router)
app.include_router(router=recipes.router)
app.include_router(router=facts.router)

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


@app.on_event("startup")
def init_db():
    """ Function to initialize the SQLite database and create tables """
    load_dotenv()
    Populate()
