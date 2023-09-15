from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))


class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[InputRequired(), Length(min=2, max=50)])
    last_name = StringField('Фамилия', validators=[InputRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=120)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=6, max=200)])
    submit = SubmitField('Зарегистрироваться')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неправильный email или пароль. Попробуйте снова.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/dashboard')
def dashboard():
    return "Это страница входа"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
