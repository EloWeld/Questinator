import json
import sqlite3

import psycopg2
from aiogram.types import User

from Src.config import Role, DB_CREDS


class Database:
    def __init__(self, path_to_db="Data.db"):
        self.NON_POSGRE_SQL = False
        super(Database, self).__init__()
        self.path_to_db = path_to_db
        self.NON_POSGRE_SQL = True

    @property
    def connection(self):
        if self.NON_POSGRE_SQL:
            return sqlite3.connect(self.path_to_db)
        else:
            return psycopg2.connect(dbname=DB_CREDS["USER"],
                                    user=DB_CREDS["USER"],
                                    password=DB_CREDS["PASSWORD"],
                                    host=DB_CREDS["HOST"])

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        if self.NON_POSGRE_SQL:
            sql = sql.replace('%s', '?')
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data


class UsersDatabase(Database):
    def __init__(self):
        super(UsersDatabase, self).__init__()

    def addUser(self, user: User):
        sql = 'INSERT INTO users(tgid, username, fullname) VALUES (%s, %s, %s)'
        params = (user.id, user.username, user.full_name)
        data = self.execute(sql, params, commit=True)
        return data

    def allUsers(self):
        sql = 'SELECT * FROM users'
        data = self.execute(sql, fetchall=True)
        if not data or len(data) == 0:
            return []
        d = [dbUserModel(x) for x in data]
        # self.last_users.update({x["id"]: x for x in d})
        return d

    def allUsersId(self):
        return [x["tgid"] for x in self.allUsers()]

    def allContrasId(self):
        return [x["tgid"] for x in self.allUsers() if x["role"] == Role.User.value]

    def getUser(self, user_tgid):
        sql = 'SELECT * FROM users ' \
              'WHERE tgid = %s'
        params = (user_tgid,)
        data = self.execute(sql, params, fetchone=True)
        d = dbUserModel(data)
        # self.last_users[d["id"]] = d
        return d

    def getUserByContraNick(self, nickname):
        sql = 'SELECT * FROM users ' \
              'WHERE contra_nick = %s'
        params = (nickname,)
        data = self.execute(sql, params, fetchone=True)
        if data is None:
            return None
        d = dbUserModel(data)
        if d is None:
            return None
        # self.last_users[d["id"]] = d
        return d

    def all_admins(self):
        return [x for x in self.allUsers() if x["role"] == Role.Admin.value]

    def allAdminsId(self):
        return [x["tgid"] for x in self.allUsers() if x["role"] == Role.Admin.value]

    def get(self, user_tgid, column):
        sql = 'SELECT * FROM users ' \
              'WHERE tgid = %s'
        params = (user_tgid,)
        data = self.execute(sql, params, fetchone=True)
        if data is None:
            return -1
        d = dbUserModel(data)
        if d is None:
            return -1
        # self.last_users[d["id"]] = d
        return d[column]

    def update(self, user_tgid, column, value):
        sql = f'UPDATE users ' \
              f'SET {column} = %s ' \
              f'WHERE tgid = %s'
        params = (value, user_tgid)
        data = self.execute(sql, params, commit=True)
        return data

    def registerContra(self, user_tgid, data):
        sql = f'UPDATE users ' \
              f'SET (description, photo, soc_net_links, contra_nick, statuses) = (%s, %s, %s, %s, %s) ' \
              f'WHERE tgid = %s'
        params = (data["description"],
                  data["photo"],
                  json.dumps(data["links"]),
                  data["contra_nick"],
                  data["statuses"],
                  user_tgid)
        data = self.execute(sql, params, commit=True)
        return data


