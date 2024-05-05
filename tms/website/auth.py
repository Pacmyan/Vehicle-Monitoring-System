from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, session,jsonify
from .models import User, Registration, Admin, Security, Visitor, Pending, RegRecords,UnRegRecords
from . import db
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import current_app
import json

auth = Blueprint('auth', __name__)

@auth.route('/home')
@login_required
def home():
    print("A)",session['role'])
    if session['role'] == 'User':
        print("hi")
        return render_template("home.html", user=current_user)
    else:
        abort(403)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usernamee = request.form.get("Username")
        password = request.form.get("password")
        data = request.form
        print(data)
        user = Admin.query.filter_by(username=usernamee).first()
        if user:
            if user.password == password:
                print("role: " + user.role)
                flash("logged in succesfully", category="success")
                session['role'] = user.role
                login_user(user, remember = True)
                return redirect(url_for('auth.admin'))
            else:
                flash("passwords doesnot match", category="error")
                print("Passwords do not match")
                return redirect(url_for('auth.login'))
        else:
            user = Security.query.filter_by(username=usernamee).first()
            if user and user.password == password:
                session['plate_number'] = request.form.get('plate_number')
                session['role'] = user.role
                login_user(user, remember = True)
                return redirect(url_for('auth.security'))
            else:
                print("User not found or incorrect password")
                return redirect(url_for('auth.login'))

    return render_template("login.html", user=current_user)


@auth.route('/admin')
@login_required
def admin():
    if session['role'] == 'Admin':
        print("hi")
        return render_template("admin.html", user=current_user)
    else:
        abort(403)

@auth.route('/security', methods=['POST','GET'])
@login_required
def security():

    if session['role'] == 'Security':
        return render_template('security.html', registrations=None, visitor_info=None, user=current_user)


@auth.route('/get_plate_number', methods=['GET'])
@login_required
def get_plate_number():
    plate_number = session.get('plate_number')
    return jsonify({'plate_number': plate_number})


