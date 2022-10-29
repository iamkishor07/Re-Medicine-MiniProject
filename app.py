# save this as app.p
from flask import Flask, g, session, redirect, request, render_template, url_for, send_file
import qrcode as qr
import random
import cv2
import os
import pymongo



client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client["Remedicine"]
users = db["Users"]
medicineData = db["medicineData"]

app = Flask(__name__)

app.secret_key = os.urandom(24)

def retriveData(uid):
    data = []
    data.append(uid["username"])
    data.append(uid["unique_id"])
    data.append(uid["tname"])
    data.append(uid["tDOE"])
    data.append(uid["tDOP"])
    return data

@app.before_request
def before_request():
    g.user = None 
    if 'user' in session:
        g.user = session['user']

@app.route('/')
def start():
    return render_template('home.html')

@app.route("/remed")
def test():
    val=request.args.get("id")
    uid=medicineData.find_one({"unique_id":val})
    if(uid):
        data=retriveData(uid)
        return render_template("ShowMedicineDetails.html",data = data)
    else:

        return redirect(url_for("medicineDetailsForm",msg = "No data found with this QR, Kindly register"))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('login.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    global invalid_user
    if request.method == 'POST':
        session.pop('user',None)
        user_list = users.find_one({"username":request.form['username']})
        # print("3")
        if user_list:
            # print("1")
            if request.form['password'] == user_list['password']:
                # print("2")
                print("if password...",user_list)
                session['user'] = request.form['username']
                print("logged in")
                return render_template('index.html',username=session['user'])
            return render_template('login.html',invalid_user="Invalid Username or Password")
        return render_template('login.html',invalid_user="Invalid Username or Password")
    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    global username_taken_msg
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_list = users.find_one({"username":username})
        if user_list:
            username_taken_msg = "Username already taken, try another one"
            return render_template('register.html',username_taken_msg=username_taken_msg)
        users.insert_one({"username":username,"password":password,"email":email})
        return redirect(url_for("login"))
    return render_template('register.html')




@app.route("/generateQR")
def generateQR():
    return render_template('GenerateQR.html')

@app.route('/createQrcode')
def createQrcode():
    return render_template('GenerateQR.html')

@app.route('/scanQR')
def scanQR():
    return render_template('ScanQR.html')

@app.route('/medicineDetails',methods=["POST"])
def medicineDetails():
    tname=request.form["Tname"]
    tDOP=request.form["TDOP"]
    tDOE=request.form["TDOE"]
    
    medicineData.insert_one({"username":session["user"],"unique_id":id,"tname":tname,"tDOP":tDOP,"tDOE":tDOE})
    return render_template("Successful.html")

@app.route('/medicineDetailsForm')
def medicineDetailsForm():
    return render_template("MedicineDetailsForm.html")


@app.route("/upload",methods=["POST"])
def upload():
    global id
    img=request.files['img'] 
    imgname=img.filename
    path=os.path.join("static/",imgname)
    img.save(path)
    d=cv2.QRCodeDetector()
    value , points , straight_code =d.detectAndDecode(cv2.imread(path))
    id=value.split("=")[1]
    uid=medicineData.find_one({"unique_id":id})
    if(uid):
        data=retriveData(uid)
        return render_template("ShowMedicineDetails.html",data = data)
    else :
        return redirect(url_for('medicineDetailsForm'))


@app.route('/Generate')
def Generate():
    r1= random.randint(1, 1000)
    # qr.add_data("Www.Remidicine.com${}".format(uuid.uuid4()))
    img =qr.make("http://localhost:5000/remed?id={}".format(r1))
                
    # qr.make(fit=True)
    # img = qr.make_image(fill_color="black", back_color="white")
    # print(r1)
    img.save(r"C:\Users\KISHORKUMAR DOPATHI\OneDrive\Desktop\Remedicine\static\kishor{}.jpg".format(r1))
    p=r"C:\Users\KISHORKUMAR DOPATHI\OneDrive\Desktop\Remedicine\static\kishor{}.jpg".format(r1)
    return send_file(p,as_attachment=True)

if __name__ == '__main__':
   app.run(debug = True)