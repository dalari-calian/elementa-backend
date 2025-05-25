from flask import jsonify, request
from app import db
from app.models import Player, Enemy, Boss
from app.routes import bp
from app.auth import token_required
import random
import math


XP_PER_ENEMY = 10  
XP_PER_BOSS = 50   
XP_MULTIPLIER = 1.5  
MONEY_PER_ENEMY = 5  
MONEY_PER_BOSS = 25  
LEVEL_UP_XP_BASE = 100  
LEVEL_UP_ATTACK_BONUS = 2  
LEVEL_UP_HP_BONUS = 20  

def calculate_level(xp):
    """Calcula o nível do jogador baseado na XP"""
    # Fórmula: level = 1 + floor(sqrt(xp / 100))
    return 1 + math.floor(math.sqrt(xp / LEVEL_UP_XP_BASE))

def calculate_xp_for_next_level(current_level):
    """Calcula a XP necessária para o próximo nível"""
    return LEVEL_UP_XP_BASE * (current_level + 1) ** 2

@bp.route('/combat/find_enemy', methods=['GET'])
@token_required
def find_enemy(current_user):
    """Encontra um inimigo aleatório baseado na área atual do jogador"""
    try:
        player_id = request.args.get('player_id')
        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400
        
        player = Player.query.get_or_404(player_id)
        current_area = player.current_area
        
        
        hp = 50 + (current_area * 10)
        attack = 5 + (current_area * 2)
        
        enemy = Enemy(
            hp=hp,
            attack=attack,
            current_area=current_area
        )
        
        db.session.add(enemy)
        db.session.commit()
        
        return jsonify({
            'message': f'Inimigo encontrado na área {current_area}!',
            'enemy': enemy.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/combat/attack_enemy', methods=['POST'])
@token_required
def attack_enemy(current_user):
    """Realiza um ataque contra um inimigo"""
    try:
        data = request.get_json() or {}
        
        player_id = data.get('player_id')
        enemy_id = data.get('enemy_id')
        
        if not player_id or not enemy_id:
            return jsonify({'error': 'player_id and enemy_id are required'}), 400
            
        player = Player.query.get_or_404(player_id)
        enemy = Enemy.query.get_or_404(enemy_id)
        
        # Jogador ataca inimigo
        enemy.hp -= player.attack
        
        combat_log = []
        combat_log.append(f"Player causou {player.attack} de dano ao inimigo!")
        
        # Verifica se o inimigo foi derrotado
        if enemy.hp <= 0:
           
            xp_gained = XP_PER_ENEMY * enemy.current_area * XP_MULTIPLIER
            money_gained = MONEY_PER_ENEMY * enemy.current_area
            
            old_level = calculate_level(player.xp)
            
            player.xp += xp_gained
            player.money += money_gained
            
            new_level = calculate_level(player.xp)
            
            # Se subiu de nível, aumenta atributos
            if new_level > old_level:
                levels_gained = new_level - old_level
                player.attack += LEVEL_UP_ATTACK_BONUS * levels_gained
                player.hp += LEVEL_UP_HP_BONUS * levels_gained
                combat_log.append(f"LEVEL UP! Jogador subiu para o nível {new_level}!")
                combat_log.append(f"Ataque aumentou para {player.attack}!")
                combat_log.append(f"HP aumentou para {player.hp}!")
            
            combat_log.append(f"Inimigo derrotado! Ganhou {xp_gained} XP e {money_gained} moedas.")
            
            
            db.session.delete(enemy)
            db.session.commit()
            
            return jsonify({
                'message': 'Vitória!',
                'combat_log': combat_log,
                'player': player.to_dict(),
                'enemy_defeated': True,
                'xp_gained': xp_gained,
                'money_gained': money_gained
            }), 200
        
     
        player.hp -= enemy.attack
        combat_log.append(f"Inimigo causou {enemy.attack} de dano ao jogador!")
        
       
        if player.hp <= 0:
            player.hp = 0  
            combat_log.append("Jogador foi derrotado!")
            
            db.session.commit()
            
            return jsonify({
                'message': 'Derrota!',
                'combat_log': combat_log,
                'player': player.to_dict(),
                'player_defeated': True
            }), 200
        
        db.session.commit()
        
       
        return jsonify({
            'message': 'Combate continua!',
            'combat_log': combat_log,
            'player': player.to_dict(),
            'enemy': enemy.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/combat/find_boss', methods=['GET'])
@token_required
def find_boss(current_user):
    """Encontra o chefe da área atual"""
    try:
        player_id = request.args.get('player_id')
        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400
        
        player = Player.query.get_or_404(player_id)
        current_area = player.current_area
        
        # Verifica se já existe um chefe para a área atual
        existing_boss = Boss.query.filter_by(current_area=current_area, defeat=False).first()
        
        if existing_boss:
            return jsonify({
                'message': f'Chefe encontrado na área {current_area}!',
                'boss': existing_boss.to_dict()
            }), 200
        
        
        hp = 150 + (current_area * 25)
        attack = 12 + (current_area * 3)
        
        boss = Boss(
            hp=hp,
            attack=attack,
            current_area=current_area,
            attemps=0,
            defeat=False
        )
        
        db.session.add(boss)
        db.session.commit()
        
        return jsonify({
            'message': f'Chefe encontrado na área {current_area}!',
            'boss': boss.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/combat/attack_boss', methods=['POST'])
@token_required
def attack_boss(current_user):
    """Realiza um ataque contra um chefe"""
    try:
        data = request.get_json() or {}
        
        player_id = data.get('player_id')
        boss_id = data.get('boss_id')
        
        if not player_id or not boss_id:
            return jsonify({'error': 'player_id and boss_id are required'}), 400
            
        player = Player.query.get_or_404(player_id)
        boss = Boss.query.get_or_404(boss_id)
        
        
        boss.attemps += 1
        
        combat_log = []
        combat_log.append(f"Tentativa #{boss.attemps} contra o chefe!")
        
        
        boss.hp -= player.attack
        combat_log.append(f"Player causou {player.attack} de dano ao chefe!")
        
        
        if boss.hp <= 0:
            
            xp_gained = XP_PER_BOSS * boss.current_area * XP_MULTIPLIER
            money_gained = MONEY_PER_BOSS * boss.current_area
            
            old_level = calculate_level(player.xp)
            
            player.xp += xp_gained
            player.money += money_gained
            
            
            boss.defeat = True
            
           
            if random.random() < 0.8: 
                player.current_area += 1
                combat_log.append(f"Área desbloqueada! Avançou para a área {player.current_area}!")
            
            new_level = calculate_level(player.xp)
            
           
            if new_level > old_level:
                levels_gained = new_level - old_level
                player.attack += LEVEL_UP_ATTACK_BONUS * levels_gained
                player.hp += LEVEL_UP_HP_BONUS * levels_gained
                combat_log.append(f"LEVEL UP! Jogador subiu para o nível {new_level}!")
                combat_log.append(f"Ataque aumentou para {player.attack}!")
                combat_log.append(f"HP aumentou para {player.hp}!")
            
            combat_log.append(f"Chefe derrotado! Ganhou {xp_gained} XP e {money_gained} moedas.")
            
            db.session.commit()
            
            return jsonify({
                'message': 'Vitória contra o Chefe!',
                'combat_log': combat_log,
                'player': player.to_dict(),
                'boss_defeated': True,
                'xp_gained': xp_gained,
                'money_gained': money_gained
            }), 200
        
       
        player.hp -= boss.attack
        combat_log.append(f"Chefe causou {boss.attack} de dano ao jogador!")
        
       
        if player.hp <= 0:
            player.hp = 0  
            combat_log.append("Jogador foi derrotado pelo chefe!")
            
            db.session.commit()
            
            return jsonify({
                'message': 'Derrota contra o Chefe!',
                'combat_log': combat_log,
                'player': player.to_dict(),
                'player_defeated': True
            }), 200
        
        db.session.commit()
        
       
        return jsonify({
            'message': 'Combate contra o Chefe continua!',
            'combat_log': combat_log,
            'player': player.to_dict(),
            'boss': boss.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/player/heal', methods=['POST'])
@token_required
def heal_player(current_user):
    """Cura o jogador à custa de dinheiro"""
    try:
        data = request.get_json() or {}
        
        player_id = data.get('player_id')
        
        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400
            
        player = Player.query.get_or_404(player_id)
        
        
        level = calculate_level(player.xp)
        heal_cost = level * 10  
        
        if player.money < heal_cost:
            return jsonify({'error': f'Dinheiro insuficiente. Necessário {heal_cost} moedas.'}), 400
        
     
        max_hp = 200 + (level * LEVEL_UP_HP_BONUS)
        heal_amount = max_hp * 0.25
        
       
        player.hp = min(player.hp + heal_amount, max_hp)
        player.money -= heal_cost
        
        db.session.commit()
        
        return jsonify({
            'message': f'Jogador curado em {heal_amount} HP por {heal_cost} moedas.',
            'player': player.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/player/stats', methods=['GET'])
@token_required
def get_player_stats(current_user):
    """Obtém estatísticas detalhadas do jogador"""
    try:
        player_id = request.args.get('player_id')
        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400
        
        player = Player.query.get_or_404(player_id)
        
        
        level = calculate_level(player.xp)
        next_level_xp = calculate_xp_for_next_level(level)
        xp_progress = player.xp - (LEVEL_UP_XP_BASE * level ** 2)
        xp_needed = next_level_xp - (LEVEL_UP_XP_BASE * level ** 2)
        xp_percentage = (xp_progress / xp_needed) * 100 if xp_needed > 0 else 100
        max_hp = 200 + (level * LEVEL_UP_HP_BONUS)
        
        # Dados de boss derrotados e progresso
        bosses_defeated = Boss.query.filter_by(defeat=True).count()
        highest_area = player.current_area
        
        return jsonify({
            'player': player.to_dict(),
            'stats': {
                'level': level,
                'xp_for_next_level': next_level_xp,
                'xp_progress': xp_progress,
                'xp_needed': xp_needed,
                'xp_percentage': xp_percentage,
                'max_hp': max_hp,
                'current_hp_percentage': (player.hp / max_hp) * 100,
                'bosses_defeated': bosses_defeated,
                'highest_area': highest_area
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
