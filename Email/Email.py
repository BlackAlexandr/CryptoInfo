import smtplib, ssl

from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mail_admin = 'team@marketwind.org'
password = 'Marke+.W1nd'

# to - address of new user/recepient
# username - personal name of new account, that his entered
# id - activation code for continue
def SendCodeConfirmAccountEmail(to, username, activation_code):
    result = 'OK'
    try:
        me = mail_admin
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Please confirm your account"
        msg['From'] =  formataddr(str(Header('MarketWind Team', 'utf-8')), me)
        msg['To'] = to

        # Create the body of the message (HTML version).
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hello {}!<br>
              Please, confirm your account. Enter activation code:<br>
              <h2>
              {}
              </h2>.
            </p>
          </body>
        </html>
        """.format(username, activation_code)

        # Record the MIME types of both parts - text/plain and text/html.
        
        msg_html = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(msg_html)

        ssl_context = ssl.create_default_context()
        # Send the message via local SMTP server.
        s = smtplib.SMTP_SSL('smtppro.zoho.com', 465, context=ssl_context)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        # Provide Gmail's login information
        s.login(mail_admin, password)
        s.sendmail(me, to, msg.as_string())
        s.quit()
    except Exception as e: 
        print (str(e))
        result = str(e)

    return result

def SendCodePecoverPasswordEmail(to, username, verification_code):
    result = 'OK'
    try:
        me = mail_admin
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Please confirm your account"
        #msg['From'] = formataddr(str(Header('MarketWind Team', 'utf-8')), me)
        msg['From'] = str(Header('MarketWind Team <{}>')).format(mail_admin)
        msg['To'] = to

        # Create the body of the message (HTML version).
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hello {}!<br>
              Please, enter verification code to recover your password:<br>
              <h2>
              {}
              </h2>.
            </p>
          </body>
        </html>
        """.format(username, verification_code)

        # Record the MIME types of both parts - text/plain and text/html.
        
        msg_html = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(msg_html)

        ssl_context = ssl.create_default_context()
        # Send the message via local SMTP server.
        s = smtplib.SMTP_SSL('smtppro.zoho.com', 465, context=ssl_context)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        # Provide Gmail's login information
        s.login(mail_admin, password)
        s.sendmail(me, to, msg.as_string())
        s.quit()
    except Exception as e: 
        print (str(e))
        result = str(e)

    return result