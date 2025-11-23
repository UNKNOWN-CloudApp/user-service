import mysql.connector.pooling

db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="user_service_pool",
    pool_size=10,
    host="136.112.51.68",
    port=3306,
    user="user",
    password="Unknown4153@",
    database="cloud"
)

def get_db():
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()