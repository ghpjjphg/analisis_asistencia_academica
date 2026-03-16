import os
import mysql.connector

conn = mysql.connector.connect(
    host=os.getenv("ballast.proxy.rlwy.net"),
    port=int(os.getenv("28843")),
    user=os.getenv("root"),
    password=os.getenv("ftkwrcyxjPORSuENUHimDvgtOYOvyJlu"),
    database=os.getenv("railway")
)
