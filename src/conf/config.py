from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    DB_URL = os.getenv("DB_URL")


config = Config
