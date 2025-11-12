import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",   # XAMPP uses localhost / 127.0.0.1
            port=3306,          # confirmed port
            user="root",
            password="",        # leave blank unless you set a root password
            database="imhotep",
            connection_timeout=5
        )
        print("✅ Connected to MySQL (port 3306)")
        print("Database:", conn.database)

    except Error as e:
        print(f"❌ Connection error {e.errno}: {e.msg}")

    finally:
        try:
            if conn.is_connected():
                conn.close()
                print("🔒 Connection closed.")
        except:
            pass


if __name__ == "__main__":
    test_connection()
