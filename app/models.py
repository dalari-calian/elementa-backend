from app import db

class Player(db.Model): # cria o modelo de objeto para db
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)
    money = db.Column(db.Float)
    xp = db.Column(db.Float)

    # converte o objeto para um dicionário
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area,
            'money': self.money,
            'xp': self.xp
        }

class Enemy(db.Model): # cria o modelo de objeto para db
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)

    # converte o objeto para um dicionário
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area
        }

class Boss(db.Model): # cria o modelo de objeto para db
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)
    attemps = db.Column(db.Integer)
    defeat = db.Column(db.Boolean)

    # converte o objeto para um dicionário
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area,
            'attemps': self.attemps,
            'defeat': self.defeat
        }
