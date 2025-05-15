import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import json
from sqlalchemy import event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Harjitsinh1971'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbershop.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Flask Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update with your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'harjitsinh.raol701@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'R_2004846709791971h'  # Update with your password
app.config['MAIL_DEFAULT_SENDER'] = 'harjitsinh.raol701@gmail.com'  # Update with your email

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Add context processor to provide 'now' to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    category = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), nullable=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service = db.relationship('Service', backref='appointments')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, canceled
    notes = db.Column(db.Text, nullable=True)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    
class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AppointmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    date = DateField('Date', validators=[DataRequired()])
    time = SelectField('Time', validators=[DataRequired()], choices=[])
    service = SelectField('Service', validators=[DataRequired()], coerce=int)
    notes = TextAreaField('Special Requests')
    submit = SubmitField('Book Appointment')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject')
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = StringField('Price', validators=[DataRequired()])
    duration = StringField('Duration (minutes)', validators=[DataRequired()])
    category = StringField('Category')
    submit = SubmitField('Save Service')

class TestimonialForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    comment = TextAreaField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Replace the @app.before_first_request with SQLAlchemy event listener
def create_initial_data():
    db.create_all()
    
    # Check if we already have users
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@famabarber.com',
            is_admin=True
        )
        admin.set_password('adminpassword')  # Change in production!
        db.session.add(admin)
        
        # Add sample services
        services = [
            Service(name='Men\'s Haircut', description='Classic haircut with styling', price=25.00, duration=30, category='Haircut'),
            Service(name='Beard Trim', description='Shape and trim your beard', price=15.00, duration=20, category='Grooming'),
            Service(name='Hot Towel Shave', description='Traditional straight razor shave with hot towel', price=35.00, duration=45, category='Shaving'),
            Service(name='Kids Haircut', description='Haircut for children under 12', price=18.00, duration=25, category='Haircut'),
            Service(name='Hair Color', description='Professional hair coloring', price=65.00, duration=90, category='Color'),
            Service(name='Highlights', description='Partial or full highlights', price=85.00, duration=120, category='Color'),
            Service(name='Haircut & Beard Trim', description='Complete package with haircut and beard trimming', price=35.00, duration=45, category='Package'),
            Service(name='VIP Package', description='Haircut, beard trim, facial, and styling', price=55.00, duration=75, category='Package'),
        ]
        
        db.session.add_all(services)
        
        # Add sample testimonial
        testimonial = Testimonial(
            name='John Doe',
            rating=3,
            comment='Costly compared to other barbershops with better haircuts.',
            approved=True
        )
        db.session.add(testimonial)
        
        # Add more positive testimonials
        more_testimonials = [
            Testimonial(name='Michael Smith', rating=5, comment='Best haircut I\'ve ever had! The attention to detail is amazing.', approved=True),
            Testimonial(name='David Johnson', rating=4, comment='Great atmosphere and professional service. Highly recommended.', approved=True),
            Testimonial(name='Robert Williams', rating=5, comment='Been coming here for years. Never had a bad experience.', approved=True),
            Testimonial(name='James Brown', rating=4, comment='The hot towel shave is a must-try. So relaxing!', approved=True),
        ]
        db.session.add_all(more_testimonials)
        
        db.session.commit()

