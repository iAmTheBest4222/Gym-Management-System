from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt() 