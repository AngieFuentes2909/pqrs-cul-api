import pg8000
import os

class Database:
    _instance = None

    def __init__(self):
        self.connection = None
        self.connect()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def connect(self):
        try:
            self.connection = pg8000.connect(
                host     = os.getenv('DB_HOST', 'localhost'),
                port     = int(os.getenv('DB_PORT', 5432)),
                database = os.getenv('DB_NAME', 'pqrs_cul'),
                user     = os.getenv('DB_USER', 'postgres'),
                password = os.getenv('DB_PASSWORD', '2909'),
            )
            self.connection.autocommit = True
            print("✅ Conectado a PostgreSQL")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            raise e

    def get_cursor(self):
        try:
            return self.connection.cursor()
        except Exception:
            self.connect()
            return self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.close()