# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Exemplo de URI: mysql+pymysql://usuario:senha@localhost/nome_do_banco
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://usuario:senha@localhost/elementa'
    SQLALCHEMY_TRACK_MODIFICATIONS = False