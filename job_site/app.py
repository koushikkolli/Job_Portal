#importing the libraries
from flask import Flask, render_template, request, jsonify, url_for, redirect
import pyrebase
import json
from requests import ConnectionError
import WebScraping_indeed as ind

#initialize the flask app

app = Flask(__name__)

app.debug = True

# firebase configuration from the firebase server
firebaseConfig = {
    "apiKey": "AIzaSyCn9jWEt920Rjnl03EvBDt35Li32RrfVvM",
    "authDomain": "portal-f4e46.firebaseapp.com",
    "databaseURL": "https://portal-f4e46.firebaseio.com",
    "projectId": "portal-f4e46",
    "storageBucket": "portal-f4e46.appspot.com",
    "messagingSenderId": "479478503614",
    "appId": "1:479478503614:web:2b1f774b29883bcdbfa6ef",
    "measurementId": "G-QSPXDJVTCM"
};

#initialising the firebase
firebase = pyrebase.initialize_app(firebaseConfig)

#initialising the firebase auth
auth= firebase.auth()

#initialising the firebase database
db = firebase.database()

#initialise the user data
user_data = {
    "user":None,
    "info":None
}

#initial loading method
@app.route("/")
@app.route("/<msg>")
def home(msg=None):
    return render_template("index.html", msg=msg)

#sign in method for validating users
@app.route("/signin", methods=['GET', 'POST'])
def signin():

    #get the global veriable for assigning the user data
    global user_data

    #check the requests method
    if request.method == 'POST':

        #get the posted values in the form
        data = request.form.to_dict()
        #print("\n\n", data,"\n\n")

        #defined using try for validating exceptions
        try:

            #sign in too firebase with the email and password
            user_data["user"] = auth.sign_in_with_email_and_password(data['email'], data['password'])
            #print("\n\n",user_data["user"]["idToken"],"\n\n")

            #get the user info
            user_data["info"] = auth.get_account_info(user_data["user"]["idToken"])
            #print("\n\n", user_data["info"], "\n\n")

            if (user_data['info']['users'][0]['emailVerified']):
                return jsonify({"result":"success", "url": url_for('search_job')+'succesfully signed in'})

            else:
                raise Exception("[] {'error':{'error':'Manual', 'message':'Please verify email to login'}}")

        #exception for loss of internet connectivity
        except ConnectionError as ce:
            #print("\n\n\tNo network :( \n\n",str(ce),"\n\n")
            return jsonify({"result":"failed", "msg":"Please check the network connection and try again"})

        #exception for if user account validation
        except Exception as e:
            #print("\nIn exception\n",str(e), "\n\n")
            resp = str(e).find(']')
            resp = eval(str(e)[resp+2:])
            #print("\n\n",resp,"\n\n",type(resp),"\n\n")
            return jsonify({"result":"failed", "msg":resp['error']['message'].replace('_'," ")})


@app.route("/searchjob")
@app.route("/searchjob<msg>")
def search_job(msg=None):
    if auth.current_user == None :
        return redirect(url_for('home', msg='login to continue'))

    uname = db.child("users").child(user_data['info']['users'][0]['localId']).child('name').get()
    uname = uname.val()
    return render_template('search_job.html', uname=uname, msg=msg)

@app.route("/logout")
def logout():
    auth.current_user = None
    user_data['user'] = None
    user_data['info'] = None
    return render_template('index.html', msg='you have been succesfully logged out')

@app.route("/get_data")
def get_data():

    if auth.current_user == None :
        return redirect(url_for('home', msg='login to continue'))

    with open('static/data.json', 'r') as read_file:
        data = read_file.read()
        return jsonify(data)

@app.route("/fetch_jobs", methods=['GET', 'POST'])
def fetch_jobs():

    if auth.current_user == None :
        return redirect(url_for('home', msg='login to continue'))

    if request.method == 'POST':
        data = request.form.to_dict()
        fetched_data = ind.prepare_url(key_word=data['job'], where=data['location'])

        if fetched_data.empty:
            return jsonify({"result": "0", "msg":"No jobs found for this choice"})

    return jsonify({"result": "1", "data": fetched_data.to_json()})

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/createAccount", methods=['GET', 'POST'])
def create_account():

    global user_data

    if request.method == 'POST':

        data = request.form.to_dict()

        #print("\n\n"+str(data)+"\n\n")

        try:
            user_data['user'] = auth.create_user_with_email_and_password(data['email'], data['password'])
            user_data['info'] = auth.get_account_info(user_data['user']['idToken'])
            p_data = {
                "name": data["name"],
                "type": data["type"]
            }

            db.child("users").child(user_data['info']['users'][0]['localId']).set(p_data)

            result = auth.send_email_verification(user_data['user']['idToken'])
            return jsonify({"result": "success", "msg":str(result['email'])})

        except ConnectionError as ce:
            #print("\n\n\tNo network :( \n\n",str(ce),"\n\n")
            return jsonify({"result":"failed", "msg":"Please check the network connection and try again"})

        except Exception as e:
            #processing the error
            try:
                emsg = str(e)
                x = emsg.find(']')
                emsg = eval(emsg[x+2:])
                return jsonify({"result": "failed", "msg":str(emsg['error']['message']).replace('_', ' ')})

            except Exception as _e:
                print(str(_e))
                print(str(e))
                return jsonify({"result": "failed", "msg":str(_e).replace('_', ' ')})
