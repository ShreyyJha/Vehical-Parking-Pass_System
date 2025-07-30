from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Application, Pass
from .forms import RegisterForm, LoginForm, ApplicationForm
from . import db, login_manager
import io
from flask import send_file
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 🔥 Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('⚠️ Email already registered. Please log in.', 'warning')
            return redirect(url_for('main.login'))
        
        # If not, create new user
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(new_user)
        db.session.commit()
        flash('✅ Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)



@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    if not (current_user.is_admin or current_user.role == 'admin'):
        applications = Application.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', applications=applications)
    else:
        # Admin: see all applications
        applications = Application.query.all()
        return render_template('admin_dashboard.html', applications=applications)

@main.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=30)
        new_app = Application(
            user_id=current_user.id,
            vehicle_number=form.vehicle_number.data,
            vehicle_type=form.vehicle_type.data,
            mobile_number=form.mobile_number.data,
            issue_date=issue_date,
            expiry_date=expiry_date
            # photo=photo_path  # Handle photo upload if needed
        )
        db.session.add(new_app)
        db.session.commit()
        flash('Application submitted successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('apply.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/approve/<int:app_id>', methods=['POST'])
@login_required
def approve_application(app_id):
    if not (current_user.is_admin or current_user.role == 'admin'):
        return "Unauthorized", 403
    application = Application.query.get_or_404(app_id)
    application.status = 'Approved'
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/reject/<int:app_id>', methods=['POST'])
@login_required
def reject_application(app_id):
    if not (current_user.is_admin or current_user.role == 'admin'):
        return "Unauthorized", 403
    application = Application.query.get_or_404(app_id)
    application.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/download_pass/<int:app_id>')
@login_required
def download_pass(app_id):
    application = Application.query.get_or_404(app_id)
    if application.status != 'Approved':
        return "Pass not approved yet.", 403
    if not (current_user.is_admin or current_user.role == 'admin' or application.user_id == current_user.id):
        return "Unauthorized", 403

    # Generate QR code
    qr_data = f"Vehicle Number: {application.vehicle_number}\nVehicle Type: {application.vehicle_type}\nStatus: {application.status}\nMobile: {application.mobile_number}"
    qr_img = qrcode.make(qr_data)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)

    # Create PDF
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=letter)

    # Rectangle dimensions
    rect_width = 350
    rect_height = 400
    page_width, page_height = letter
    rect_x = (page_width - rect_width) / 2
    rect_y = (page_height - rect_height) / 2

    # Draw rectangle
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2)
    c.rect(rect_x, rect_y, rect_width, rect_height)

    # Centered positions
    center_x = page_width / 2

    # Draw QR code (smaller size, centered)
    qr_img_pil = Image.open(qr_buf)
    qr_size = 80  # Decreased size
    qr_x = center_x - qr_size / 2
    qr_y = rect_y + rect_height - 110
    c.drawInlineImage(qr_img_pil, qr_x, qr_y, width=qr_size, height=qr_size)

    # Draw text (centered inside rectangle)
    text_y = qr_y - 20
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(center_x, text_y, "PARKING PASS")

    text_y -= 35
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(center_x, text_y, application.user.name.upper())

    text_y -= 25
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(center_x, text_y, application.vehicle_number)

    text_y -= 20
    c.setFont("Helvetica", 12)
    c.drawCentredString(center_x, text_y, f"Vehicle: {application.vehicle_type}")

    text_y -= 20
    c.drawCentredString(center_x, text_y, f"Status: {application.status}")

    text_y -= 20
    c.drawCentredString(center_x, text_y, f"Issue Date: {application.issue_date.strftime('%m/%d/%Y')}")

    text_y -= 20
    c.drawCentredString(center_x, text_y, f"Expiry Date: {application.expiry_date.strftime('%m/%d/%Y')}")

    text_y -= 20
    c.drawCentredString(center_x, text_y, f"Mobile: {application.mobile_number}")


    c.showPage()
    c.save()
    pdf_buf.seek(0)

    return send_file(pdf_buf, as_attachment=True, download_name=f"pass_{application.id}.pdf", mimetype='application/pdf')