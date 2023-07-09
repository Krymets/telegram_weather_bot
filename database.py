

class DataBase:
    def __init__(self):
        pass

    def connect(self):
        self.conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        self.cursor = self.conn.cursor()
        self.conn.autocommit = True

    def end_connection(self):
        self.cursor.close()
        self.conn.close()

    def create(self):
        pass