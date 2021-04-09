import os
import datetime
from passlib.hash import sha256_crypt
from flask import Flask, redirect, url_for, session, request, jsonify, Markup, render_template
import json
import pymongo

app = Flask(__name__)

app.config["SECRET_KEY"] = "very_secret_rn"

#client = pymongo.MongoClient("mongodb+srv://myhahaTest:<bruhMoment>@myjaja.9kk5r.mongodb.net/<jaja>?retryWrites=true&w=majority")
#db  = client.get_default_database()
#client = pymongo.MongoClient("mongodb://localhost:27017/")
#db = client["database"]

#userCol = db["users"]

@app.route('/') # home and main
def home():
    with open('jsons/posts.json') as postsLol:
        postList = json.load(postsLol)
    with open('jsons/usrpass.json') as usersLol:
        userList = json.load(usersLol)
    pastPosts = ""

    friendsList = ""
    try:
        if (session["loggedIn"] == True): # Fix this so if cookies show user does not exist, send them to login
            try:
                for x in range(0, len(postList)): # Show all posts
                    for y in range(0, len(userList)):
                        if (userList[y]["username"] == session["username"]):
                            if (postList[x]["name"] == session["username"] or postList[x]["name"] in userList[y]["friends"]):
                                pastPosts += "<div class='post'><a href='/user/" + postList[x]["name"] + "'><b>" + postList[x]["name"] + "</b></a><br><p>" + postList[x]["content"] + "</p></div><br><br>"
                            #else:
                            #    if (postList[x]["name"] in session["friends"]): ####
                            #       pastPosts += "<div class='post'><p><b>" + postList[x]["name"] + "</b></p><button style='width: 75px; height: 30px;' class='addFriend' onclick='return addFriend(" + "\"" + postList[x]["name"] + "\"" + ")'>Add Friend</button><p>" + postList[x]["content"] + "</p></div><hr><br><br>"
                for i in range(0, len(userList)):
                    if (userList[i]["username"] == session["username"]):
                        for j in range(0, len(userList[i]["friends"])):
                            friendsList += "<a class='friend' href='/user/" + userList[i]["friends"][j] + "'>" + userList[i]["friends"][j] + "</a>    <button class='removeFriend' onclick='return removeFriend(" + "\"" + userList[i]["friends"][j] + "\"" + ")'>Remove</button><hr>"

                return render_template('index.html', dib = Markup(pastPosts), logged_in = Markup("<p>Welcome to MyHaha, " + session["username"] + "! <a href='/signout'>Sign Out</a></p>"), da_form = Markup("<form id='forma' action='/posted' method='POST'><textarea id='postBox' name='postContent' style='width:100%; height:100%;' placeholder='Make a post...'></textarea><input class='postbutton' type='submit' value='Post' style='width=20px; height=15px;'></form>"), friends = Markup(friendsList))
            except:
                return redirect('/login')
        else:
            return redirect('/login')
    except:
        return redirect('/login')

    #else:
    #    return render_template('index.html', dib = Markup(pastPosts), logged_in = Markup("<p>Welcome to MyHaha, " + session["username"] + "!</p>"))

@app.route("/addFriend/<person>") # the bit thats called when you click the add freind button
def addFriend(person):
    personToAdd = str(person)
    with open("jsons/usrpass.json") as user_list:
        users = json.load(user_list) #finish this (?)
    whole = users
    currentUser = session["username"]
    userInList = 0
    for userNum in range (0, len(users)):
        if (users[userNum]["username"] == currentUser):
            userInList = userNum
            break
    session["friends"].append(personToAdd)
    print(session["friends"])
    whole[userInList]["friends"].append(personToAdd)
    with open("jsons/usrpass.json", 'w') as out:
        json.dump(whole, out)
    return redirect('/')

@app.route("/removeFriend/<person>") # same as add friend but remove
def removeFriend(person):
    personToRemove = str(person)
    with open("jsons/usrpass.json") as user_list:
        users = json.load(user_list)
    whole = users
    currentUser = session["username"]
    userInList = 0
    for userNum in range (0, len(users)):
        if (users[userNum]["username"] == currentUser):
            userInList = userNum
    #session["friends"].remove(personToRemove)
    whole[userInList]["friends"].remove(personToRemove)
    with open("jsons/usrpass.json", 'w') as out:
        json.dump(whole, out)
    return redirect('/')


@app.route('/signup') # the bit that shows you the actual page to sign up on
def sign_up():
    return render_template('/signup.html')

# the bit thats called when you click the sign up button (yes passwords are encrypted)
@app.route('/signed', methods=["POST"])
def register():
    with open('jsons/usrpass.json') as userInfo:
        currentUsers = json.load(userInfo)

    # wholeThing = currentUsers
    userUser = request.form['userField']
    userPswd = request.form['passwField']
    userConfirm = request.form['confirmPassw']
    if (userPswd != userConfirm):
        return render_template('/signup.html', signup_failed = Markup("<p style='color: #fff;'>Passwords are not the same, please try again."))

    query = {"username": userUser}
    theReturn = userCol.find(query)
    length = theReturn.count()

    #for user in range (0, len(currentUsers)): # error stuff
    if ():
        return render_template('/signup.html', signup_failed = Markup("<p style='color: #fff;'>Username already exists. Please select a different username</p>"))

    key = sha256_crypt.hash(userPswd) # the actual bit that encrypts your stuff
    print(key)
    arrivedUser = {"username": userUser, "password": str(key), "friends": [], "bio": ""}
    x = userCol.insert_one(arrivedUser)
    print(x)
    #with open ('jsons/usrpass.json', 'w') as out:
    #    json.dump(wholeThing, out)
    #return redirect('/login')

