import mysql.connector
def get_conn():
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",          # your password here
            database="imhotep",
            connection_timeout=5, # prevent hangs
            autocommit=False
        )