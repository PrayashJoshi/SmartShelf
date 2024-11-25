import sqlite3
import logging
from typing import List
from datetime import datetime
from dataclasses import dataclass
from errors import DatabaseError

logger = logging.getLogger("")
logging.basicConfig(
    format="%(levelname)s:\t  %(message)s", level=logging.DEBUG
)


@dataclass
class MonthlyStatDetail:
    signup_date: str
    year: str
    signups: int


@dataclass
class UserDetail:
    name: str
    email: str
    password: str
    date: str = datetime.now().strftime("%Y-%m-%d")


class UserPipeline:
    def __init__(self, db_path='smartshelf.db'):
        self.db_path = db_path

    def _get_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")

    def add_new_user(self, new_user: UserDetail) -> bool:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO User (name, email, password, reg_date)
                VALUES (?, ?, ?, ?);
                """,
                [new_user.name, new_user.email, new_user.password, new_user.date]
            )
        except Exception as e:
            logger.error(f"Cannot add new user {e}")
        finally:
            cursor.commit()
            conn.close()

    def verify_credentials(self, email: str, password: str) -> bool:
        """Verify the user credentials on login and password changes"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            res = cursor.execute(
                """
                SELECT user_id, name, email from User
                WHERE email = ?
                AND password= ?;
                """,
                [email, password],
            )
            user = res.fetchone()
            if user is None:
                raise DatabaseError("User Not Found")
            return True
        except Exception as e:
            logger.error(f"Cannot verify user {e}")
            raise e
        finally:
            conn.close()

    def update_credentials(self, id: int, newInfo: UserDetail) -> bool:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE User
                SET name= ?, email= ?, password = ?
                WHERE user_id = ?;
                """,
                [newInfo.name, newInfo.email, newInfo.password, id],
            )
            return True
        except Exception as e:
            logger.error(f"Cannot verify user {e}")
            raise e
        finally:
            cursor.commit()
            conn.close()

    def get_monthly_signups(self) -> List[MonthlyStatDetail]:
        conn = self._get_db_connection()
        cursor = conn.cursor()
        try:
            res = cursor.execute(
                """
                SELECT strftime('%m, %Y', reg_date) AS signup_date,
                strftime('%Y', reg_date) AS year, Count(*) as signups
                FROM User GROUP BY signup_date ORDER BY year;
                """
            )
            column_names = [description[0] for description in cursor.description]
            result = [dict(zip(column_names, row)) for row in res.fetchall()]
            return result
        except Exception as e:
            logger.error(f"Cannot fetch monthly statistics {e}")
        finally:
            conn.close()