@app.route('/posted', methods=["POST"]) # posting function
def post():
    with open('jsons/posts.json') as theIn:
        jsInput = json.load(theIn)
    whole = jsInput
    post = {}
    post["name"] = session["username"]
    post["content"] = request.form["postContent"]
    if (request.form["postContent"] == ""):
        return redirect('/')
    elif (len(request.form["postContent"]) >= 256):
        return redirect('/')
    whole.append(post)
    with open('jsons/posts.json', 'w') as out:
        json.dump(whole, out)
    return redirect('/')

@app.route('/login') # displays the login webpage
def login():
    return render_template('login.html', login_failed = "")

# login function where passwords are encrypted as well
@app.route('/sign', methods=["POST"])
def login_check():
    with open('jsons/usrpass.json') as login_info:
        details = json.load(login_info)
    userUser = request.form['userField']
    userPswdBase = request.form['passwField']
    userPswd = sha256_crypt.hash(userPswdBase) # encryption!
    newUser = True
    ustr = False
    usrps = False
    usrFrnd = []
    for user in range (0, len(details)):
        if (userUser == details[user]["username"]):
            ustr = True
            if (sha256_crypt.verify(userPswdBase, details[user]["password"]) == True):
                usrps = True
                usrFrnd = details[user]["friends"]
                if (details[user]["bio"] != ""):
                    newUser = False
                break
    if (ustr == True and usrps == True):
        session["loggedIn"] = True
        session["username"] = userUser
        session["friends"] = usrFrnd
        if (newUser == True):
            return redirect("/create/False")
        else:
            return redirect("/")
    else:
        return render_template('login.html', login_failed = Markup("<p style='color: #fff;'>Either your username or password is incorrect. Please try again</p>"))

@app.route('/signout') # self explanatory
def sign_out():
    session.clear()
    return redirect('/')

@app.route("/create/<error>") # bio creation page handler thing
def create_profile(error):
    if (error == True):
        return render_template("create.html", bio_error = "Your bio is too long, please shorten it.")
    return render_template("create.html", bio_error="")

@app.route("/done", methods=["POST"]) # the actual stuff that controls bio creation
def profile_done():
    if (len(request.form["bio"]) >= 650):
        return redirect("/create/True")
    else:
        with open ("jsons/usrpass.json") as user_info:
            userInfo = json.load(user_info)
        whole = userInfo
        user = session["username"]
        for x in range(0, len(whole)):
            if (whole[x]["username"] == user):
                whole[x]["bio"] = request.form["bio"]
                break
        with open ("jsons/usrpass.json", 'w') as out:
            json.dump(whole, out)

        return redirect("/")

@app.route('/user/<username>') # profile handler
def profile(username):
    with open ("jsons/usrpass.json") as user_info:
        userInfo = json.load(user_info)

    for x in range (0, len(userInfo)):
        if (userInfo[x]["username"] == username):
            daUserBio = userInfo[x]["bio"]

    if username not in session["friends"]:
        return render_template("profileLayout.html", profile_name = username, profile_bio = daUserBio, add_friend_button = Markup("<button style='width: 75px; height: 30px;' class='addFriend' onclick='return addFriend(" + "\"" + username + "\"" + ")'>Add Friend</button>"))
    else:
        return render_template("profileLayout.html", profile_name = username, profile_bio = daUserBio, add_friend_button = Markup("""<!-- -->"""))

    #return render_template("profileLayout.html", profile_name = username, profile_bio = daUserBio)

@app.route('/search', methods=["POST"])
def prof_search():
    prevSearch = request.form['old_search']
    print(prevSearch)
    with open ("jsons/usrpass.json") as user_info:
        users = json.load(user_info)

    foundUsers = ""

    for user in users:
        if (prevSearch == user["username"]):
            return redirect("/profile/" + user["username"])
        else:
            if (prevSearch.upper() == user["username"].upper()):
                foundUsers += "<a class='friend' href='/user/" + user["username"] + "'><b>" + user["username"] + "</b></a><br>"

    if (len(foundUsers) != 0):
        return render_template("search.html", el_searcho = Markup("""<input name="old_search" placeholder= {{ old_search }} class="Rectangle_1 textBox">
                <input type="submit" value="search" class="Rectangle_3"></input>"""), listed_users = Markup(foundUsers))
    else:
        return render_template("search.html", el_searcho = Markup("""<input name="old_search" placeholder= {{ old_search }} class="Rectangle_1 textBox">
                <input type="submit" value="search" class="Rectangle_3"></input>"""), listed_users = Markup("<a class='friend'><b>No users found by that name. Make sure you typed the name correctly.</b></a>"))

if (__name__ == '__main__'):
    app.run(debug=True, port=12121)
