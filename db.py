import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="98.86.9.11",
        user="root",
        password="Srii@773",
        database="atirath"
    )
