from flask import Blueprint

# tem a mesma função app = Flask(__name__)
bp = Blueprint('main', __name__)

# encapsulando as rotas
from app.routes import players
