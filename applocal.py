from functools import wraps
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import dash_bootstrap_components as dbc
from datetime import timedelta
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user, login_required, login_manager
from utils.login_handler import restricted_page

# Локальные импорты модулей вставлять после инстанта основного модуля приложения
# Там откуда начинается  import pages.signin as signin_page
login_manager = LoginManager()
server = Flask(__name__,
            static_folder='assets',
            template_folder='assets')
       
# Настройка сессии на сервере
server.secret_key = 'BAD_SECRET_KEY'
server.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=35)

@server.before_request
def make_session_permanent():
    session.permanent = True
    server.permanent_session_lifetime = timedelta(minutes=35)

# -------------- Импорт обработчиков по соответствующим страницам ------------
import pages.signin as signin_page
import pages.signup as signup_page
import pages.recover as recovery_page
import pages.reg_confirm as confirm_page
import pages.password as recoverpsw_page
from pages.main import MWDb 
import pages.briefcase as briefcase_page
import pages.markets as markets
import pages.menu as menu

# Создаем объект login_manager для авторизация пользователей
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


# Класс пользователь для login_manager
class User(UserMixin):
    # Сохроняем в модели id пользователя
    def __init__(self, username):
        self.id = username

# Проверка на авторизацию пользователя
@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)

# ---------------------- Маршрутизация -----------------
@server.route('/')
def index():
    return render_template('/markets/market.html')

@server.route('/contacts')
def contacts():
    return render_template('/Contacts/contacts.html')

@server.route('/about')
def about():
    return render_template('/About/about.html')

@server.errorhandler(404)
def page_not_found(e):
    return render_template('/NotFound/error.html'), 404

@server.route('/signin')
def signin():
    if current_user.is_authenticated is True:
        return redirect('/')
    else:
        return render_template('/Login/Signin/signin.html')

@server.route('/signup')
def signup():
    if current_user.is_authenticated is True:
        return redirect('/')
    else:
        return render_template('/Login/Signup/signup.html')

@server.route('/recovery')
def recovery():
    if current_user.is_authenticated is True:
        return redirect('/')
    else:
        return render_template('/Login/Recovery/recovery.html')
    
@server.route('/changing-pass')
def changingPass():
    if current_user.is_authenticated is True:
        return redirect('/')
    else:
        return render_template('/Login/Recovery/password.html')   

@server.route('/confirm')
def confirm():
    if current_user.is_authenticated is True:
        return redirect('/')
    else:
        return render_template('/Login/Signup/reg_confirm.html')

@server.route('/briefcase')
@login_required
def briefcase():
    return render_template('/Profile/briefcase.html')


@server.route('/getMenu')
def getMenu():
    user = ''
    if current_user.is_authenticated is True:
        user = current_user.id
    return menu.GetMenu(user)

@server.route('/logoutUser')
def logoutUser():
    logout_user()
    return redirect('/signin')  # redirect to ЛИЧНЫЙ КАБИНЕТ

# авторизация на сайте, вход по Login
@server.route('/login', methods=['POST'])
def login():
    mail = request.form['Email']
    psw = request.form['Password']
    result = signin_page.CheckSignin(mail, psw, MWDb)
    
    if result == 'OK':
        # обозначаем в login_manager что пользователь авторизовался
        login_user(User(mail))
        return redirect('/briefcase')  # redirect to ЛИЧНЫЙ КАБИНЕТ
    else:
          return redirect('/signin') 

# регистрация на сайте по Email
@server.route('/checkingEmail')
def checkingEmail():
    mail =  request.args.get('mail', 0)
    return signup_page.CheckingEmail(MWDb, mail)

# регистрация на сайте по Email
@server.route('/userSignup', methods=['POST'])
def userSignup():
    name = request.form['Name']
    mail =  request.form['Email']
    psw = request.form['Password']
    country = request.form['Country']
    result = signup_page.DoSignup(name, mail, psw, country, MWDb)
    if result == 'OK':
        return redirect('/confirm')# redirect to ПОДТВЕРЖДЕНИЕ ПАРОЛЯ
    return redirect('/signup')


# функция для подтверждения регистрации
# для примера может получать уникальный номер пользователя
# если все ок то активируем кабинет
@server.route('/checkConfirmPsw', methods=['POST'])
def checkConfirmPsw():
    confirmCode = request.form['confirm_code']
    result =  confirm_page.ConfirmAccount(confirmCode, MWDb)
    if result == 'OK':
        print(result) # Redirect to confirmation success here
        return redirect('/recovery/password')
    else:
        print(result) # Redirect to confirmation ERROR here
        return jsonify(result=False)
    