# Set up SQLAlchemy event to create initial data
@event.listens_for(db.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    if len(tables) > 0:
        create_initial_data()

with app.app_context():
    db.create_all()
    # Check if we need to create initial data
    if User.query.count() == 0:
        create_initial_data()

# Routes
@app.route('/')
def index():
    # Simplify: Just render the base template to avoid errors
    return render_template('index.html', 
                        services=[], 
                        testimonials=[],
                        gallery_images=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template('services.html', services=services)

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()
    return render_template('gallery.html', images=images)

@app.route('/testimonials')
def testimonials():
    form = TestimonialForm()
    testimonials = Testimonial.query.filter_by(approved=True).order_by(Testimonial.date.desc()).all()
    return render_template('testimonials.html', testimonials=testimonials, form=form)

@app.route('/testimonials/add', methods=['POST'])
def add_testimonial():
    form = TestimonialForm()
    if form.validate_on_submit():
        testimonial = Testimonial(
            name=form.name.data,
            rating=form.rating.data,
            comment=form.comment.data,
            approved=False  # Will need admin approval
        )
        db.session.add(testimonial)
        db.session.commit()
        flash('Thank you for your review! It will be visible after approval.')
        return redirect(url_for('testimonials'))
    
    return redirect(url_for('testimonials'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                subject=f"New Contact Message: {form.subject.data}",
                recipients=["admin@famabarber.com"],  # Update with admin email
                body=f"From: {form.name.data} ({form.email.data})\n\n{form.message.data}"
            )
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email: {e}")
            
        flash('Your message has been sent. We will get back to you soon!')
        return redirect(url_for('contact'))
        
    return render_template('contact.html', form=form)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = AppointmentForm()
    
    # Populate service choices
    services = Service.query.all()
    form.service.choices = [(s.id, f"{s.name} - ${s.price}") for s in services]
    
    # Populate time choices (8 AM to 6 PM in 30-minute intervals)
    form.time.choices = [
        ('09:00', '9:00 AM'), ('09:30', '9:30 AM'),
        ('10:00', '10:00 AM'), ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'), ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'), ('12:30', '12:30 PM'),
        ('13:00', '1:00 PM'), ('13:30', '1:30 PM'),
        ('14:00', '2:00 PM'), ('14:30', '2:30 PM'),
        ('15:00', '3:00 PM'), ('15:30', '3:30 PM'),
        ('16:00', '4:00 PM'), ('16:30', '4:30 PM'),
        ('17:00', '5:00 PM'), ('17:30', '5:30 PM'),
        ('18:00', '6:00 PM'), ('18:30', '6:30 PM'),
    ]
    
    if form.validate_on_submit():
        service = Service.query.get(form.service.data)
        
        # Convert time string to time object
        time_str = form.time.data
        hour, minute = map(int, time_str.split(':'))
        appointment_time = datetime.time(hour, minute)
        
        appointment = Appointment(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            date=form.date.data,
            time=appointment_time,
            service_id=service.id,
            notes=form.notes.data,
            status='pending'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send confirmation email
        try:
            msg = Message(
                subject="Your Appointment Confirmation - Fama Barber Shop",
                recipients=[form.email.data],
                body=f"Dear {form.name.data},\n\nYour appointment has been scheduled for {form.date.data.strftime('%A, %B %d, %Y')} at {time_str}.\n\nService: {service.name}\nPrice: ${service.price}\n\nThank you for choosing Fama Barber Shop & Beauty Salon.\n\nAddress: 500 N Bell Ave #109, Denton, TX 76209\nPhone: +1 940-612-9127"
            )
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send confirmation email: {e}")
        
        flash('Your appointment has been scheduled! Check your email for confirmation.')
        return redirect(url_for('booking'))
    
    return render_template('booking.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.')
        return redirect(url_for('index'))
        
    appointments = Appointment.query.order_by(Appointment.date.desc()).limit(10).all()
    messages = ContactMessage.query.filter_by(read=False).all()
    pending_testimonials = Testimonial.query.filter_by(approved=False).all()
    
    return render_template('admin/dashboard.html', 
                          appointments=appointments, 
                          messages=messages,
                          pending_testimonials=pending_testimonials)

@app.route('/admin/services', methods=['GET', 'POST'])
@login_required
def admin_services():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            price=float(form.price.data),
            duration=int(form.duration.data),
            category=form.category.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!')
        return redirect(url_for('admin_services'))
        
    services = Service.query.all()
    return render_template('admin/services.html', services=services, form=form)

@app.route('/admin/service/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    service = Service.query.get_or_404(id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.price = float(form.price.data)
        service.duration = int(form.duration.data)
        service.category = form.category.data
        
        db.session.commit()
        flash('Service updated successfully!')
        return redirect(url_for('admin_services'))
        
    return render_template('admin/edit_service.html', form=form, service=service)

@app.route('/admin/service/<int:id>/delete', methods=['POST'])
@login_required
def delete_service(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!')
    return redirect(url_for('admin_services'))

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    appointments = Appointment.query.order_by(Appointment.date, Appointment.time).all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/appointment/<int:id>/update', methods=['POST'])
@login_required
def update_appointment(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    appointment = Appointment.query.get_or_404(id)
    status = request.form.get('status')
    
    if status in ['pending', 'confirmed', 'canceled']:
        appointment.status = status
        db.session.commit()
        flash('Appointment status updated!')
        
    return redirect(url_for('admin_appointments'))

@app.route('/admin/gallery', methods=['GET', 'POST'])
@login_required
def admin_gallery():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            # Add timestamp to ensure uniqueness
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            description = request.form.get('description', '')
            image = GalleryImage(filename=filename, description=description)
            db.session.add(image)
            db.session.commit()
            
            flash('Image uploaded successfully!')
            return redirect(url_for('admin_gallery'))
    
    images = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()
    return render_template('admin/gallery.html', images=images)

@app.route('/admin/gallery/<int:id>/delete', methods=['POST'])
@login_required
def delete_gallery_image(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    image = GalleryImage.query.get_or_404(id)
    
    # Delete file from filesystem
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully!')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/testimonials')
@login_required
def admin_testimonials():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    testimonials = Testimonial.query.order_by(Testimonial.approved, Testimonial.date.desc()).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonial/<int:id>/approve', methods=['POST'])
@login_required
def approve_testimonial(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    testimonial = Testimonial.query.get_or_404(id)
    testimonial.approved = True
    db.session.commit()
    
    flash('Testimonial approved!')
    return redirect(url_for('admin_testimonials'))

@app.route('/admin/testimonial/<int:id>/delete', methods=['POST'])
@login_required
def delete_testimonial(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    testimonial = Testimonial.query.get_or_404(id)
    db.session.delete(testimonial)
    db.session.commit()
    
    flash('Testimonial deleted!')
    return redirect(url_for('admin_testimonials'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/message/<int:id>/view', methods=['GET', 'POST'])
@login_required
def view_message(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    message = ContactMessage.query.get_or_404(id)
    
    if not message.read:
        message.read = True
        db.session.commit()
    
    if request.method == 'POST':
        reply_text = request.form.get('reply', '')
        
        # Send reply email
        try:
            msg = Message(
                subject=f"Re: {message.subject or 'Your message to Fama Barber Shop'}",
                recipients=[message.email],
                body=f"Dear {message.name},\n\n{reply_text}\n\nRegards,\nFama Barber Shop & Beauty Salon\n500 N Bell Ave #109, Denton, TX 76209\nPhone: +1 940-612-9127"
            )
            mail.send(msg)
            flash('Reply sent successfully!')
        except Exception as e:
            app.logger.error(f"Failed to send reply email: {e}")
            flash('Failed to send reply. Please try again later.')
            
        return redirect(url_for('admin_messages'))
        
    return render_template('admin/view_message.html', message=message)

@app.route('/admin/message/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted!')
    return redirect(url_for('admin_messages'))

# API endpoints for frontend
@app.route('/api/services')
def api_services():
    services = Service.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'price': s.price,
        'duration': s.duration,
        'category': s.category
    } for s in services])

@app.route('/api/testimonials')
def api_testimonials():
    testimonials = Testimonial.query.filter_by(approved=True).order_by(Testimonial.date.desc()).all()
    return jsonify([{
        'name': t.name,
        'rating': t.rating,
        'comment': t.comment,
        'date': t.date.strftime('%B %d, %Y')
    } for t in testimonials])

@app.route('/api/gallery')
def api_gallery():
    images = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()
    return jsonify([{
        'id': img.id,
        'url': url_for('static', filename=f'uploads/{img.filename}'),
        'description': img.description
    } for img in images])

@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    data = request.get_json()
    date_str = data.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date is required'}), 400
        
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
        
    # Get all booked appointments for this date
    booked_slots = Appointment.query.filter_by(
        date=date, 
        status='confirmed'
    ).all()
    
    # Convert to time strings for easy comparison
    booked_times = [appt.time.strftime('%H:%M') for appt in booked_slots]
    
    # All available time slots
    all_slots = [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
        '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
        '18:00', '18:30'
    ]
    
    # Filter out booked slots
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return jsonify({
        'date': date_str,
        'available_slots': available_slots
    })

if __name__ == '__main__':
    app.run(debug=True) 

# Add this line for Vercel deployment
app.debug = False 
