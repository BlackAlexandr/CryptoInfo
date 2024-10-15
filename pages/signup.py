"""
Signup page code execution
"""
import re
import bcrypt
import datetime
import string
import random

# таблицы главной базы
import pandas as users 
import sqlite3 as db

from Email.Email import SendCodeConfirmAccountEmail


def CheckingEmail(mwdb, email):
    conn = db.connect(mwdb)
    q = "SELECT Email FROM Users WHERE Email = \'{}\'".format(email)
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 0:
        return 'New'
    else:
        return 'Email is already registered'

def DoSignup(name, Email, enteredpsw, country, mwdb):
    newID = 0 # havent newID value
    result = 'Error'
    conn = db.connect(mwdb)
    q = "SELECT Password FROM Users WHERE Email = \'{}\'".format(Email)
    
    user = users.read_sql_query(q, conn)
    if user.shape[0] == 0: # not registered, do it
        if IsValidPassword(enteredpsw):
            try:
                # generate 4 sign activation code
                activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                
                bytes = enteredpsw.encode('utf-8')
                # generating the salt for unique hash
                salt = bcrypt.gensalt()
                hash = bcrypt.hashpw(bytes, salt)
                dttext = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                tmexp = datetime.datetime.today() + datetime.timedelta(days=14)
                dttextexp = tmexp.strftime('%Y-%m-%d %H:%M:%S')
                dbcursor = conn.cursor()
                dbcursor.execute("INSERT INTO USERS (Name,Email,Password,Country,Telegram,DateReg,TrialExpired,LastPaid,Approved,VerifyCode) values (?,?,?,?,?,?,?,?,?,?)", (name,Email,hash,country,'no', dttext,dttextexp,'no','no', activation_code))
                conn.commit()
                result = 'OK'
                # reget his new id
                q = "SELECT ID FROM Users WHERE Email = \'{}\'".format(Email)
                user = users.read_sql_query(q, conn)
                if user.shape[0] > 0: # found created id
                    newID = user['ID'][0]
                else:
                    result = "Error: New user id not found"

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
    else: # already registered
        result = 'Warning: User already registered'

    conn.close()
    if newID > 0:
        SendCodeConfirmAccountEmail(Email, name, activation_code)
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
        elif not re.search("[_@$!#]" , psw):
            flag = False
            break
        elif re.search("\s" , psw):
            flag = False
            break
        else:
            flag = True
            break
    
    return flag