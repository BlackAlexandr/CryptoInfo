"""
Example of creating a custom 404 page to display when the URL isn't found
"""
import bcrypt
import pandas as users 
import sqlite3 as db
#Функция авторизации
def CheckSignin(mail, enteredpsw, mwdb):
    result = 'Unknown username or password'
    conn = db.connect(mwdb)
    q = "SELECT ID, Password, Approved FROM Users WHERE Email = \'{}\'".format(mail)
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 1: 
        if user.loc[0]['Approved'] == 'yes':
            userpsw = user.loc[0]['Password'] 
            enteredBytes = enteredpsw.encode('utf-8')
            # проверка пароля
            if bcrypt.checkpw(enteredBytes, userpsw):
                result = 'OK'
            print(result)
        else:
            result = 'Account is not confirmed by user'

    conn.close()

    return result

#Функция получения id пользователя
def GetUserId(mwdb, mail):
    result = 0
    conn = db.connect(mwdb)
    q = "SELECT ID, Approved FROM Users WHERE Email = \'{}\'".format(mail)
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 1: # gives number of users
        if user.loc[0]['Approved'] == 'yes':
            usrId = user.loc[0]['ID']
            result = usrId
        else:
              result = 0
    return int(result)