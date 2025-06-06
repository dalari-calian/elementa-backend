from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)
    money = db.Column(db.Float)
    xp = db.Column(db.Float)

 
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area,
            'money': self.money,
            'xp': self.xp
        }

class Enemy(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)

 
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area
        }

class Boss(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    current_area = db.Column(db.Integer)
    attemps = db.Column(db.Integer)
    defeat = db.Column(db.Boolean)

    
    def to_dict(self):
        return {
            'id': self.id,
            'hp': self.hp,
            'attack': self.attack,
            'current_area': self.current_area,
            'attemps': self.attemps,
            'defeat': self.defeat
        }
