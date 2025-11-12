import pymysql
from pymysql import err as db_errors
import bcrypt

class AuthHandler:
    @staticmethod
    def verify_user_credentials(User_ID, Password):
        try:
            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.Cursor
            )
            cur = conn.cursor()
            cur.execute("SELECT Password FROM user WHERE User_ID=%s", (User_ID,))
            row = cur.fetchone()
            cur.close(); conn.close()

            if not row:
                return "Invalid Credentials"

            stored_hash = row[0]
            if bcrypt.checkpw(Password.encode('utf-8'), stored_hash.encode('utf-8')):
                return "Login Success"
            else:
                return "Invalid Credentials"

        except db_errors.Error as e:
            return "Database Error: " + str(e)

    @staticmethod
    def reset_user_password(User_ID, Password):
        try:
            conn = pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.Cursor
            )
            cur = conn.cursor()

            cur.execute("SELECT User_ID FROM user WHERE User_ID=%s", (User_ID,))
            if cur.fetchone() is None:
                cur.close(); conn.close()
                return "Unique Code not found"

            hashed_pw = bcrypt.hashpw(Password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE user SET Password=%s WHERE User_ID=%s", (hashed_pw, User_ID))
            conn.commit()
            cur.close(); conn.close()

            return "Password successfully updated"

        except db_errors.Error as e:
            return "Database Error: " + str(e)