# функция для подтверждения изменения пароля
# на почту приходит код подтверждения
# если все ок то активируем кабинет
@server.route('/regConfirm', methods=['POST'])
def regConfirm():
    confirmCode = request.form['confirm_code']
    result =  confirm_page.ConfirmAccount(confirmCode, MWDb)
    if result == 'OK':
        print(result) # Redirect to confirmation success here
        return redirect('/signin')
    else:
        print(result) # Redirect to confirmation ERROR here
        return jsonify(result=False)


#Функция запроса восстановления пароля
#Получаем email юзера 
#Отправляем ему письмо с ссылкой на изменения пароля
#Переходим на страницу ввода кода
@server.route('/recoverPassword', methods=['POST'])
def recoverPassword():
    mail =  request.form['mail'].strip()
    result = recovery_page.Recovery(mail, MWDb)
    if result == 'OK':
         # почта такая есть, email отправлен с ссылкой на страницу восстановления пароля
        return redirect('/recovery/password')
    
    session['error'] = 'messages'
    return redirect('/error') # такой пользователь не найден


#Функция для восстановления пароля
#Получаем новый пароль и заменяем его в базе
@server.route('/changePassword', methods=['POST'])
def changePassword():
    verify_code = request.form['code']
    newPsw = request.form['newP']

    recoverpsw_page.DoChangeRecoverPassword(verify_code, newPsw, MWDb)
    return redirect('/signin')

#Функция для получения ошибки
#Получаем ошибку и отображаем ее на специальной странице
@server.route('/getError/')
def getError():
    error = session['error']
    return jsonify(message = error)

#Функция выгрузки списока рынков из бд
@server.route('/GetMarkets')
def GetMarkets():
    return jsonify(message = briefcase_page.GetMarkets(MWDb))

#Функция выгрузки компаний из бд
@server.route('/GetCompanies')
def GetCompanies():
    idMarket =  request.args.get('idMarket', 0)
    return jsonify(data = briefcase_page.GetCompanies(MWDb, idMarket))

#Функция добавления позиции в существующий портфель
@server.route('/AddPositionToPortfolio', methods=['POST'])
def AddPositionToPortfolio():
    return jsonify(briefcase_page.AddPositionToPortfolio(MWDb, request.get_json()))

#Функция 
@server.route('/CheckingPositionInPortfolio')
def CheckingPositionInPortfolio():
    positionID =  request.args.get('positionID', 0)
    portfolioName =  request.args.get('portfolioName', 0)
    return jsonify(briefcase_page.CheckingPositionInPortfolio(MWDb, positionID, portfolioName))

#Функция 
@server.route('/SavePortfolio', methods=['POST'])
def SavePortfolio():
    userId = signin_page.GetUserId(MWDb, current_user.id)
    return jsonify(briefcase_page.CreatePortfolio(MWDb, request.get_json(), userId))

#Функция выгрузки портфелей пользователя c позициями
@server.route('/GetMyPortfoliosPositions')
def GetMyPortfoliosPositions():
    userId = signin_page.GetUserId(MWDb, current_user.id)
    return jsonify(data = briefcase_page.GetMyPortfoliosPositions(MWDb, userId))

#Функция выгрузки портфелей пользователя
@server.route('/GetMyPortfolios')
def GetMyPortfolios():
    userId = signin_page.GetUserId(MWDb, current_user.id)
    marketID =  request.args.get('marketID', 0)
    return jsonify(data = briefcase_page.GetMyPortfolios(MWDb, userId, marketID))

#Функция удаления из портфеля какой-либо позиции
@server.route('/RemovePosition')
def RemovePosition():
    idPosition =  request.args.get('idPosition', 0)
    return jsonify(data = briefcase_page.RemovePosition(MWDb, idPosition))

#Функция обновления позиции в портфеле
@server.route('/UpdatePosition', methods=['POST'])
def UpdatePosition():
    position = request.get_json()
    return jsonify(briefcase_page.UpdatePosition(MWDb, position))

#Функция удаления портфеля пользователя
@server.route('/RemovePortfolio')
def RemovePortfolio():
    portfolioID =  request.args.get('portfolioID', 0)
    return jsonify(data = briefcase_page.RemovePortfolio(MWDb, portfolioID))

#Функция выгрузки списока рынков из бд
@server.route('/GetMarketsData')
def GetMarketsData():
    return jsonify(data = markets.GetMarketsData())

@server.route('/GetGraphData')
def GetGraphData():
    ticker =  request.args.get('ticker', 0)
    return jsonify(data = markets.GetGraphData(ticker))
# ------------------------------------------------------------------------------

@login_manager.unauthorized_handler     # In unauthorized_handler we have a callback URL 
def unauthorized_callback():            # In call back url we can specify where we want to 
    return redirect('/')

if __name__ == '__main__':
   server.run()