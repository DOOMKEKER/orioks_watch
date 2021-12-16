import db_sql
import connect
from pandas import DataFrame

def new_scores(tel_id, conn):
    login, password = db_sql.get_user(tel_id, conn)
    db_scores = db_sql.get_scores(tel_id, conn)
    orioks_scores = connect.request_scores(login, password)

    insert_scores = {}
    update_scores = {}
    for subject in orioks_scores:
        for sh in orioks_scores[subject]:
            #check if there is data from the site in the database
            #it's a bit confusing, but in short I divide scores those that new and those that have been updated
            if not db_scores.isin([subject,sh,orioks_scores[subject][sh]]).all(axis=1).any():
                if not db_scores.loc[:,["subject","cm"]].isin([subject,sh]).all(axis=1).any():
                    if not subject in insert_scores:
                        insert_scores[subject] = {}
                    insert_scores[subject][sh] = orioks_scores[subject][sh]
                    continue
                if not subject in update_scores:
                    update_scores[subject] = {}
                update_scores[subject][sh] = orioks_scores[subject][sh]
    return insert_scores, update_scores