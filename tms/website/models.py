from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    vehicleNumber = db.Column(db.String, unique=True)
    licenceNumber = db.Column(db.String)
    universityId = db.Column(db.String)
    universityEmail = db.Column(db.String)
    vehicleType = db.Column(db.String)
    approval = db.Column(db.String, default="pending")
    filename = db.Column(db.String)
    data = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    faculty_name = db.Column(db.String)
    occupation = db.Column(db.String)
    faculty_id = db.Column(db.String)
    email = db.Column(db.String)
    vehicle_number = db.Column(db.String)
    vehicle_type = db.Column(db.String)
    purpose = db.Column(db.String)
    date = db.Column(db.Date)
    allowance = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Pending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String,db.ForeignKey('visitor.name'))
    action = db.Column(db.String)
    reason = db.Column(db.String)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(30))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String, default="User")

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    role = db.Column(db.String, default="Admin")

class Security(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    role = db.Column(db.String, default="Security")

class RegRecords(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String, db.ForeignKey('registration.name'))
    vehicleNumber = db.Column(db.String, db.ForeignKey('registration.id'))
    allowDisallow = db.Column(db.String)
    inOut = db.Column(db.String)
    purpose = db.Column(db.String)
    date = db.Column(db.DateTime)

class UnRegRecords(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    vehicleNumber = db.Column(db.String)
    allowDisallow = db.Column(db.String)
    inOut = db.Column(db.String)
    purpose = db.Column(db.String)
    date = db.Column(db.DateTime)
