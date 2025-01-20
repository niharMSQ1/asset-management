from decouple import config
import mysql.connector
from mysql.connector import Error

connection = None

def get_connection():
    global connection
    if connection is None or not connection.is_connected():
        try:
            connection = mysql.connector.connect(
                host=config("HOST"),
                user=config("USER"),
                database=config("DB"),
                port=config("PORT"),
                password=config("PASSWORD"),
            )
        except Error as e:
            connection = None
    return connection