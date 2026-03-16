import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("ballast.proxy.rlwy.net"),
    port=int(os.getenv("28843")),
    user=os.getenv("root"),
    password=os.getenv("ftkwrcyxjPORSuENUHimDvgtOYOvyJlu"),
    database=os.getenv("railway")
    )
