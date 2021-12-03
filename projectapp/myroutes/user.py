from operator import sub
import random,os,string,json,requests
from flask_mail import Message
from flask import render_template,url_for,session,request,flash,abort
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash

from projectapp import app,db
from projectapp.mymodel import Document, Guest, Questions, State, Gift, Transaction, guest_gift,Lga
from projectapp import mail,Message

@app.route('/', methods=['GET','POST'])
def home(): 
    if request.method=='GET':
        
        try:
            response = requests.get('http://127.0.0.1:8082/hostel/api/v1.0/listall/')
            hostels = json.loads(response.text)
        except requests.exceptions.ConnectionError as e:
            hostels = []
        mystates = db.session.query(State).all()
        return render_template('user/index.html',mystates=mystates,hostels=hostels)
    else:
        #retrieve form data
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        email = request.form.get('email')
        password = request.form.get('password')
        #save into database
        #convert password
        converted = generate_password_hash(password)
        g = Guest(guest_fname=fname,guest_lname=lname,state_id=state,guest_email=email,guest_pwd=converted)
        db.session.add(g)
        db.session.commit()
        #keep details in session
        session['user'] = g.id
        #save feedback in a flash
        flash('Form has been successfully submitted')
        #redirect to user/profile
        return redirect('user/profile')

@app.route('/user/profile')
def profile():
    loggedin_user = session.get('user')
    if loggedin_user != None:
        data = db.session.query(Guest).get(loggedin_user)
        iv = db.session.query(Document).get(1)
        return render_template('/user/profile.html',data=data,iv=iv)
    else:
        return 'display login form'

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/user/login', methods=['GET','POST'])
def login():
    if request.method =='GET':
        #1 display a template with login form
        return render_template('user/login.html')
    else:
        #2 retrieve form data
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #3 write a query to fetch from te guest table where username ='' and password =''
        deets = db.session.query(Guest).filter(Guest.guest_email==username).first()
        #4 if data was fetched, keep the id in session and redirect to profile page
        if deets:
            loggedin_user = deets.id
            hashedpass = deets.guest_pwd
            check = check_password_hash(hashedpass,pwd)
            if check:
                session['user'] = loggedin_user
                return redirect('/user/profile')
            else:
                flash('invalid username or password')
                return redirect(url_for('login'))
        else:
            #5 if data was empty, keep feedback in a flash and redirect to homepage/login page
            flash('invalid username or password')
            return redirect(url_for('login'))

@app.route('/user/gift',methods=['GET','POST'])
def gift():
    loggedin_user = session.get('user')
    if loggedin_user:
        if request.method == 'GET':
            mygifts = db.session.query(Gift).all()
            return render_template('user/gift.html',mygifts=mygifts)
        else:
            #retrieve form data
            selectedgift = request.form.getlist('item')
            if selectedgift:
                for i in selectedgift:
                    totalqty = 'quantity'+str(i)
                    total = request.form.get(totalqty,1)
                    statement = guest_gift.insert().values(gift_id=i, guest_id=loggedin_user,qty=total)
                    db.session.execute(statement)
                db.session.commit()
                flash('Thank you for your donation')
                return redirect('/user/profile')
            else:
                flash('Please select at least one gift item')
                return redirect('/user/gift')
    else:
        return redirect('/user/login')

@app.route('/addpicture', methods=['GET','POST'])
def addpicture():
    if session.get('user') != None:
        if request.method=='GET':
            return render_template('/user/addpicture.html')
        else:
            fileobj = request.files['uploadpic']
            if fileobj.filename == '':
                flash('Please select a file')
                return redirect(url_for('addpicture'))
            else:
                 #get the file extension,  #splits file into 2 parts on the extension
                name, ext = os.path.splitext(fileobj.filename)
                allowed_extensions=['.jpg','.jpeg','.png','.gif']
                if ext not in allowed_extensions:
                    flash(f'Extension {ext} is not allowed')
                    return redirect(url_for('addpicture'))
                else:
                    sample_xters = random.sample(string.ascii_lowercase,10) 
                    newname = ''.join(sample_xters) + ext
                    #original = str(random.random() * 10000) + fileobj.filename
                    destination = 'projectapp/static/images/guestpic/' +newname
                    fileobj.save(destination)
                    #save details into database
                    guestid = session.get('user')
                    guest = db.session.query(Guest).get(guestid)
                    guest.guest_profile_pic=newname
                    db.session.commit()
                    return redirect(url_for('profile'))
    else:
        return redirect('/user/login')

@app.route('/user/questions')
def questions():
    if session.get('user') !=None:
        return render_template('user/questions.html')
    else:
        return redirect(url_for('login'))

