import psycopg2
from app.core.config import settings
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT



def create_database(dbname, user, password, host, port):
    connection = psycopg2.connect(user=user, password=password, port=port, host=host)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(f'CREATE DATABASE {dbname}')
    cursor.close()
    connection.close()
    print(f"База данных {dbname} - создана")


if __name__ == '__main__':
    create_database(settings.db_name, settings.user, settings.password, settings.password, settings.port)




