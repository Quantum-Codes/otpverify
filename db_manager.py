import smtplib, os, dotenv, datetime
import mysql.connector
from email.message import EmailMessage

dotenv.load_dotenv() 

class emailer:
    def __init__(self):
        self.sender = os.environ["email"]

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(self.sender, os.environ["app_password"])

        self.session = s

    def send_mail(self, recipient, message):
        msg = EmailMessage()
        msg['Subject'] = "OTP for simple login"
        msg['From'] = self.sender
        msg['To'] = recipient
        msg.set_content(message, subtype='html')
        self.session.send_message(msg)

    def logout(self):
        self.session.quit()


class database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost", user="root", password="ankit", database="testdb"
        )
        self.sql = self.db.cursor()
        self.dict_sql = self.db.cursor(dictionary=True)

    def add_user(self, user, password, email, otp, session):
        self.sql.execute(
            "INSERT INTO login (username, password, email, otp, verified, session) VALUES (%s, %s, %s, %s, 0, %s);",
            (user, password, email, otp, session),
        )
        self.db.commit()
    
    def get_all_users(self):
        self.sql.execute("SELECT * FROM login;")
        return self.sql.fetchall()
        
    def get_pass(self, username):
        self.sql.execute("SELECT password FROM login WHERE username = %s;", (username,))
        return self.sql.fetchone()[0]
    
    def get_session(self, session):
        self.dict_sql.execute("SELECT username, otp, email, verified, otp_expiry FROM login WHERE session = %s;", (session,))
        res = self.dict_sql.fetchone()
        return res
    
    def get_self(self, username):
        """Retruns password also through email for login purpose only. else use get_session()"""
        self.dict_sql.execute("SELECT username, password, otp, email, verified, otp_expiry FROM login WHERE username = %s;", (username,))
        res = self.dict_sql.fetchone()
        return res
    
    def update_session(self, session, username):
        self.sql.execute("UPDATE login SET session = %s WHERE username = %s;", (session, username))
        self.db.commit()
        
    def delete_session(self, session):
        self.sql.execute("UPDATE login SET session = NULL WHERE session = %s;", (session,))
        self.db.commit()
    
    def update_session(self, username, session, invalidate_otp = False):
        if invalidate_otp:
            self.sql.execute("UPDATE login SET session = %s, otp = NULL, otp_expiry = NULL WHERE username = %s;", (session, username))
        else:
            self.sql.execute("UPDATE login SET session = %s WHERE username = %s;", (session, username))
        self.db.commit()
    
    def verify_user(self, username):
        self.sql.execute("UPDATE login SET verified = 1, otp = NULL, otp_expiry = NULL WHERE username = %s;", (username,))
        self.db.commit()
    
    def set_otp(self, username, otp):
        self.sql.execute("UPDATE login SET otp = %s, otp_expiry = %s WHERE username = %s;", (otp, datetime.datetime.now() + datetime.timedelta(hours=3) , username)) # for some reason, cant pass epoch seconds into TIMESTAMP col
        self.db.commit()