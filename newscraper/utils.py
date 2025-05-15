import logging
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()   

DATABASE_URL = os.getenv("DATABASE_URL")

class DatabaseUtils:
    def __init__(self):
        self.connect_to_db()

    def connect_to_db(self):
        """Establishes a connection to the database and creates a cursor."""
        try:
            self.connection = psycopg2.connect(DATABASE_URL)

            self.cursor = self.connection.cursor()
            logging.info("Database connection successful")
        except Exception as e:
            logging.exception(f"Error connecting to database: {str(e)}")
            self.connection = None
            self.cursor = None

    def insert_data(self, table_name, data):
        if not self.cursor:
            logging.error("No database connection. Insert failed.")
            return

        # Convert datetime fields to strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        columns = data.keys()
        values = data.values()
        insert_query = sql.SQL(
            """
            INSERT INTO {table} ({fields})
            VALUES ({placeholders})
            """
        ).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
        )
        try:
            self.cursor.execute(insert_query, tuple(values))
            self.connection.commit()
            logging.info(f"Data inserted successfully into {table_name}")
        except psycopg2.Error as e:
            logging.exception(f"Error inserting data: {str(e)}")
            self.connection.rollback()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logging.info("Database connection closed")