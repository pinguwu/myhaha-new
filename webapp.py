import os
import hashlib
from flask import Flask, redirect, url_for, session, request, jsonify, Markup, render_template
import json

app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_rn"

salt = os.urandom(32)


@app.route('/')
def home():
    with open('jsons/posts.json') as postsLol:
        postList = json.load(postsLol)
    with open('jsons/usrpass.json') as usersLol:
        userList = json.load(usersLol)
    pastPosts = ""

    try:
        if (session["loggedIn"] == True):
            try:        
                for x in range(0, len(postList)):
                    for y in range(0, len(userList)):
                        if (userList[y]["username"] == session["username"]):
                            if (postList[x]["name"] == session["username"] or postList[x]["name"] in userList[y]["friends"]):
                                pastPosts += "<div class='post'><p><b>" + postList[x]["name"] + "</b></p><p>" + postList[x]["content"] + "</p></div><br><br>"
                            else:
                                pastPosts += "<div class='post'><p><b>" + postList[x]["name"] + "</b></p><button class='addFriend' onclick='return addFriend(" + "\"" + postList[x]["name"] + "\"" + ")'>Add Friend</button><p>" + postList[x]["content"] + "</p></div><br><br>"
                return render_template('index.html', dib = Markup(pastPosts), logged_in = Markup("<p>Welcome to MyHaha, " + session["username"] + "! <a href='/signout'>Sign Out</a></p>"), da_form = Markup("<form action='/posted' method='POST'><input name='postContent' style='width:20%; height:20px;' placeholder='Make a post...'></input><input type='submit' value='Post'></form>"))   
            except:
                return render_template('index.html', dib = "", logged_in = Markup("<p>You are not logged in. Please log in <a href='/login'>here</a></p>"))
        else:
            return render_template('index.html', dib = "", logged_in = Markup("<p>You are not logged in. Please log in <a href='/login'>here</a></p>"))
    except:
        return render_template('index.html', dib = "", logged_in = Markup("<p>You are not logged in. Please log in <a href='/login'>here</a></p>"))
    
    #else:
    #    return render_template('index.html', dib = Markup(pastPosts), logged_in = Markup("<p>Welcome to MyHaha, " + session["username"] + "!</p>"))

@app.route("/addFriend/<person>")
def addFriend(person):
    personToAdd = str(person)
    with open("jsons/usrpass.json") as user_list:
        users = json.load(user_list) #finish this
    whole = users
    currentUser = session["username"]
    userInList = 0
    for userNum in range (0, len(users)):
        if (users[userNum]["username"] == currentUser):
            userInList = userNum
            break
    whole[userInList]["friends"].append(personToAdd)
    with open("jsons/usrpass.json", 'w') as out:
        json.dump(whole, out)
    return redirect('/')

@app.route('/signup')
def sign_up():
    return render_template('/signup.html')

@app.route('/signed', methods=["POST"])
def register():
    with open('jsons/usrpass.json') as userInfo:
        currentUsers = json.load(userInfo)
    wholeThing = currentUsers
    userUser = request.form['userField']
    userPswd = request.form['passwField']

    for user in range (0, len(currentUsers)):
        if (userUser == currentUsers[user]["username"]):
            return render_template('/signup.html', signup_failed = Markup("<p>Username already exists. Please select a different username"))
    key = hashlib.pbkdf2_hmac (
        'sha256',
        userPswd.encode('utf-8'),
        salt,
        100000
    )
    wholeThing.append({"username": userUser, "password": str(key), "friends": []})
    with open ('jsons/usrpass.json', 'w') as out:
        json.dump(wholeThing, out)
    return redirect('/login')

@app.route('/posted', methods=["POST"])
def post():
    with open('jsons/posts.json') as theIn:
        jsInput = json.load(theIn)
    whole = jsInput
    post = {}
    post["name"] = session["username"]
    post["content"] = request.form["postContent"]
    whole.append(post)
    with open('jsons/posts.json', 'w') as out:
        json.dump(whole, out)
    return redirect('/')

@app.route('/login')
def login():
    return render_template('login.html', login_failed = "")

@app.route('/sign', methods=["POST"])
def login_check():
    with open('jsons/usrpass.json') as login_info:
        details = json.load(login_info)
    userUser = request.form['userField']
    userPswdBase = request.form['passwField']
    userPswd = hashlib.pbkdf2_hmac (
        'sha256',
        userPswdBase.encode('utf-8'),
        salt,
        100000
    )

    ustr = False
    usrps = False
    usrFrnd = []
    for user in range (0, len(details)):
        if (userUser == details[user]["username"]):
            ustr = True
            if (str(userPswd) == details[user]["password"]):
                usrps = True
                usrFrnd = details[user]["friends"]
                break
    if (ustr == True and usrps == True):
        session["loggedIn"] = True
        session["username"] = userUser
        session["friends"] = usrFrnd
        return redirect("/")
    else:
        return render_template('login.html', login_failed = "Either your username or password is incorrect. Please try again.")

@app.route('/signout')
def sign_out():
    session.clear()
    return redirect('/')

if (__name__ == '__main__'):
    app.run(debug=True, port=12121)