@auth.route('/loginn', methods=['GET', 'POST'])
def loginn():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                print(user.role)
                flash("logged in succesfully", category="success")
                session['role'] = user.role
                session['id'] = user.id
                login_user(user, remember = True)
                return redirect(url_for('auth.home'))
            else:
                flash("passwords doesnot match", category="error")
        else:
            flash("user not found", category="error")
            return redirect(url_for('auth.signup'))

    data = request.form
    print(data)
    return render_template("loginn.html", name="loki", user=current_user)


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        name = request.form.get("firstName")
        password = request.form.get("password")
        password1 = request.form.get("password1")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("User already exist", category='error')
        elif len(email) != 20:
            flash("email is not in the format xxyyyyxx@uohyd.ac.in (x-digit, y-alphabet)", category='error')
        elif password != password1:
            flash('passwords are not matching', category='error')
        elif len(password) < 4:
            flash('password is short', category='error')
        else:
            new_user = User(email=email, first_name=name,
                            password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('you are registered', category='success')
            print("user created")
            data = request.form
            print(data)

            return redirect(url_for('auth.loginn'))

    return render_template("signup.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    return redirect(url_for('auth.loginn'))


@auth.route('/logoutt')
@login_required
def logoutt():
    session.pop('role', None)
    logout_user() 
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if session['role'] == 'User':
        user = current_user
        if request.method == 'POST':
            name_of_owner = request.form['Name']
            vehicle_registration_number = request.form['Vehicle registration number']
            licence_number = request.form['licence']
            university_id_number = request.form['ID']
            university_email_id = request.form['email']
            vehicle_type = request.form['Vehicle Type']
            approval = "pending"

            # Handle file upload
            file = request.files['file']
            new_registration = Registration(
                name=name_of_owner,
                vehicleNumber=vehicle_registration_number,
                licenceNumber=licence_number,
                universityId=university_id_number,
                universityEmail=university_email_id,
                vehicleType=vehicle_type,
                approval=approval,
                filename=file.filename,  # Add file_path
                data=file.read(),
                user_id=user.id
            )

            db.session.add(new_registration)
            db.session.commit()
            flash('Your vehicle is up for registration', category='success')
            return redirect(url_for('auth.home'))  # Corrected the redirect URL

        return render_template("register.html", user=current_user)
    else:
        abort(403)


from datetime import datetime

@auth.route('/vehiclesinfo',methods=['GET', 'POST'])
@login_required
def vehiclesinfo():
    if session['role'] == 'Admin':
        print("hi")
        rrecords = RegRecords.query.all()
        urecords = UnRegRecords.query.all()
        return render_template("records.html", user=current_user,rrecords = rrecords,urecords=urecords)
    else:
        abort(403)

@auth.route('/visitorForm', methods=['GET', 'POST'])
@login_required
def visitorForm():
    if session['role'] == 'User':
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            faculty_name = request.form.get('faculty_name')
            occupation = request.form.get('occupation')
            faculty_id = request.form.get('faculty_id')
            email = request.form.get('email')
            vehicle_number = request.form.get('vehicle_number')
            vehicle_type = request.form.get('vehicle_type')
            purpose = request.form.get('purpose')
            date_str = request.form.get('date')
            
            # Convert date string to Python date object
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Create a new Visitor instance
            new_visitor = Visitor(
                name=name,
                faculty_name=faculty_name,
                occupation=occupation,
                faculty_id=faculty_id,
                email=email,
                vehicle_number=vehicle_number,
                vehicle_type=vehicle_type,
                purpose=purpose,
                date=date,
                allowance="No",
                user_id=current_user.id  # Assuming you have a user ID associated with the current user
            )

            # Add the new visitor to the database
            db.session.add(new_visitor)
            db.session.commit()

            flash('Visitor registered successfully', 'success')
            return redirect(url_for('auth.visitorForm'))

        return render_template("visitor.html", user=current_user)
    else:
        abort(403)


@auth.route('/approval')
@login_required
def approval():
    if session['role'] == 'Admin':
        not_approved_registrations = Registration.query.filter_by(approval='pending').all()
        return render_template('approval.html',registrations=not_approved_registrations,user = current_user)
    else :
        abort(403)

@auth.route('/vehicles')
@login_required
def myVehicles():
    if session['role'] == 'User':
        id = session['id']
        print(id,":; id")
        vehicles = Registration.query.filter_by(user_id = id).all()
        return render_template('myVehicles.html',user = current_user,vehicles = vehicles)
    else :
        abort(403)

@auth.route('/myVisitors')
@login_required
def myVisitors():
    if session['role'] == 'User':
        id = session['id']
        print(id,":; id")
        visitors = Visitor.query.filter_by(user_id = id).all()
        return render_template('myVisitors.html',user = current_user,visitors = visitors)
    else :
        abort(403)

@auth.route('/vehicleRecords')
@login_required
def vehicleRecords():
    if session['role'] == 'User':
        id = session['id']
        print(id,":; id")
        records = RegRecords.query.filter_by(user_id = id).all()
        return render_template('UserVehicleRecords.html',user = current_user,records = records)
    else :
        abort(403)

@auth.route('/PendingRequests')
@login_required
def pendingRequests():
    if session['role'] == 'User':
        id = session['id']
        print(id,": id")
        pending = Pending.query.filter_by(user_id = id).all()
        return render_template('pendingRequests.html',user = current_user,pending = pending)
    else :
        abort(403)

@auth.route('/accept-registration/<int:id>', methods=['POST'])
@login_required
def accept_registration(id):
    if session['role'] == 'Admin':
        registration = Registration.query.get(id)
        if registration:
            registration.approval = 'approved'
            db.session.commit()
            flash('Registration accepted successfully.', category='success')
        else:
            flash('Registration not found.', category='error')
    else:
        abort(403)
    return redirect(url_for('auth.approval'))

@auth.route('/decline-registration/<int:id>', methods=['POST'])
@login_required
def decline_registration(id):
    if session['role'] == 'Admin':
        registration = Registration.query.get(id)
        if registration:
            registration.approval = 'declined'
            db.session.commit()
            flash('Registration declined successfully.', category='success')
        else:
            flash('Registration not found.', category='error')
    else:
        abort(403)
    return redirect(url_for('auth.approval'))

@auth.route('/search_registration', methods=['GET', 'POST'])
@login_required
def search_registration():
    plate_number = request.args.get('plate_number')
    registrations = None
    visitor_info = None
    if plate_number:
        registrations = Registration.query.filter_by(vehicleNumber=plate_number).all()
        if not registrations:
            visitor_info = Visitor.query.filter_by(vehicle_number=plate_number).first()
    return render_template('security.html', registrations=registrations, visitor_info=visitor_info, user=current_user)

@auth.route('/submit_purpose', methods=['POST'])
@login_required
def submit_purpose():
    if request.method == 'POST':
        purpose = request.form.get('purpose')
        allow_disallow = request.form.get('allow_disallow')
        in_out = request.form.get('in_out')
        vehicleNumber = request.form.get('vehicleNumber')

        print("In/Out:", in_out)
        print("Purpose:", purpose)
        print("Allow/Disallow:", allow_disallow)
        print("vehicle number:",vehicleNumber)
        UnRegRecord = UnRegRecords(vehicleNumber=vehicleNumber, allowDisallow=allow_disallow, inOut=in_out, purpose=purpose, date = datetime.now())
        db.session.add(UnRegRecord)
        db.session.commit()
        # Here you can store the purpose in your database or perform any other necessary actions
        flash('Purpose submitted successfully!', 'success')
        return redirect(url_for('auth.search_registration'))  # Return a valid response
    else:
        # Handle the case where the form submission method is not POST
        flash('Invalid request method', 'error')
        return redirect(url_for('auth.search_registration')) 

@auth.route('/send_notification', methods=['POST'])
@login_required
def send_notification():
    if request.method == 'POST':
        user_id = request.json.get('id') 
        visitor_name = request.json.get('name')
        action = 'pending'
        reason = request.json.get('purpose')
        new_pending = Pending(user_id=user_id, name=visitor_name, action=action, reason=reason)
        db.session.add(new_pending)
        db.session.commit()
        return jsonify({"visid" : new_pending.id})
    else:
        flash('Invalid request method', 'error')
        return redirect(url_for('auth.search_registration'))
    
@auth.route('/send_notification1', methods=['POST'])
@login_required
def send_notification1():
    if request.method == 'POST': 
        id = request.json.get('id')
        print(id)
        pending = Pending.query.filter_by(id = id).first()
        print(pending)
        output = json.dumps({'name':pending.name,'action':pending.action})
        return output
    else:
        flash('Invalid request method', 'error')
        return redirect(url_for('auth.search_registration'))

    
@auth.route('/get_pending_action', methods=['GET'])
def get_pending_action():
    visitor_name = request.args.get('name')
    pending_entry = Pending.query.filter_by(name=visitor_name).first()
    if pending_entry:
        return jsonify({'action': pending_entry.action})
    else:
        return jsonify({'action': 'No pending action found for this visitor.'})

@auth.route('/process_action', methods=['POST'])
@login_required
def process_action():
    action = request.json.get('action')
    vehicleNumber = request.json.get('vehicleNumber')
    name = request.json.get('name')
    id = request.json.get('id')  # Not sure what this id refers to; adjust as needed

    # Create a new record in the RegRecords table
    if action in ['in', 'out']:  # Ensure action is valid
        record = RegRecords(
            user_id=id,  # Assuming current_user is available
            name=name,
            vehicleNumber=vehicleNumber,
            allowDisallow='allow',  # Set to 'allow'
            inOut=action,  # 'in' or 'out'
            purpose='registered vehicle',  # Set purpose as 'registered vehicle'
            date=datetime.now()  # Set current timestamp
        )
        db.session.add(record)
        db.session.commit()
    else:
        flash('Invalid action')

    return redirect(url_for('auth.search_registration'))

@auth.route('/toggle_allowance/<int:visitor_id>', methods=['POST'])
@login_required
def toggle_allowance(visitor_id):
    visitor = Visitor.query.get(visitor_id)
    if visitor:
        # Toggle the allowance status
        if visitor.allowance == 'Yes':
            visitor.allowance = 'No'
        else:
            visitor.allowance = 'Yes'
        db.session.commit()
        return redirect(url_for('auth.myVisitors'))  # Removed 'user=current_user'
    else:
        # Handle the case where visitor_id does not exist
        return redirect(url_for('auth.myVisitors'))


@auth.route('/update_action', methods=['POST'])
@login_required
def update_action():
    data = request.json
    pending_id = data.get('id')
    action = data.get('action')
    print(action)
    print(pending_id)
    if pending_id and action:
        pending = Pending.query.get(pending_id)

        if pending:
            pending.action = action
            db.session.commit()
            return redirect(url_for('auth.pendingRequests'))
        else:
            return redirect(url_for('auth.pendingRequests'))
    else:
        return redirect(url_for('auth.pendingRequests'))
    
@auth.route('/submit_disallow_form', methods=['POST'])
def submit_disallow_form():
    data = request.json
    purpose = data.get('purpose')
    pending_id = data.get('id')
    print(purpose)
    print(pending_id)
    if purpose:
          # Assuming you're passing the pending ID in the request query parameters
        pending = Pending.query.get(pending_id)

        if pending:
            pending.action = 'disallowed'
            pending.reason = purpose
            db.session.commit()
            return jsonify({'message': 'Disallowed successfully.'}), 200
        else:
            return jsonify({'error': 'Pending record not found.'}), 404
    else:
        return jsonify({'error': 'Purpose is required.'}), 400
