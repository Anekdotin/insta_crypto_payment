from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI_0
from decimal import Decimal


def floating_decimals(f_val, dec):
    prc = "{:."+str(dec)+"f}"
    return Decimal(prc.format(f_val))



app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_0


db = SQLAlchemy(app)