@app.route('/user/questionajax')
def questionajax():
    if session.get('user') !=None:
        return render_template('user/questionajax.html')
    else:
        return redirect(url_for('login'))

@app.route('/user/submitquestion', methods=['GET','POST'])
def submitquestion():
    loggedin = session.get('user')
    if loggedin !=None:
        myquest = request.form.get('question')
        ques = Questions(guest_id=loggedin,question=myquest)
        db.session.add(ques)
        db.session.commit()
        flash('Thank you for asking')
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))

@app.route('/user/submitquestionajax', methods=['GET','POST'])
def submitquestionajax():
    loggedin = session.get('user')
    if loggedin !=None:
        myquest = request.form.get('quest')
        myfirst = request.form.get('first')
        mylast = request.form.get('last')
        pixobj = request.files['pix']
        filename = pixobj.filename
        myques = Questions(guest_id=loggedin,question=myquest)
        db.session.add(myques)
        db.session.commit()
        return f'Thank you {myfirst} {mylast}, your question has been asked'
    else:
        return 'please log in to ask a question'

@app.route('/user/available',methods=['GET','POST'])
def available():
    if request.method=='GET':
        records = db.session.query(State).all()
        return render_template('user/available.html', records=records)
    else:
        user = request.form.get('user')
        deets = db.session.query(Guest).filter(Guest.guest_email==user).all()
        if deets:
            rsp = {"msg":"you have registered with this email","status":"failed"}
            return json.dumps(rsp)
        else:
            rsp = {"msg":"username available","status":"success"}
            return json.dumps(rsp)

@app.route('/user/lga')
def lga():
    state=request.args.get('stateid')
    data = db.session.query(Lga).filter(Lga.state_id==state).all()
    tosend = "<select class='form-control' name=''>"
    for t in data:
        tosend = tosend + f"<option>{t.lga_name}</option>"
    tosend= tosend+"</select>"
    return tosend

@app.route('/user/donatecash',methods=['GET','POST'])
def donatecash():
    loggedin = session.get('user')
    if loggedin:
        if request.method == 'GET':
            return render_template('user/donatecash.html')
        else:
            return 'Form submitted here'
    else:
        abort(403)




def refno():
    sample_xters = random.sample(string.digits,10)
    newname = ''.join(sample_xters)
    return newname

@app.route('/user/paycash',methods=['GET','POST'])
def paycash():
    loggedin = session.get('user')
    if loggedin:
        if request.method == 'GET':
            return render_template('user/paycash.html')
        else:
            #retrieve form data
            amount = request.form.get('amount',0)
            ref = refno()
            session['trxref'] = ref
            tran = Transaction(trx_guestid=loggedin,trx_amt=amount,trx_status='pending',trx_ref=ref)
            db.session.add(tran)
            db.session.commit()
            return redirect(url_for("paymentconfirmation"))
    else:
        return redirect(url_for('login'))


@app.route('/user/paymentconfirmation',methods=['GET','POST'])
def paymentconfirmation():
    if session.get('user') !=None and session.get('trxref') !=None:
        ref = session.get('trxref')
        deets = db.session.query(Transaction).filter(Transaction.trx_ref==ref).first()

        if request.method=='GET':
            return render_template('user/paymentconfirmation.html',deets=deets)  
        else:
            #connect to paystack endpoint
            amount = deets.trx_amt * 100
            email=deets.guest.guest_email
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_fa3151af8a36aea0eb83b7a1a83bb6e348f056ce"}            
            data = {"reference": ref, "amount": amount, "email": email}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

            rsp = json.loads(response.text) 	
            if rsp.get('status') == True:
                payurl = rsp['data']['authorization_url']
                return redirect(payurl)
            else:
                return redirect(url_for('paycash'))
    else:     
        return redirect(url_for('login'))

@app.route('/user/paymentverification')
def paystack():
    loggedin = session.get('user')
    if loggedin:
        #receive response from payment company and inform user of the transaction status
        return 'Transaction completed'
    else:
        abort(403)

@app.route('/testmail')
def testmail():
    Message()
    msg = Message(subject="Testing Mail", sender="ogunyemii@gmail.com", recipients=['cutymotunrayo@gmail.com'], body="Test Mail")
    fp = open('requirements.txt')
    msg.html= "<div><h1>Welcome Motunrayo</h1><p>We are excited to have you on board. Please find attached the company packet</p><hr><span>CEO, Google</span><img src='https://brandlogos.net/wp-content/uploads/2015/09/Google-logo-1-512x512.png'></div>"
    msg.attach('Requirements.txt', "application/text", fp.read())
    mail.send(msg)
    return "Mail was sent"

@app.route('/about-me')
def about():
    pwd = app.config['PASSWORD']
    return render_template('user/about.html',pwd=pwd)