from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(10), default='staff')  # 'staff' or 'admin'
    is_admin = db.Column(db.Boolean, default=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vehicle_number = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(50))
    mobile_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')  # Pending/Approved/Rejected
    issue_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    user = db.relationship('User', backref='applications')

class Pass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    pass_number = db.Column(db.String(20))
    pdf_file = db.Column(db.String(200))
