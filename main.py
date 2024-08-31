from flask import Flask, render_template, redirect, request, make_response
import db_manager
import random

app = Flask(__name__)
emailer = db_manager.emailer()
db = db_manager.database()

# could have put this in a file
message = """
<html><head>
    <style>
    #otpbody {
        width: 60%;
        margin: auto;
        height: 4em;
        font-size: 2em;
    }
    #header, #content {
        height: 50%;
        text-align: center;
        line-height: 2em;
    }

    #header {
        background: lightblue;
    }
    #content {
        background: black;
        color: white;
    }</style>
</head><body>
    <div id="otpbody">
        <div id="header">
            Simple Login
        </div>
        <div id="content">
            Your OTP is: [otp]
        </div>
    </div>
</body></html>
"""

def respond(page, cookies, template = False):
    if template:
        resp = render_template(page)
    else:
        resp = make_response(redirect(page))

    for cookie in cookies:
        resp.set_cookie(key=cookie["key"], value=cookie["value"], max_age=cookie["expires"])

    return resp

def otpgen():
    return random.randint(1000, 9999)

def sessiongen():
    return str(random.randint(10000, 99999))
    


@app.route("/")
def indexpage():
    if not request.cookies.get("session"):
        return "You arent logged in.. <br><a href = '/login'>Login</a> or <a href = '/signup'>Signup</a>"
    
    user = db.get_session(request.cookies.get("session"))
    if not user:
        return respond("/login", [{"key":"session", "value":"", "expires":0}])
        
    return render_template("main.html", user = user, userlist = db.get_all_users())


@app.route("/signup", methods=["POST", "GET"])
def signuppage():
    if request.method == "POST":
        if not (
            request.form.get("username")
            and request.form.get("pass")
            and request.form.get("email")
        ):
            return "fill it properly"

        session = sessiongen()
        db.add_user(
            request.form["username"].lower().strip(),
            request.form["pass"],
            request.form["email"].lower().strip(),
            otpgen(),  # otp
            session,
        )
        return respond(
            "/",
            [{"key": "session", "value": session, "expires": 7 * 24 * 3600}],
        )

    return render_template("login.html", aim="signup", msg=None)

@app.route("/login", methods=["POST", "GET"])
def loginpage():
    if request.method == "POST":
        if not (
            request.form.get("username")
            and request.form.get("pass")
        ):
            return "fill it properly"
        
        username = request.form.get("username").lower().strip()
        user = db.get_self(username) # return None if no user exists
        if not user:
            return "wrong username"
        saved_pass = user["password"]
        if request.form["pass"] != saved_pass:
            return "wrong password"
        
        if user["verified"] == 1:
            otp = otpgen()
            db.set_otp(user["username"], otp)
            return respond("/otpverify", [{"key": "otp", "value": username, "expires": 3*3600}])
        else:
            # if email not verified even once then ignore 2fa
            session = str(random.randint(10000, 99999))
            db.update_session(username, session)
            return respond(
                "/",
                [{"key": "session", "value": session, "expires": 7 * 24 * 3600}],
            )

    return render_template("login.html", aim="login", msg=None)


@app.route("/logout")
def logoutpage():
    session = request.cookies.get("session")
    if session:
        db.delete_session(session)
        return respond("/login", [{"key":"session", "value":"", "expires":0}, {"key":"otp", "value":"", "expires":0}])
    
@app.route("/otpverify", methods = ["GET", "POST"])
def otpverify():
    if not request.cookies.get("otp"):
        if not request.cookies.get("session"):
            return redirect("/login")
        
    user = db.get_session(request.cookies.get("session"))
    if not user:
        if not request.cookies.get("otp"):
            return respond("/login", [{"key":"session", "value":"", "expires":0}])
        user = db.get_self(request.cookies.get("otp"))
    
    if request.method == "GET":
        print(user["otp_expiry"], type(user["otp_expiry"]))
        emailer.send_mail(user["email"], message.replace("[otp]", str(user["otp"])))
        return render_template("otpverify.html")
    else:
        if user["otp"] == int(request.form["otp"]):
            if user["verified"] == 0:
                db.verify_user(user["username"])
                return "your email is verified. enabled 2FA.<br>Go to <a href='/'>mainpage</a>"
            else:
                session = sessiongen()
                db.update_session(user["username"], session)
                return respond(
            "/",
            [{"key": "session", "value": session, "expires": 7 * 24 * 3600}, {"key":"otp", "value":"", "expires":0}],
        )
        else:
            return "wrong otp"

app.run("0.0.0.0", port=8080)
