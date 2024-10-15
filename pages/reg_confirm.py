# таблицы главной базы
import pandas as users 
import sqlite3 as db
def ConfirmAccount(activation_code, mwdb):
    conn = db.connect(mwdb)
    q = "SELECT Email FROM Users WHERE VerifyCode = \'{}\'".format(activation_code)
    
    result = "Confirmation account error"
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 1: # found, confirmation Ok
        try:
            print(user['Email'][0])
            cursor = conn.cursor()
            sql_update_query = "UPDATE USERS set Approved = 'yes' where Email = \'{}\'".format(user['Email'][0])
            cursor.execute(sql_update_query)
            sql_update_query = "UPDATE USERS set VerifyCode = '0000' where Email = \'{}\'".format(user['Email'][0])
            cursor.execute(sql_update_query)
            conn.commit()
            cursor.close()
            result = "OK"
        except Exception as e: 
            print (str(e))
            result =  str(e)

    return result