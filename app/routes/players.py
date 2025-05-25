from flask import jsonify, request
from app import db
from app.models import Player
from app.routes import bp
from app.auth import token_required

@bp.route('/players', methods=['GET'])
@token_required
def get_players(current_user):
    # recupera uma id de player que pode ter sido passado por parâmetro
    player_id = request.args.get('player_id')

    # se existir uma id de player
    if player_id:
        try:
            player = Player.query.get_or_404(player_id)
            return jsonify(player.to_dict()), 200 # sucesso na requisição
        except Exception as e:
            return jsonify({'erro': str(e)})
    else:
        # se não tem um id, manda todos os playeres
        try:
            players = Player.query.all()
            return jsonify([player.to_dict() for player in players]), 200 # sucesso na requisição
        except Exception as e:
            return jsonify({'erro': str(e)})



@bp.route('/players', methods=['POST'])
@token_required
def create_player(current_user):
    try:
        # recuperar o conteudo do json
        data = request.get_json() or {}

        #if 'username' not in data or 'password'  not in data:
        #    return jsonify({'error': 'Username and Password are required'})
        #if Player.query.filter_by(email=data['email']).first():
        # if Player.query.filter_by(email="andrei.carniel@catolicasc.com.br").first():
        #    return jsonify({'error': 'Email already exists'})

        player = Player(hp=200, attack=10, current_area=1, money=0, xp=0)
        db.session.add(player)
        db.session.commit()

        return jsonify(player.to_dict()), 201 # sucesso na criação
    except Exception as e:
        return jsonify({'error': str(e)}), 500 # erro de servidor
        
@bp.route('/players/<int:player_id>', methods=['PUT'])
@token_required
def update_player(current_user, player_id):
    try:
        player = Player.query.get_or_404(player_id)
        data = request.get_json() or {}
        
 
        if 'hp' in data:
            player.hp = data['hp']
        if 'attack' in data:
            player.attack = data['attack']
        if 'current_area' in data:
            player.current_area = data['current_area']
        if 'money' in data:
            player.money = data['money']
        if 'xp' in data:
            player.xp = data['xp']
            
        db.session.commit()
        return jsonify(player.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
