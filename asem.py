from flask import Flask 
from flask import render_template, request, redirect, url_for, flash
from ipaddress import IPv4Address  # for your IP address
from pyairmore.request import AirmoreSession  # to create an AirmoreSession
from pyairmore.services.messaging import MessagingService  # to send messages
# from openpyxl import load_workbook
import time
import os

app = Flask(__name__)

#a path should be provided here:
app.config["FILE_UPLOADS"] = str(r"C:\Users\hp\Documents\BulkSMS\uploads")
app.secret_key = os.urandom(12)
ALLOWED_EXTS = {"txt", "csv", "xlsc"}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/connect', methods = ['POST'])
def connect():
    ip = IPv4Address("192.168.183.22")  # let's create an IP address object
# now create a session
    session = AirmoreSession(ip)
# if your port is not 2333
# session = AirmoreSession(ip, 2333)  # assuming it is 2334

    was_accepted = session.request_authorization()
    if was_accepted:
        flash("Connected Successfully!")
        service = MessagingService(session)
        def sendSms(telephone, message):
            service.send_message(telephone, message)

        return render_template("index.html")
    else:
        flash("Please open your airmore app on your mobile.")
        return "Not connected!"



@app.route('/send', methods = ['POST'])
def send():
    if request.method == 'POST':
        if request.files:

            file_list = request.files['list']

            path = os.path.join(app.config["FILE_UPLOADS"], file_list.filename)

            file_list.save(os.path.join(app.config["FILE_UPLOADS"], file_list.filename))


    fh = open(path,'r')
    topic = request.form.get("topic")
    meet = request.form.get("meetLink")
    when = request.form.get("time")
    aspace = request.form.get("as")
    sign = request.form.get("sign")
    message = request.form.get("message") + "\n" + topic + "\n: "+when+"\n"+meet +"\n"+ sign + "\n" + aspace

    if not topic or not meet or not time or not message or not sign:
        return "failure"
    
    else:
        txtfh = fh.read()
        uniqlist = []
        ip = IPv4Address("192.168.183.22")
        session = AirmoreSession(ip)
        service = MessagingService(session)
        def sendSms(telephone, message):
             return service.send_message(telephone, message)
        def namesep(firstName):
            return firstName.split(" ")[0]

        def format(phone):
	        cln = phone.replace(" ","").replace("-","")
	        if (cln.startswith("251")):
		        return "+"+cln
	        elif (cln.startswith("9")):
		        return "0"+cln
	        else:
		        return cln
        for i in txtfh.split('\n'):
	        if i in uniqlist:
		        pass
	        else:
		        uniqlist.append(namesep(i.split(",")[0])+","+format(i.split(",")[-1]))
        
        for i in uniqlist:
            msg = "Dear "+i.split(",")[0]+",\n"+message
            number = str(i.split(",")[1])
            content = "Send to: " + i
            sendSms(number,msg)
            time.sleep(1)

        flash("Congratulations! You sent an invitation.")
        return render_template("success.html", content = content)

app.run(debug = True) 
