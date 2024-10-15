
# таблицы главной базы
import pandas as users 
import sqlite3 as db

import string
import random

from Email.Email import SendCodePecoverPasswordEmail

def Recovery(Email,mwdb):
    result = 'User not found'
    conn = db.connect(mwdb)
    q = "SELECT Name FROM Users WHERE Email = \'{}\'".format(Email)
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 1: # gives number of users
        # generate 4 sign activation code
        activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        cursor = conn.cursor()
        sql_update_query = "UPDATE USERS set VerifyCode = \'{}\' where Email = \'{}\'".format(activation_code, Email)
        cursor.execute(sql_update_query)
        conn.commit()
        cursor.close()
        SendCodePecoverPasswordEmail(Email, user['Name'][0], activation_code)
        result = 'OK'

    conn.close()

    return result