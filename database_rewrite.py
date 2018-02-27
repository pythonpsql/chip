
from psycopg2 import pool, sql


class Database():
    __connection_pool = None
    def __init__(self, **kwargs):
        self.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)


    # def initialise(**kwargs):
        # Database.__connection_pool = pool.SimpleConnectionPool(1,
                                                               # 10,
                                                               # **kwargs)

    def get_connection(self):
        return self.__connection_pool.getconn()

    def return_connection(self, connection):
        self.__connection_pool.putconn(connection)

    def close_all_connections(self):
        self.__connection_pool.closeall()


class CursorFromConnectionFromPool():
    def __init__(self, **kwargs):
        self.db = Database(**kwargs)
        self.connection = None
        self.cursor = None

    def __enter__(self):
        print("__enter__")
        print(self.db)
        self.connection = self.db.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:  # TypeError, AttributeError, ValueError
            self.connection.rollback()
        else:
            self.cursor.close
            self.connection.commit()
        self.db.return_connection(self.connection)

if __name__ == "__main__":
    c1 = CursorFromConnectionFromPool(database='chip', host='localhost', user='dba_tovak')
    c2 = CursorFromConnectionFromPool(database='deck', host='localhost', user='dba_tovak')
    with c1 as cursor:
        cursor.execute("select * from sale_invoice")
        print(cursor.fetchall())
    with c2 as cursor:
        cursor.execute("select * from customer")
        print(cursor.fetchall())
