from flask import Flask, Blueprint, render_template, redirect, url_for, flash, request, session
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
import random
import os
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
from flask_mail import Mail, Message
from models import db, User, PasswordResetToken, Item, Category, Notification, ItemStatusEnum
app = Flask(__name__)

app.config['SECRET_KEY'] = 'd6b5f6a4d1c1e3c9b7d9d2f1e8b9c0a4e5d6f7a8b9c0d1e2f3a4b5c6d7e8f9g0h'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/lost-found_db?charset=utf8mb4'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '_____@gmail.com'
app.config['MAIL_PASSWORD'] = 'passeward'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db.init_app(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_otp_reg(email, otp):
    msg = Message('Email Confirmation OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #004085; text-align: centre;">LOST-FOUND Management Team</h2>
        <p>Welcome!</p>
        <p>Thank you for signing up! Please confirm your college email ID.</p>
        <p style="font-size: 18px; color: #007bff;"><strong>Your OTP code is: {otp}</strong></p>
        <p style="color: #6c757d;">If you did not request this, please ignore this email.</p>
        <hr>
        <p style="font-size: 12px; color: #6c757d;">This is an automated message, please do not reply.</p>
    </div>
    '''
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
        flash('Failed to send OTP. Please try again later.', category='danger')

def send_otp_forget_pass(email, otp):
    msg = Message('Password Reset OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #004085;  text-align: centre;">LOST-FOUND Management Team</h2>
        <p>You have requested a password reset.</p>
        <p style="font-size: 18px; color: #007bff;"><strong>Your OTP code is: {otp}</strong></p>
        <p style="color: #6c757d;">If you did not request this, please secure your account immediately.</p>
        <hr>
        <p style="font-size: 12px; color: #6c757d;">This is an automated message, please do not reply.</p>
    </div>
    '''
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
        flash('Failed to send OTP. Please try again later.', category='danger')


def generate_otp():
    return f"{random.randint(100000, 999999)}"

EXPIRATION_TIME = 600

def generate_token(data, expiration=EXPIRATION_TIME):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps(data).decode('utf-8')

def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None
    return data


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        roll_number = request.form.get('roll_number')
        batch = request.form.get('batch')
        course = request.form.get('course')
        branch = request.form.get('branch')

        # ✅ 密码校验（保留，安全）
        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(
                char.isalpha() for char in password):
            flash('Password must be at least 8 characters long and contain both letters and digits.', category='danger')
            return redirect(url_for('register'))

        # ✅ 邮箱是否重复
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', category='danger')
            return redirect(url_for('register'))

        # ✅ 直接创建用户，不验证邮箱
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            roll_number=roll_number,
            batch=batch,
            course=course,
            branch=branch,
            is_verified=True   # ✅ 关键：直接放行
        )
        db.session.add(new_user)
        db.session.commit()

        flash('注册成功，请登录！', category='success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Route for verifying registration
@app.route('/verify_registration', methods=['GET', 'POST'])
def verify_registration():
    if request.method == 'POST':
        otp = request.form.get('otp')
        temp_user = session.get('temp_user')

        if temp_user:
            # Convert both to timezone-aware datetimes for comparison
            otp_generated_at = temp_user.get('otp_generated_at').astimezone(timezone.utc)
            otp_age = datetime.now(timezone.utc) - otp_generated_at

            if otp_age.total_seconds() > 600:  # 10 minutes in seconds
                flash('OTP has expired. Please request a new one.', category='danger')
                return redirect(url_for('register'))

            if temp_user['otp'] == otp:
                new_user = User(
                    email=temp_user['email'],
                    first_name=temp_user['first_name'],
                    last_name=temp_user['last_name'],
                    password=temp_user['password'],
                    roll_number=temp_user['roll_number'],
                    batch=temp_user['batch'],
                    course=temp_user['course'],
                    branch=temp_user['branch'],
                    is_verified=True
                )
                db.session.add(new_user)
                db.session.commit()
                session.pop('temp_user', None)
                flash('Your account has been created successfully!', category='success')
                return redirect(url_for('login'))
            else:
                flash('Invalid OTP. Please try again.', category='danger')

    return render_template('verify_registration.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            if user.is_verified:
                login_user(user)
                flash('Login successful!', category='success')
                return redirect(url_for('home_page'))
            else:
                flash('Please verify your email before logging in.', category='danger')
        else:
            flash('Login failed. Check your credentials.', category='danger')
    return render_template('login.html')


# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()

        if user:

            session['reset_user'] = user.id

            flash('邮箱验证成功，请设置新密码。', category='success')

            return redirect(url_for('reset_password'))

        else:

            flash('该邮箱未注册。', category='danger')


    return render_template('forgot_password.html')



# Route for resetting password
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    user_id = session.get('reset_user')

    if not user_id:

        flash('请先验证邮箱。', category='danger')

        return redirect(url_for('forgot_password'))


    if request.method == 'POST':

        password = request.form.get('password')


        if password is None or len(password) < 8 or \
           not any(char.isdigit() for char in password) or \
           not any(char.isalpha() for char in password):

            flash(
                '密码至少8位，并且包含字母和数字。',
                category='danger'
            )

            return redirect(url_for('reset_password'))



        user = User.query.get(user_id)

        user.password = bcrypt.generate_password_hash(password).decode('utf-8')

        db.session.commit()


        session.pop('reset_user', None)


        flash(
            '密码修改成功，请重新登录。',
            category='success'
        )


        return redirect(url_for('login'))



    return render_template('reset_password.html')


@app.route('/admin')
@login_required
def admin():

    # 判断是不是管理员
    if not current_user.is_admin:
        flash('没有管理员权限', 'danger')
        return redirect(url_for('home_page'))

    # 获取所有数据
    users = User.query.all()
    items = Item.query.all()
    categories = Category.query.all()

    return render_template(
        'admin.html',
        users=users,
        items=items,
        categories=categories,
        user_count=len(users),
        item_count=len(items),
        category_count=len(categories)
    )


@app.route('/admin/delete_item/<int:item_id>', methods=['POST'])
@login_required
def admin_delete_item(item_id):

    if not current_user.is_admin:
        flash('没有权限','danger')
        return redirect(url_for('home_page'))


    item = Item.query.get_or_404(item_id)


    db.session.delete(item)

    db.session.commit()


    flash('删除成功','success')

    return redirect(url_for('admin'))


@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('没有权限', 'danger')
        return redirect(url_for('home_page'))

    user = User.query.get_or_404(user_id)

    # 不允许修改自己的管理员权限
    if user.id == current_user.id:
        flash('不能修改自己的管理员权限', 'danger')
        return redirect(url_for('admin'))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash('管理员权限已修改', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):

    if not current_user.is_admin:
        flash('没有权限','danger')
        return redirect(url_for('home_page'))

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('不能删除自己','danger')
        return redirect(url_for('admin'))

    db.session.delete(user)
    db.session.commit()

    flash('用户删除成功','success')

    return redirect(url_for('admin'))

@app.route('/')
def home_page():
    # Get search and category parameters from the request
    search_term = request.args.get('search', '')
    category_id = request.args.get('category', '')

    # Build the query with filters
    query = Item.query

    if search_term:
        query = query.filter(
            (Item.name.ilike(f'%{search_term}%')) |
            (Item.description.ilike(f'%{search_term}%'))
        )

    if category_id:
        query = query.filter(Item.category_id == category_id)

    items = query.all()
    categories = Category.query.all()

    return render_template('home.html', items=items, categories=categories)


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():

    categories = Category.query.all()

    if request.method == 'POST':

        name = request.form.get('name')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        status = request.form.get('status')
        date = request.form.get('date')
        location = request.form.get('location')
        image = request.files.get('image')


        image_filename = 'default.jpg'

        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_filename
                )
            )


        new_item = Item(
            name=name,
            description=description,
            category_id=category_id,
            status=status,
            date=date,
            image_file=image_filename,
            user_id=current_user.id,
            location=location
        )


        db.session.add(new_item)
        db.session.commit()


        flash('发布成功', 'success')
        return redirect(url_for('home_page'))


    return render_template(
        'add_item.html',
        categories=categories
    )

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    # 所有权校验：仅允许所有者编辑
    if item.user_id != current_user.id:
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('home_page'))

    if request.method == 'POST':
        item.name = request.form.get('name', item.name)
        item.description = request.form.get('description', item.description)
        item.category_id = request.form.get('category', item.category_id)
        item.status = request.form.get('status', item.status)
        item.date = request.form.get('date', item.date)
        item.location = request.form.get('location', item.location)
        image_file = request.files.get('image') or request.files.get('image_file')

        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            item.image_file = image_filename

        db.session.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('home_page'))

    categories = Category.query.all()
    return render_template('edit_item.html', item=item, categories=categories)


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)

    # 所有权校验：仅允许所有者删除
    if item.user_id != current_user.id:
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('home_page'))

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully.', 'success')
    return redirect(url_for('home_page'))

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_details.html', item=item)


@app.route('/notifications')
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html', notifications=notifications)


@app.route('/profile')
@login_required
def view_profile():
    courses = {
        'BTECH': 'Btech',
        'BARCH': 'Barch',
        'MTECH': 'Mtech',
        'MSC': 'Msc',
        'PHD': 'PHD'
    }
    branches = {
        'CSE': 'CSE',
        'ECE': 'ECE',
        'EEE': 'EEE',
        'ICE': 'ICE',
        'Chem': 'Chem',
        'Civil': 'Civil',
        'MECH': 'MECH',
        'Prod': 'Prod',
        'Other': 'Other'
    }
    return render_template('profile.html', courses=courses, branches=branches)



@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        user = User.query.get(current_user.id)
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.roll_number = request.form['roll_number']
        user.batch = request.form['batch']
        user.course = request.form['course']
        user.branch = request.form['branch']

        # Handle image upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('static/images', filename)
                file.save(file_path)
                user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('view_profile'))

    return render_template('edit_profile.html')

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


if __name__ == '__main__':
    app.run(debug=True)