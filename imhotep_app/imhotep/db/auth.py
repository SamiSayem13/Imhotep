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
    def reset_user_password(User_ID, Password, match):
        try:
            # 'with' automatically opens and closes the connection and cursor
            with pymysql.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="imhotep",
                cursorclass=pymysql.cursors.Cursor
            ) as conn:
                with conn.cursor() as cur:

                    # 1. Get the STORED MATCH HASH for the user (ONE query)
                    # We use backticks (`) because 'user' and 'match' are SQL keywords
                    cur.execute("SELECT `match` FROM `user` WHERE `User_ID`=%s", (User_ID,))
                    result = cur.fetchone()

                    # 2. Check 1: Was the User_ID found?
                    if result is None:
                        return "Unique Code not found"

                    # 3. Check 2: (Fixes Crash Bug) Is the match column empty?
                    if result[0] is None:
                        return "Error: Security text not set for this user."

                    # 4. Check 3: Does the security text match?
                    stored_hash = result[0].encode('utf-8')

                    if bcrypt.checkpw(match.encode('utf-8'), stored_hash):
                        # SUCCESS! Both checks passed. Update the password.
                        hashed_pw = bcrypt.hashpw(Password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cur.execute("UPDATE `user` SET `Password`=%s WHERE `User_ID`=%s", (hashed_pw, User_ID))
                        conn.commit()
                        return "Password successfully updated"
                    else:
                        # User was found, but the 'match' text was wrong
                        return "Invalid Credentials"

        # 5. Correct exception handling
        except pymysql.Error as e:
            return "Database Error: " + str(e)
        except Exception as e:
            # Catch any other error (like bcrypt failing or the None.encode)
            return "An unexpected error occurred: " + str(e)
