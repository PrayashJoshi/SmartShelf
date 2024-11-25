import sqlite3
import logging
from typing import List
from datetime import datetime
from dataclasses import dataclass
from errors import DatabaseError
import shortuuid

logger = logging.getLogger("")
logging.basicConfig(format="%(levelname)s:\t  %(message)s", level=logging.DEBUG)


@dataclass
class ReceiptItemDetail:
    name: str
    price: float


@dataclass
class ReceiptDetail:
    ingredients: List[ReceiptItemDetail]
    user_id: int
    date: str = datetime.now().strftime("%Y-%m-%d")


@dataclass
class SummaryDetail:
    receipt_id: int
    add_date: str
    items: int
    total: float


@dataclass
class PriceDetail:
    total: int
    month: str
    year: str


class ReceiptPipeline:
    def __init__(self, db_path="smartshelf.db"):
        self.db_path = db_path

    def _get_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")

    def add_new_receipt(self, receipt: ReceiptDetail) -> bool:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            id = shortuuid.ShortUUID().random(length=32)
            for item in receipt.ingredients:
                print(item)
                cursor.execute(
                    """
                    INSERT INTO Receipt(
                        receipt_id,
                        name,
                        price,
                        add_date,
                        user_id)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    [id, item.name, item.price, receipt.date, receipt.user_id],
                )

            conn.commit()
            conn.close()
            return "ok"
        except Exception as e:
            print(e)
            return e

    def get_receipt_history(self, user_id: int) -> List[SummaryDetail]:
        """Verify the user credentials on login and password changes"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            res = cursor.execute(
                """
                    SELECT receipt_id, add_date, COUNT(*) as items,
                    SUM(price) as total
                    FROM Receipt
                    WHERE Receipt.user_id == ?
                    GROUP BY receipt_id
                    ORDER BY add_date DESC;
                    """[
                    user_id
                ]
            )

            column_names = [description[0] for description in cursor.description]
            result = [dict(zip(column_names, row)) for row in res.fetchall()]
            conn.close()
            return result
        except Exception as e:
            print(e)
            return e

    def get_price_history(self, year: int, user_id: int) -> List[PriceDetail]:
        try:
            conn = sqlite3.connect("smartshelf.db")
            cursor = conn.cursor()
            res = cursor.execute(
                """
                    SELECT SUM(price) as total,
                    strftime('%m', add_date) AS month,
                    strftime('%Y', add_date) AS year
                    FROM Receipt
                    WHERE Receipt.user_id == ?
                    AND year == ?
                    GROUP BY month
                    """,
                [user_id, year],
            )

            column_names = [description[0] for description in cursor.description]
            result = [dict(zip(column_names, row)) for row in res.fetchall()]
            conn.close()
            return result
        except Exception as e:
            print(e)
            return e

    def get_receipt_for_user(self, user_id: int, receipt_id: str):
        try:
            conn = sqlite3.connect("smartshelf.db")
            cursor = conn.cursor()
            res = cursor.execute(
                """
                    SELECT name, price
                    FROM Receipt
                    WHERE user_id == ?
                    AND receipt_id == ?;
                    """,
                [user_id, receipt_id],
            )

            column_names = [description[0] for description in cursor.description]
            result = [dict(zip(column_names, row)) for row in res.fetchall()]
            conn.close()
            return result
        except Exception as e:
            print(e)
            return e
