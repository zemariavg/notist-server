import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PSW = os.getenv("MYSQL_PSW")


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=MYSQL_USER,
        password=MYSQL_PSW,
        database=MYSQL_DB,
        port=DB_PORT
    )