class WithdrawsDatabase(Database):
    def __init__(self):
        super(WithdrawsDatabase, self).__init__()

    def add_request(self, sender_id, amount):
        sql = 'INSERT INTO wd_requests(sender_id, amount) VALUES (%s, %s)'
        params = (sender_id, amount)
        data = self.execute(sql, params, commit=True)
        return data

    def all_requests(self):
        sql = 'SELECT * FROM wd_requests'
        data = self.execute(sql, fetchall=True)
        if not data or len(data) == 0:
            return []
        d = [dbWDRModel(x) for x in data]
        return d

    def update_withdraw(self, trans_id: int, column: str, new_value: str):
        sql = f'UPDATE wd_requests ' \
              f'SET {column} = %s ' \
              f'WHERE trans_id = %s'
        params = (new_value, trans_id)
        data = self.execute(sql, params, commit=True)
        return data

    def get(self, trans_id: int):
        sql = 'SELECT * FROM wd_requests ' \
              'WHERE trans_id = %s'
        params = (trans_id,)
        data = self.execute(sql, params, fetchone=True)
        return dbWDRModel(data)


class QuestDatabase(Database):
    def __init__(self):
        super(QuestDatabase, self).__init__()

    def send_question(self, sender_id, contra_id, question: dict, price):
        sql = 'INSERT INTO questions(s_id, r_id, question, amount) VALUES (%s, %s, %s, %s)'
        params = (sender_id, contra_id, json.dumps(question), price)
        data = self.execute(sql, params, commit=True)
        return data

    def all_questions(self):
        sql = 'SELECT * FROM questions'
        data = self.execute(sql, fetchall=True)
        if not data or len(data) == 0:
            return []
        d = [dbQuestionModel(x) for x in data]
        return d

    def update_question(self, q_id: int, column: str, new_value: str):
        sql = f'UPDATE questions ' \
              f'SET {column} = %s ' \
              f'WHERE q_id = %s'
        params = (new_value, q_id)
        data = self.execute(sql, params, commit=True)
        return data

    def update_questions(self, q_id: int, d: dict):
        sql = f'UPDATE questions ' \
              f'SET ({", ".join(d.keys())}) = ({", ".join(["%s"] *len(d))}) ' \
              f'WHERE q_id = %s'
        params = tuple(list(d.values()) + [q_id])
        data = self.execute(sql, params, commit=True)
        return data

    def questsByContraID(self, contra_id: int):
        return [x for x in self.all_questions() if int(x["r_id"]) == contra_id]

    def activeContraQuests(self, contra_id: int):
        return [x for x in self.questsByContraID(contra_id) if x["status"] == "NOT_ANSWERED"]

    def questByID(self, question_id: int):
        qsts = [x for x in self.all_questions() if int(x["q_id"]) == int(question_id)]
        if len(qsts) == 0:
            return None
        return qsts[0]


# Models
def dbWDRModel(x):
    if not x:
        return None
    result = dict(sender_id=x[0],
                  amount=x[1],
                  trans_id=int(x[2]),
                  status=x[3],
                  )
    return result


def dbUserModel(x):
    if not x:
        return None
    result = dict(id=x[0],
                  tgid=x[1],
                  role=int(x[2]),
                  username=x[3],
                  fullname=x[4],
                  deposit=float(x[5]),
                  photo=str(x[6]),
                  description=str(x[7]),
                  soc_net_links=tojson(x[8]),
                  abilities=tojson(x[9]),
                  contra_nick=x[10],
                  statuses=x[11],
                  withdraw_data=tojson(x[12]),
                  custom_fee=float(x[13]),
                  )
    return result


def dbQuestionModel(x):
    if not x:
        return None
    result = dict(s_id=x[0],
                  r_id=x[1],
                  question=tojson(x[2]),
                  status=x[3],
                  amount=x[4],
                  q_answer=tojson(x[5]),
                  q_id=x[6],
                  )
    return result


def tojson(x):
    if x is None:
        return None
    elif isinstance(x, dict):
        return x
    else:
        return json.loads(x)


WithdrawsDB = WithdrawsDatabase()
UsersDB = UsersDatabase()
QuestDB = QuestDatabase()
