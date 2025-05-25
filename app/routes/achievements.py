from flask import jsonify, request
from app import db
from app.models import Player
from app.routes import bp
from app.auth import token_required
import json
import os
from datetime import datetime


ACHIEVEMENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'achievements.json')


os.makedirs(os.path.dirname(ACHIEVEMENTS_FILE), exist_ok=True)


if not os.path.exists(ACHIEVEMENTS_FILE):
    default_achievements = [
        {
            "id": 1,
            "name": "Primeiro Passo",
            "description": "Derrote seu primeiro inimigo",
            "reward_xp": 20,
            "reward_money": 10,
            "icon": "first_step.png",
            "area_required": 1,
            "enemies_defeated_required": 1,
            "bosses_defeated_required": 0
        },
        {
            "id": 2,
            "name": "Exterminador",
            "description": "Derrote 10 inimigos",
            "reward_xp": 50,
            "reward_money": 25,
            "icon": "exterminator.png",
            "area_required": 1,
            "enemies_defeated_required": 10,
            "bosses_defeated_required": 0
        },
        {
            "id": 3,
            "name": "Caçador de Chefes",
            "description": "Derrote seu primeiro chefe",
            "reward_xp": 100,
            "reward_money": 50,
            "icon": "boss_hunter.png",
            "area_required": 1,
            "enemies_defeated_required": 0,
            "bosses_defeated_required": 1
        },
        {
            "id": 4,
            "name": "Aventureiro",
            "description": "Alcance a área 2",
            "reward_xp": 150,
            "reward_money": 75,
            "icon": "adventurer.png",
            "area_required": 2,
            "enemies_defeated_required": 0,
            "bosses_defeated_required": 0
        },
        {
            "id": 5,
            "name": "Mestre das Lâminas",
            "description": "Alcance 20 de ataque",
            "reward_xp": 200,
            "reward_money": 100,
            "icon": "blade_master.png",
            "attack_required": 20,
            "area_required": 1,
            "enemies_defeated_required": 0,
            "bosses_defeated_required": 0
        }
    ]
    

    os.makedirs(os.path.dirname(ACHIEVEMENTS_FILE), exist_ok=True)
    with open(ACHIEVEMENTS_FILE, 'w') as f:
        json.dump(default_achievements, f, indent=4)


class PlayerAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    achievement_id = db.Column(db.Integer)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
   
    __table_args__ = (
        db.UniqueConstraint('player_id', 'achievement_id', name='_player_achievement_uc'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'achievement_id': self.achievement_id,
            'unlocked_at': self.unlocked_at.isoformat()
        }


def load_achievements():
    with open(ACHIEVEMENTS_FILE, 'r') as f:
        return json.load(f)

@bp.route('/achievements', methods=['GET'])
@token_required
def get_all_achievements(current_user):
    """Obter todas as conquistas disponíveis no jogo"""
    try:
        achievements = load_achievements()
        return jsonify(achievements), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/players/<int:player_id>/achievements', methods=['GET'])
@token_required
def get_player_achievements(current_user, player_id):
    """Obter as conquistas desbloqueadas por um jogador"""
    try:
       
        player = Player.query.get_or_404(player_id)
        
       
        player_achievements = PlayerAchievement.query.filter_by(player_id=player_id).all()
        achievement_ids = [pa.achievement_id for pa in player_achievements]
        
       
        all_achievements = load_achievements()
        
 
        unlocked = []
        locked = []
        
        for achievement in all_achievements:
            if achievement['id'] in achievement_ids:
           
                unlock_date = next((pa.unlocked_at for pa in player_achievements if pa.achievement_id == achievement['id']), None)
                achievement_copy = achievement.copy()
                achievement_copy['unlocked'] = True
                achievement_copy['unlocked_at'] = unlock_date.isoformat() if unlock_date else None
                unlocked.append(achievement_copy)
            else:
                achievement_copy = achievement.copy()
                achievement_copy['unlocked'] = False
                locked.append(achievement_copy)
                
        return jsonify({
            'unlocked': unlocked,
            'locked': locked,
            'total': len(all_achievements),
            'unlocked_count': len(unlocked),
            'progress_percentage': (len(unlocked) / len(all_achievements)) * 100
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/players/<int:player_id>/check_achievements', methods=['POST'])
@token_required
def check_achievements(current_user, player_id):
    """Verifica e desbloqueia conquistas para um jogador"""
    try:
        player = Player.query.get_or_404(player_id)
        
       
        data = request.get_json() or {}
        enemies_defeated = data.get('enemies_defeated', 0)
        bosses_defeated = data.get('bosses_defeated', 0)
        
       
        all_achievements = load_achievements()
        
      
        unlocked_achievements = PlayerAchievement.query.filter_by(player_id=player_id).all()
        unlocked_ids = [ua.achievement_id for ua in unlocked_achievements]
        
        newly_unlocked = []
        
  
        for achievement in all_achievements:
            if achievement['id'] not in unlocked_ids:
                requirements_met = True
                
              
                if 'area_required' in achievement and player.current_area < achievement['area_required']:
                    requirements_met = False
                    
                
                if 'attack_required' in achievement and player.attack < achievement['attack_required']:
                    requirements_met = False
                    
                
                if 'enemies_defeated_required' in achievement and enemies_defeated < achievement['enemies_defeated_required']:
                    requirements_met = False
                    
                
                if 'bosses_defeated_required' in achievement and bosses_defeated < achievement['bosses_defeated_required']:
                    requirements_met = False
                    
               
                if requirements_met:
                    new_achievement = PlayerAchievement(
                        player_id=player_id,
                        achievement_id=achievement['id'],
                        unlocked_at=datetime.utcnow()
                    )
                    db.session.add(new_achievement)
                    
              
                    if 'reward_xp' in achievement:
                        player.xp += achievement['reward_xp']
                    if 'reward_money' in achievement:
                        player.money += achievement['reward_money']
                    
                    newly_unlocked.append({
                        'achievement': achievement,
                        'rewards': {
                            'xp': achievement.get('reward_xp', 0),
                            'money': achievement.get('reward_money', 0)
                        }
                    })
        
   
        db.session.commit()
        
        return jsonify({
            'newly_unlocked': newly_unlocked,
            'player': player.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
