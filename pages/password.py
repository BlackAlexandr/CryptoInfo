

import re
import bcrypt

# таблицы главной базы
import pandas as users 
import sqlite3 as db

def DoChangeRecoverPassword(verify_code, enteredpsw, mwdb):
    newID = 0 # havent newID value
    result = 'Error'
    conn = db.connect(mwdb)
    q = "SELECT Password FROM Users WHERE VerifyCode = \'{}\'".format(verify_code)
    
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 1: # not registered, do it
        if IsValidPassword(enteredpsw):
            try:
                bytes = enteredpsw.encode('utf-8')
                # generating the salt for unique hash
                salt = bcrypt.gensalt()
                hash = bcrypt.hashpw(bytes, salt)
                
                dbcursor = conn.cursor()
                q = "UPDATE USERS SET Password = ? WHERE VerifyCode = ?"
                dbcursor.execute(q, (hash, verify_code))
                conn.commit()
                q = "UPDATE USERS SET VerifyCode = '0000' WHERE VerifyCode = \'{}\'".format(verify_code)
                dbcursor.execute(q)
                conn.commit()
                result = 'OK'
                
            except Exception as e: 
                print (str(e))
                result = str(e)
        else:
            result = 'Primary conditions for password validation:\
                    \n\
                    \n Minimum 8 characters.\
                    \n The alphabet must be between [a-z]\
                    \n At least one alphabet should be of Upper Case [A-Z]\
                    \n At least 1 number or digit between [0-9].\
                    \n At least 1 character from [ _ or @ or $ ].\
                    '
    else: 
        result = 'Invalid verification code'

    conn.close()

    return result

'''
Primary conditions for password validation:

Minimum 8 characters.
The alphabet must be between [a-z]
At least one alphabet should be of Upper Case [A-Z]
At least 1 number or digit between [0-9].
At least 1 character from [ _ or @ or $ ].
'''
# Python program to check validation of password
# Module of regular expression is used with search()
def IsValidPassword(psw):
    flag = True
    while True:
        if (len(psw)<=8):
            flag = False
            break
        elif not re.search("[a-z]", psw):
            flag = False
            break
        elif not re.search("[A-Z]", psw):
            flag = False
            break
        elif not re.search("[0-9]", psw):
            flag = False
            break
        elif not re.search("[_@$]" , psw):
            flag = False
            break
        elif re.search("\s" , psw):
            flag = False
            break
        else:
            flag = True
            break
    
    return flag