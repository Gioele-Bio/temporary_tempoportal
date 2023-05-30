from flask import Flask, render_template, redirect
# For authorisation forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email

# Manage DB connection
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Login helpers
from flask.helpers import url_for
from flask_login import LoginManager, login_user, logout_user
from flask_login.mixins import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
######## end imports

# Import Dash App
from dash_app.__main__ import create_dash_application


# Initialise running app
app = Flask(__name__,
    static_folder='./templates/static' # this is for the css of the html templates
    )
# Set secret key for the app! (This will need to be moved to environment varible using dotenv once in production)
app.config['SECRET_KEY'] = 'not_so_secret'


# Give address to db, in this case local folder, will become sql server
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"

#### Configure DB on app
db = SQLAlchemy(app)
migrate = Migrate(app, db)

######## Set up login manager
login = LoginManager()
login.init_app(app)

#### Set up dash app
create_dash_application(app)

# user_loader function is in charge of retrieving users from db!
@login.user_loader
def user_loader(user_id):
    # Return user info based on id
    return User.query.filter_by(id=user_id).first()


########################
# CLASSES

# Class for users 
class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True) # Need the autoincrement!
    email = db.Column(db.String(128), nullable=False) # NO MORE PRIMARY KEY. but not null
    password = db.Column(db.String(128), nullable=False)



# Class for logging in
class LoginForm(FlaskForm):
    email = StringField('email', validators=[Length(min=5)])
    password = PasswordField('password', validators=[Length(min=5)])

# Class for registering a user
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[Length(min=5)])
    password = PasswordField('password', validators=[Length(min=5)])
    repeat_password = PasswordField('repeat_password', validators=[Length(min=5)])

########################






# ###########
#As of now the app cannot import itself, need to fix it! search run dash app in flask app
# apparently DispatcherMiddleware works but need to find flask alternative





#https://flask.palletsprojects.com/en/2.2.x/patterns/appdispatch/






#########################
# ROUTES

# Home route redirects to login
@app.route('/')
def index():
    return redirect(url_for('login'))


# Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Declare login form obj
    form = LoginForm()
    # Check if the form is valid or not
    if form.validate_on_submit():
        # If the form is valid we want to get the user obj by email, and check the hashed pass
        user = User.query.filter_by(email=form.email.data).first()

        # If the user object is none, it means that it's not present in the DB and consequently was never registered
        if not user:
            # This 'artificially' registers an error associated with the email!!
            form.email.errors.append(f'Could not find an account associated with the email {form.email.data}')

            # form.errors.pop('password')
            print(form.errors.keys())
            return render_template('login.html', form=form, errors=form.errors)

        

        # Check pass
        if user and check_password_hash(user.password, form.password.data):
            # Login the user (cookie)
            login_user(user)
            # Redirect it to the dash app!
            return redirect(url_for('/app/'))
        # If the password is wrong, give error message
        else:
            form.password.errors.append('Wrong password, try again!')

        print(form.errors)
    # Standard return with template
    return render_template('login.html', form=form, errors=form.errors)




# Route to register 
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # Check if valid and both pass are the same
    if form.validate_on_submit() and form.password.data == form.repeat_password.data:

        # Check that there is not already an account associated with the email
        repeat_user = User.query.filter_by(email=form.email.data).first()

        if repeat_user == None:
            # Make user model to return (with data taken from form)
            user = User(
                email = form.email.data,
                # Save hashed pass
                password = generate_password_hash(form.password.data)
            )
            # Save new user in DB!
            db.session.add(user)
            db.session.commit()

            #Redirect to login!
            return redirect(url_for('login'))

        #else there is already an account registered with it
        else:
            form.email.errors.append('There is already an account associated with this email!')


    else:
        print(form.errors) #### This does not pick up if pass are different!! 
        # Condition to notify user that the passwords are different!
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('The passwords do not match!')

        

    # Standard template
    return render_template('register.html', form=form, errors=form.errors)



# Logout endpoint (removes cookies)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

############################


if __name__ == '__main__':
    app.run()








##########################











