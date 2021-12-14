import db_sql
import connect
from pandas import DataFrame

def new_scores(tel_id, conn):
    login, password = db_sql.get_user(tel_id)
    db_scores = db_sql.get_scores(tel_id, conn)
    orioks_scores = connect.request_scores(login, password)

    new_scores = {}
    for st in orioks_scores:
        for sh in orioks_scores[st]:
            #check if there is data from the site in the database
            if not db_scores.isin([st,sh,orioks_scores[st][sh]]).all(axis=1).any():
                if not st in new_scores:
                    new_scores[st] = {}
                new_scores[st][sh] = orioks_scores[st][sh]
    return new_scores