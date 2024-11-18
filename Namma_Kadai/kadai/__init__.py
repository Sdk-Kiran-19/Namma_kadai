from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///namma_kadai.db'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from kadai import routes