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
    sql_command = f"""SELECT users.tel_id, cm_s.subject, cm_s.cm, cm_s.ball FROM users
                        JOIN cm_s ON users.tel_id = cm_s.tel_id
                        WHERE users.tel_id = '{tel_id}';
                    """
    data = pd.read_sql(sql_command, conn)
    return data.iloc[:,1:4]

def update_insert_user(tel_id, login, password, cursor, choose, conn):
    if choose == "add":
        sql_command = f"""UPDATE users
                            SET login = '{login}', password = '{password}'
                            WHERE tel_id = '{tel_id}';
                        """
    elif choose == "change":
        sql_command = f"""INSERT INTO users (tel_id, login, password)
                            VALUES ({tel_id}, {login}, {password});"
                        """
    cursor.execute(sql_command)
    conn.commit()
    return 0

def get_user(tel_id, conn):
    sql_command = f"""SELECT login, password FROM users
                        WHERE tel_id = '{tel_id}';
                    """
    data = pd.read_sql(sql_command, conn)
    return data["login"][0], data["password"][0]

def get_all_users(conn):
    sql_command = "SELECT tel_id FROM users;"
    data = pd.read_sql(sql_command, conn)
    return data

def receive_notifications(tel_id, cursor, yes_no, conn):
    sql_command = f"""UPDATE users
                        SET notifications = '{yes_no}'
                        WHERE tel_id = '{tel_id}';
                    """
    cursor.execute(sql_command)
    conn.commit()
    return 0

def insert_data(tel_id, data, cursor, conn):
    sql_command = ""
    for subject in data:
        for cm in data[subject]:
            ball = data[subject][cm]
            sql_command += f"""INSERT INTO cm_s (tel_id, subject, cm, ball)
                            VALUES ('{tel_id}', '{subject}', '{cm}', '{ball}');\n
                            """
    cursor.execute(sql_command)
    conn.commit()
    return 0

def update_data(tel_id, data, cursor, conn):
    sql_command = ""
    for subject in data:
        print(subject)
        for cm in data[subject]:
            ball = data[subject][cm]
            sql_command += f"""UPDATE cm_s 
                                SET ball = '{ball}'
                                WHERE tel_id = '{tel_id}' AND
                                    subject = '{subject}' AND
                                    cm ='{cm}';\n
                            """
    cursor.execute(sql_command)
    conn.commit()
    return 0