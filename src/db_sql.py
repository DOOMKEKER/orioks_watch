import psycopg2
import pandas as pd
import config as creds

# Set up a connection to the postgres server.
def sql_connect():
    conn_string = "host="+ creds.PGHOST +" port="+ "5432" +" dbname="+ creds.PGDATABASE +" user=" + creds.PGUSER \
    +" password="+ creds.PGPASSWORD
    conn=psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return conn, cursor

def get_scores(tel_id, conn):
    sql_command = f"""SELECT users.tel_id, cm_s.subject, SUM(cm_s.ball) FROM users
                        JOIN cm_s on users.tel_id = cm_s.tel_id
                        GROUP BY users.tel_id, cm_s.subject
                        HAVING users.tel_id = '{tel_id}';
                    """
    data = pd.read_sql(sql_command, conn)
    return data

def insert_user(tel_id, login, password, cursor):
    sql_command = f"""INSERT INTO users (tel_id, login, password)
                        VALUES ({tel_id}, {login}, {password});"
                   """
    cursor.execute(sql_command)
    cursor.commit()
    return 0

def update_user(tel_id, login, password, cursor):
    sql_command = f"""UPDATE users
                        SET login = '{login}', password = '{password}'
                        WHERE tel_id = '{tel_id}';
                    """
    cursor.execute(sql_command) #TODO try: expect?
    cursor.commit()
    return 0

