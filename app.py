from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signature_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    full_name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Signature Template Model
class SignatureTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    html_content = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    templates = SignatureTemplate.query.all()
    return render_template('index.html', templates=templates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        position = request.form.get('position')
        department = request.form.get('department')
        phone = request.form.get('phone')
        is_admin = request.form.get('is_admin') == 'on'

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('create_user'))

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            position=position,
            department=department,
            phone=phone,
            is_admin=is_admin
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_user.html')

# Signature Template Routes
@app.route('/templates')
@login_required
def list_templates():
    templates = SignatureTemplate.query.all()
    return render_template('templates/list.html', templates=templates)

@app.route('/templates/create', methods=['GET', 'POST'])
@login_required
def create_template():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        html_content = request.form.get('html_content')
        is_default = request.form.get('is_default') == 'on'

        if is_default:
            # Reset all other templates' is_default to False
            SignatureTemplate.query.update({'is_default': False})
        
        template = SignatureTemplate(
            name=name,
            description=description,
            html_content=html_content,
            is_default=is_default,
            created_by=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        flash('Template created successfully', 'success')
        return redirect(url_for('list_templates'))
    
    return render_template('templates/create.html')

@app.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    template = SignatureTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        template.name = request.form.get('name')
        template.description = request.form.get('description')
        template.html_content = request.form.get('html_content')
        is_default = request.form.get('is_default') == 'on'
        
        if is_default:
            # Reset all other templates' is_default to False
            SignatureTemplate.query.filter(SignatureTemplate.id != template_id).update({'is_default': False})
        template.is_default = is_default
        
        db.session.commit()
        flash('Template updated successfully', 'success')
        return redirect(url_for('list_templates'))
    
    return render_template('templates/edit.html', template=template)

@app.route('/templates/<int:template_id>/preview')
@login_required
def preview_template(template_id):
    template = SignatureTemplate.query.get_or_404(template_id)
    return template.html_content

@app.route('/templates/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_template(template_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    template = SignatureTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return jsonify({'message': 'Template deleted successfully'})

@app.route('/update_signature/<username>', methods=['POST'])
@login_required
def update_signature(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    template_id = request.form.get('template_id')
    template = SignatureTemplate.query.get(template_id)
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('index'))
    
    # TODO: Implement signature update logic
    flash('Signature updated successfully', 'success')
    return redirect(url_for('index'))

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 