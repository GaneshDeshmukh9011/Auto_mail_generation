from flask import Flask,render_template,request,redirect,session,send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date,time
import pandas as pd
import os
import sys
from docxtpl import DocxTemplate
import smtplib
from smtplib import SMTPAuthenticationError
import ssl
from email.message import EmailMessage
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import base64
from sqlalchemy import LargeBinary
from docx import Document
import markdown
from werkzeug.utils import secure_filename
from flask_executor import Executor
import sqlite3
import pyotp
import random
import tkinter as tk
from tkinter import messagebox
import requests
import shutil




app=Flask(__name__)
app.secret_key = "login"
db_folder = os.path.abspath('D:/flask_practice1/flask_practice/instance')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_folder}/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



executor=Executor(app)
class Notices_details(db.Model):
    SNO=db.Column(db.Integer,primary_key=True)
    year=db.Column(db.String(15))
    title=db.Column(db.String(200),nullable=False)
    desc=db.Column(db.String(500),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    excel = db.Column(db.String(200))
    word = db.Column(db.String(200))
    status=db.Column(db.Integer)
    generate=db.Column(db.Integer)
    send_mail=db.Column(db.Integer)
    
    
class Database(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    role=db.Column(db.String(15),nullable=False)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    branch=db.Column(db.String(20))
    email=db.Column(db.String(50))

class Generate(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    year = db.Column(db.String(500), nullable=False)
    notify=db.Column(db.Integer)
    date=db.Column(db.String(20))
    


with app.app_context():
   db.create_all()


subject = "Regarding Checking Generated Notices"
email_password = ''
email_receiver=''

email_sender1 = ''

email_receiver1=''
em1 = MIMEMultipart()
em1['Subject'] = subject
em1['From'] = email_sender1
em1['To'] =email_receiver
body={}
UPLOAD_FOLDER=None
otp=None




def check_internet():
    try:
        requests.get('http://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False



@app.route("/admin",methods=['GET','POST'])
def index():
    
    if check_internet():


        if not session.get('a_logged-in'):
            return render_template("login.html")
        global UPLOAD_FOLDER
        if request.method=='POST':
            title=request.form['class']
            desc=request.form['branch']
            excel1=request.files['excel']
            word1=request.files['word']
            excel=excel1.filename
            word=word1.filename
            year=request.form['year']
            allNotices_detailss=Notices_details.query.all()
            allNotices_detailss1=Database.query.filter_by().first()
            j=1
            for i in allNotices_detailss:
                if i.title==title and i.desc==desc and i.year==year:
                    j=0
                    break

            if j==0:
                allNotices_detailss = Notices_details.query.all()
                msg4=0
                if not allNotices_detailss:
                    msg4=1
                if msg4==1:
                    username=session.get('a_username')
                    f_letter=username[0].upper()
                    return render_template('index.html',msg4=msg4,username=username,f_letter=f_letter)
                else:
                    username=session.get('a_username')
                    f_letter=username[0].upper()
                    return render_template('index.html',allNotices_detailss=allNotices_detailss,username=username,f_letter=f_letter,msg=1)
            else:
                UPLOAD_FOLDER = f"D:/flask_practice1/flask_practice/{year}/{title}/uploads"
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

                UPLOAD_FOLDER1 = f"D:/flask_practice1/flask_practice/{year}/{title}/uploads"
                app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1

               
                if word1.filename == '':
                    return "No selected file"

                if word1:
                    
                    branch_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], desc)
                    if not os.path.exists(branch_upload_folder):
                        os.makedirs(branch_upload_folder)

                    file_path = os.path.join(branch_upload_folder, word1.filename)
                    word1.save(file_path)


                if excel1.filename == '':
                    return "No selected file"

                if excel1:
                    branch_upload_folder1 = os.path.join(app.config['UPLOAD_FOLDER1'], desc)
                    if not os.path.exists(branch_upload_folder1):
                        os.makedirs(branch_upload_folder1)

                    file_path1 = os.path.join(branch_upload_folder1, excel1.filename)
                    excel1.save(file_path1)

                Notices_details1=Notices_details(year=year,title=title, desc=desc, excel=excel, word=word)

                db.session.add(Notices_details1)
                db.session.commit()
                generate=Generate(title=title,desc=desc,year=year)
                db.session.add(generate)
                db.session.commit()
                msg1=1
                return redirect("/display")
        return redirect("/display")    
    return render_template("no_network.html")





@app.route("/send_mail/<int:SNO>")
def send_mail(SNO):

    if check_internet():


        if not session.get('a_logged-in'):
            print("hello")
            return render_template("login.html")
        global email_password
        i=0
        j=0
        
        email=session.get('email')
        Notices_detail=Notices_details.query.filter_by(SNO=SNO).first()
        generate1=Generate.query.filter_by(title=Notices_detail.title,desc=Notices_detail.desc,year=Notices_detail.year).first()
        
        if Notices_detail.status==1:
            df=pd.read_excel(f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/uploads/{Notices_detail.desc}/{Notices_detail.excel}")
            word_files_list = os.listdir(f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/Notices/{Notices_detail.desc}/{generate1.date}")
            for value in df['pending fees']:
                if value>=50000 and value<100000:
                    found=0
                    for file in word_files_list:
                        if df.at[j,"Name"]==os.path.splitext(file)[0]:
                            found=1
                            break
                    if found==1:
                        email_receiver=df.at[j, 'email_address']



                        subject = 'Urgent: Notice of Pending Tuition Fees'
                        body = 'Please find the attached Word file.'

                        
                        em = MIMEMultipart()
                        em['From'] = email_sender1
                        em['To'] = email_receiver
                        em['Subject'] = subject
                        

                        attachment_path=f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/Notices/{Notices_detail.desc}/{generate1.date}/{df.loc[j, 'Name']}.pdf"

                        attachment = open(attachment_path, 'rb')
                        # word_attachment = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
                        word_attachment = MIMEBase('application', 'octet-stream')
                        word_attachment.set_payload(attachment.read())
                        encoders.encode_base64(word_attachment)
                        word_attachment.add_header('Content-Disposition', f'attachment; filename={df.loc[j, 'Name']}.pdf')
                        em.attach(word_attachment)

                            # Attach the body of the email
                        em.attach(MIMEText(body, 'plain'))
                        

                        
                        

                        context = ssl.create_default_context()

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                            #smtp.starttls()
                            smtp.login(email_sender1, email_password)
                            smtp.sendmail(email_sender1, email_receiver, em.as_string())
                        i=i+1
                j=j+1
            Notices_detail.send_mail=1
            db.session.commit()

            return redirect("/display")
        status="Not Checked"
        sno=1
        return redirect('/display')
    
    return render_template("no_network.html")



@app.route("/filter",methods=['GET','POST'])
def filter():
    print("Hello")
    if check_internet():
        if not session.get('a_logged-in'):
            return render_template("login.html")
        if request.method=='POST':
            Notices_detail=None
            class1=request.form.get('class')
            branch=request.form.get('branch')
            year=request.form.get('year')
            username=session.get('a_username')
            f_letter=username[0].upper()
            allNotices_detailss = Notices_details.query.all()

            if class1=="" and branch=="" and year=="":
               
                msg4=0
                if not allNotices_detailss:
                    msg4=1
                if msg4==1:
                    username=session.get('a_username')
                    f_letter=username[0].upper()
                    return render_template('index.html',msg4=msg4,username=username,f_letter=f_letter)
                else:
                    username=session.get('a_username')
                    f_letter=username[0].upper()
                    return render_template('index.html',allNotices_detailss=allNotices_detailss,username=username,f_letter=f_letter,msg7=1)
                
            if class1 and branch and year:
                Notices_detail=Notices_details.query.filter_by(title=class1,desc=branch,year=year).all()

            elif class1 and branch:
                Notices_detail=Notices_details.query.filter_by(title=class1,desc=branch).all()

            elif class1 and year:
                Notices_detail=Notices_details.query.filter_by(title=class1,year=year).all()

            elif year and branch:
                Notices_detail=Notices_details.query.filter_by(year=year,desc=branch).all()

            elif class1:
                Notices_detail=Notices_details.query.filter_by(title=class1).all()
            
            elif branch:
                Notices_detail=Notices_details.query.filter_by(desc=branch).all()
            
            elif year:
                Notices_detail=Notices_details.query.filter_by(year=year).all()


            if not Notices_detail:
                msg=1
                username=session.get('a_username')
                f_letter=username[0].upper()
                return render_template('index.html',allNotices_detailss=allNotices_detailss,username=username,f_letter=f_letter,msg7=1)
            msg=1
            return render_template("index.html",allNotices_detailss=Notices_detail,msg5=msg,username=username,f_letter=f_letter)
        return redirect("/display")
    return render_template("no_network.html")


@app.route("/display")
def display():
    if not session.get('a_logged-in'):
        return render_template("login.html")
    
    allNotices_detailss = Notices_details.query.all()
    msg4=0
    if not allNotices_detailss:
        msg4=1
    if msg4==1:
        username=session.get('a_username')
        f_letter=username[0].upper()
        return render_template('index.html',msg4=msg4,username=username,f_letter=f_letter)
    else:
        username=session.get('a_username')
        f_letter=username[0].upper()
        return render_template('index.html',allNotices_detailss=allNotices_detailss,username=username,f_letter=f_letter)


@app.route("/login3")
def login3():
    return render_template("login.html")

@app.route("/delete/<int:SNO>")
def delete(SNO):
    if not session.get('a_logged-in'):
        return render_template("login.html")
    Notices_detail=Notices_details.query.filter_by(SNO=SNO).first()
    
    db.session.delete(Notices_detail)
    db.session.commit()
    generate=Generate.query.filter_by(sno=SNO).first()
    db.session.delete(generate)
    db.session.commit()
    
    
    folder_path = f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/uploads/{Notices_detail.desc}"

    files = os.listdir(folder_path)

    for file in files:
        file_path = os.path.join(folder_path, file)
        
        if os.path.isfile(file_path):
            
            os.remove(file_path)
           
    return redirect("http://127.0.0.1:5000/display")



@app.route("/delete1/<int:sno>")
def delete1(sno):
    if not session.get('a_logged-in'):
        return render_template("login.html")
    database=Database.query.filter_by(sno=sno).first()
    if database:
        db.session.delete(database)
        db.session.commit()
        return redirect("/dashboard")
    return redirect("/dashboard")

sno1=0
@app.route("/edit/<int:sno>")
def edit(sno):
    global sno1
    sno1=sno
    return redirect("/edit")

@app.route("/edit")
def edit1():
    return render_template("register.html",msg8=1,msg333=1)

@app.route("/update",methods=['GET','POST'])
def update():
    global sno1
    if request.method=="POST":
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']
        database=Database.query.filter_by(sno=sno1).first()
        database.title=username
        database.desc=password
        database.email=email
        db.session.commit()
        return redirect("/dashboard")
    



ind=None
@app.route("/notices/<int:SNO>")
def notices(SNO):
    if not session.get('a_logged-in'):
        return render_template("login.html")
    

    global email_sender
    global email_password
    global email_receiver
    global body
    global em
    global subject
    global ind
    Notices_detail=Notices_details.query.get(SNO)
    folder_path=f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/Notices/{Notices_detail.desc}/{date.today()}"
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    
    os.makedirs(folder_path)
    fname2=f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/uploads/{Notices_detail.desc}/{Notices_detail.word}"
    df=pd.read_excel(f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/uploads/{Notices_detail.desc}/{Notices_detail.excel}")
    os.chdir(f"D:/flask_practice1/flask_practice/{Notices_detail.year}/{Notices_detail.title}/Notices/{Notices_detail.desc}/{date.today()}")
    name = df["Name"].values
    id = df["roll_no"].values
    branch = df["branch"].values
    year = df["year"].values
    pending_fees = df["pending fees"].values

    zipped = zip(name, id, branch, year, pending_fees)
    file_name = []

    for a, b, c, d, e in zipped:
        if 50000 <= e < 100000:
            doc=DocxTemplate(fname2)

            context = {"student_name": a, "student_id": b, "branch": c, "year": d, "pending_fees": e}
            doc.render(context)
            doc.save('{}.docx'.format(f"{a}"))
            file_name.append(f"{a}")
            ind=1
    Notices_detail.generate=1
    db.session.commit()
    generate=Generate.query.filter_by(title=Notices_detail.title,desc=Notices_detail.desc,year=Notices_detail.year).first()
    generate.date=date.today()
    db.session.commit()


    body[Notices_detail.title]=Notices_detail.desc

    
    

    return redirect("/display")

@app.route("/notify",methods=['GET','POST'])
def notify():
    # for i in body:
    #     body1+=f"{body[]}"
    if not session.get('a_logged-in'):
        return render_template("login.html")
    if request.method=='POST':
        
        global email_sender1
        global email_password
        global email_receiver
        global body
        
        
        global subject
        i=1
        generate1=Generate.query.all()
        length=len(generate1)
        for i in generate1:
            body1=""
            text_part=""
            context=None
            em=None
            notices_detail=Notices_details.query.filter_by(title=i.title,desc=i.desc,year=i.year).first()
            if notices_detail.status!=1:
                body1=f"""Check the following notices-\n{i.title}->{i.desc}->{i.date}\n"""
                text_part = MIMEText(body1, 'plain')
                database=Database.query.filter_by(branch=i.desc).first()
                if database:
                    em = MIMEMultipart()
                    em['Subject'] = subject

                    em.attach(text_part)
                    context = ssl.create_default_context()
                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                            smtp.login(email_sender1, email_password)
                            smtp.sendmail(email_sender1, database.email, em.as_string())
                        pass
                    except smtplib.SMTPServerDisconnected as e:
                        print("SMTP server disconnected unexpectedly:", e)
                        allNotices_details=Notices_details.query.all()
                        username=session.get('a_username')
                        f_letter=username[0].upper()
                        return render_template("index.html",msg666=1,allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
                            
                    except Exception as e:
                        allNotices_details=Notices_details.query.all()
                        username=session.get('a_username')
                        f_letter=username[0].upper()
                        return render_template("index.html",msg3=1,allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
                            
                else:
                    allNotices_details=Notices_details.query.all()
                    username=session.get('a_username')
                    f_letter=username[0].upper()
                    return render_template("index.html",msg444=1,branch=i.desc,allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
                

    allNotices_details=Notices_details.query.all()
    username=session.get('a_username')
    f_letter=username[0].upper()
    return redirect("/display")



@app.route('/')
def hello_world():
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('email', None)
    if session.get('a_logged-in'):
        session['a_logged-in']=False
    elif session.get('v_logged-in'):
        session['v_logged-in']=False

    return render_template("login.html")
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if check_internet():
        if request.method == 'POST':
            if 'username' in request.form and 'password' in request.form:
                username = request.form["username"]
                password = request.form["password"]
                role = request.form["role"]
                # Notices_details=Database(title=username,desc=password,role=role,email=email_sender1)
                # db.session.add(Notices_details)
                # db.session.commit()
                allNotices_details=Database.query.all()
                for i in allNotices_details:
                    if role=='Admin':
                        if i.title==username and i.desc==password and i.role=='Admin':
                            session['email'] = i.email
                            # session['password']=i.password
                            session['a_username']=i.title
                            session['username']=i.title
                            username=session.get('a_username')
                            f_letter=username[0].upper()
                            session['a_logged-in']=True
                            msg=None
                            return redirect('/display')
                    elif role=='Verifier':
                        if i.title==username and i.desc==password and i.role=='Verifier':
                            session['email']= i.email
                            # session['password']=i.password
                            session['v_username']=i.title
                            username=session.get('v_username')
                            session['username']=i.title
                            f_letter=username[0].upper()
                            session['v_logged-in']=True
                            msg1=None
                            return redirect("/verifier")
                        
            msg = "Invalid username/password"
            return render_template("login.html", msg=msg)

        return render_template("login.html")
    return render_template("no_network.html")

@app.route("/verifier")
def verifier():
    if not session.get('v_logged-in'):
        return render_template("login.html")
    username=session.get('v_username')
    f_letter=username[0].upper()
    return render_template("index1.html",username=username,f_letter=f_letter)
    


@app.route("/register",methods=['GET','POST'])
def register():
    msg=None
    if request.method=='POST':
        username=request.form['username']
        role=request.form['role']
        email1=request.form['email']
        Notices_details=Database.query.all()
        for i in Notices_details:
            if i.title==username:
                msg="Username Already Exist!"
                return render_template("register.html",msg5=msg,msg6=1)
            
        if role=="Verifier":
            branch=request.form['branch']
            Notices_details=Database(title=username,desc=request.form['password'],role=request.form['role'],email=email1,branch=branch)
        else:
            Notices_details=Database(title=username,desc=request.form['password'],role=request.form['role'],email=email1)
        db.session.add(Notices_details)
        db.session.commit()
        msg="Registration Successfully"
    msg=1

    return redirect("/dashboard")
    

@app.route("/register1")
def register1():
    msg=1
    return render_template("register.html",msg6=msg,msg11=1,msg222=1)

@app.route("/goto")
def goto():
    # allNotices_details=Notices_details.query.all()
    # username=session.get('a_username')
    # f_letter=username[0].upper()
    # return render_template("index.html",allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
    if session.get('v_logged-in') or session.get('a_logged-in'):
        if session.get('v_logged-in'):
            allNotices_details=Notices_details.query.all()
            username=session.get('v_username')
            f_letter=username[0].upper()
            return render_template("index1.html",allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
        elif session.get('a_logged-in'):
            allNotices_details=Notices_details.query.all()
            username=session.get('a_username')
            f_letter=username[0].upper()
            return render_template("index.html",allNotices_detailss=allNotices_details,username=username,f_letter=f_letter)
            
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get('a_logged-in'):
        return render_template("login.html")
    msg=1
    allNotices_detailss=Database.query.all()
    return render_template("register.html",msg7=msg,allNotices_detailss=allNotices_detailss,msg10=1,msg111=1)


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route("/superadmin")
def superadmin():
    global email_password
    global email_sender1
    global email_receiver1
    global em1
    global otp
    
    otp=generate_otp()
    body=f"Your OTP for Login is: {otp}"
    body1=MIMEText(body, 'plain')
    em1.attach(body1)
    context = ssl.create_default_context()
    msg=2
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        #smtp.starttls()
        smtp.login(email_sender1, email_password)
        smtp.sendmail(email_sender1, email_receiver1, em1.as_string())
        msg=1

    return render_template("login.html",msg7=msg)


@app.route("/login5",methods=['GET','POST'])
def login5():
    if request.method=='POST':
        otp1=request.form['otp']
        global otp
        if otp1==otp:
            msg=1
            allNotices_detailss=Database.query.all()
            return render_template("register.html",msg7=msg,allNotices_detailss=allNotices_detailss) 
        else:
            msg=1
            return render_template("login.html",msg8=msg)



class1=None
branch=None


upload=None
@app.route('/display1',methods=['GET','POST'])
def index1():
    if not session.get('v_logged-in'):
        return render_template("login.html")
    global class1
    global branch
    global year
    global date1
    global upload
    # Fetch a list of uploaded Word files
    if request.method=='POST':
        username=session.get('v_username')
        data=Database.query.filter_by(title=username).first()
        class1=request.form['class']
        branch=data.branch
        year=request.form['year']
        date1=request.form['date']
        Notices_detail=Notices_details.query.filter_by(title=class1,desc=branch,year=year).first()
        if Notices_detail!=None:
            if Notices_detail.generate==1:
                upload=os.path.join(f"D:/flask_practice1/flask_practice/{year}/{class1}/Notices",branch,date1)
                word_files_list = os.listdir(upload)
                if word_files_list:
                    generate=Generate.query.filter_by(title=class1,desc=branch,year=year).first()
                    generate.notify=1
                    db.session.commit()
                    
                    f_letter=username[0].upper()
                    return render_template('index1.html', word_files=word_files_list,username=username,f_letter=f_letter)
        msg=1
        # return render_template("index1.html",msg=msg,msg1=msg)
    msg=None
    username=session.get('v_username')
    f_letter=username[0].upper()
    
    return render_template("index1.html",msg=msg,username=username,f_letter=f_letter,msg555=1)



# Create the 'uploads' directory if it doesn't exist
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_docx(docx_path):
    if not session.get('v_logged-in'):
        return render_template("login.html")
    doc = Document(docx_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return text

def convert_to_html(text_content):
    if not session.get('v_logged-in'):
        return render_template("login.html")
    return markdown.markdown(text_content)


@app.route('/uploads/<filename>')
def download_file(filename):
    if not session.get('v_logged-in'):
        return render_template("login.html")
    global upload
    return send_from_directory(upload, filename, as_attachment=True)

@app.route('/reload')
def reload():
    global upload
    global class1
    global branch
    global year
    global date1
    word_files_list = os.listdir(upload)
    username=session.get('v_username')
    f_letter=username[0].upper()
    return render_template('index1.html', word_files=word_files_list,username=username,f_letter=f_letter)

@app.route('/delete_notice/<filename>')
def delete_notice(filename):
    if not session.get('v_logged-in'):
        return render_template("login.html")
    global upload
    file_path=os.path.join(upload,filename)
    os.remove(file_path)
    return redirect("/reload")
   


@app.route('/view/<filename>')
def view_file(filename):
    if not session.get('v_logged-in'):
        return render_template("login.html")
    global upload
    # Extract text from Word file
    docx_path = os.path.join(upload, filename)
    text_content = extract_text_from_docx(docx_path)
    
    # Convert text content to HTML using Markdown
    html_content = convert_to_html(text_content)
    
    # Display HTML content in the browser with cache control headers
    response = make_response(render_template('view.html', html_content=html_content))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('v_logged-in'):
        return render_template("login.html")
    # Handle file replacements
    if 'wordfile' in request.files:
        global upload
        global class1
        global branch
        global year
        global date1
        word_file = request.files['wordfile']
        if word_file.filename != '':
            # Use the original filename without modification
            filename = secure_filename(word_file.filename)
            
           
            try:
                filepath = os.path.join(upload, filename)
            except :
                return render_template("login.html")
            # Check if the file already exists and remove it
            file=os.path.splitext(filepath)[0]
            if os.path.exists(f"{file}.docx"):
                os.remove(f"{file}.docx")
            # Save the new file
            word_file.save(filepath)
            word_files_list = os.listdir(upload)
            username=session.get('v_username')
            f_letter=username[0].upper()
            return render_template('index1.html', word_files=word_files_list,username=username,f_letter=f_letter)
    username=session.get('v_username')
    f_letter=username[0].upper()
    return render_template('index1.html', word_files=word_files_list,username=username,f_letter=f_letter)

@app.route('/login11')
def submit():
    global ind
    

    global class1
    global branch
    global year
    global date1
    # Perform any necessary checks before displaying the message
    # (For demonstration purposes, let's assume all checks pass)
    try:
        generate=Generate.query.filter_by(title=class1,desc=branch,year=year,date=date1).first()
    except NameError:
        return render_template("login.html")
    if generate!=None:
        Notices_detail=Notices_details.query.filter_by(title=generate.title,desc=generate.desc,year=generate.year).first()
        Notices_detail.status=1
        db.session.commit() 
        generate.notify=0
        db.session.commit() 
    sno=1
    username=session.get('v_username')
    f_letter=username[0].upper()
    return render_template("index1.html",sno=sno,username=username,f_letter=f_letter)


@app.route("/user_portal")
def user_portal():
    if session.get('v_logged-in') or session.get('a_logged-in'):
        if session.get('v_logged-in'):
            user_details=Database.query.filter_by(title=session.get("v_username")).first()
            return render_template("user.html",user_details=user_details)
        elif session.get('a_logged-in'):
            user_details=Database.query.filter_by(title=session.get("a_username")).first()
            return render_template("user.html",user_details=user_details)
            
    return render_template("login.html")
    


if __name__ == "__main__":
    with app.app_context():
        db.create_all
    app.run(debug=True)
    # # gunicorn -w 4 -b 0.0.0.0:5000 app:app
    # pass
