import requests
import json


BASE_URL = 'http://localhost:5000'

def test_api():

    print("1. Realizando login...")
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"Erro no login: {response.text}")
        return
    
    token = response.json()['token']
    print(f"Login bem-sucedido! Token: {token[:20]}...")
   
    headers = {
        'x-access-token': token,
        'Content-Type': 'application/json'
    }
     
    print("\n2. Criando um novo jogador...")
    headers_with_content = headers.copy()
    headers_with_content['Content-Type'] = 'application/json'
    response = requests.post(f'{BASE_URL}/players', headers=headers_with_content, json={})
    if response.status_code != 201:
        print(f"Erro ao criar jogador: {response.text}")
        return
    
    player = response.json()
    player_id = player['id']
    print(f"Jogador criado com sucesso! ID: {player_id}")
    print(f"Estatísticas iniciais: HP={player['hp']}, Ataque={player['attack']}, Área={player['current_area']}")
    
   
    print("\n3. Procurando um inimigo...")
    response = requests.get(f'{BASE_URL}/combat/find_enemy?player_id={player_id}', headers=headers)
    if response.status_code != 200:
        print(f"Erro ao procurar inimigo: {response.text}")
        return
    
    enemy = response.json()['enemy']
    enemy_id = enemy['id']
    print(f"Inimigo encontrado! ID: {enemy_id}")
    print(f"Estatísticas do inimigo: HP={enemy['hp']}, Ataque={enemy['attack']}")
    
  
    print("\n4. Atacando o inimigo...")
    combat_data = {
        'player_id': player_id,
        'enemy_id': enemy_id
    }
    
  
    combat_round = 1
    while True:
        print(f"\nRound {combat_round}:")
        response = requests.post(f'{BASE_URL}/combat/attack_enemy', headers=headers, json=combat_data)
        if response.status_code != 200:
            print(f"Erro no combate: {response.text}")
            break
        
        result = response.json()
        
       
        for log_entry in result.get('combat_log', []):
            print(f"  {log_entry}")
        
       
        if result.get('enemy_defeated', False):
            print(f"\nInimigo derrotado!")
            print(f"XP ganho: {result.get('xp_gained', 0)}")
            print(f"Dinheiro ganho: {result.get('money_gained', 0)}")
            break
        elif result.get('player_defeated', False):
            print(f"\nJogador derrotado!")
            break
        
    
        player_hp = result['player']['hp']
        enemy_hp = result['enemy']['hp']
        print(f"  HP do Jogador: {player_hp}, HP do Inimigo: {enemy_hp}")
        
        combat_round += 1
    
   
    print("\n5. Verificando conquistas...")
    achievement_data = {
        'enemies_defeated': 1,
        'bosses_defeated': 0
    }
    response = requests.post(f'{BASE_URL}/players/{player_id}/check_achievements', headers=headers, json=achievement_data)
    if response.status_code != 200:
        print(f"Erro ao verificar conquistas: {response.text}")
        return
    
    achievements = response.json()
    if achievements['newly_unlocked']:
        print("Novas conquistas desbloqueadas:")
        for achievement in achievements['newly_unlocked']:
            print(f"  {achievement['achievement']['name']}: {achievement['achievement']['description']}")
            print(f"  Recompensas: {achievement['rewards']['xp']} XP, {achievement['rewards']['money']} moedas")
    else:
        print("Nenhuma nova conquista desbloqueada.")
    

    print("\n6. Estatísticas atualizadas do jogador...")
    response = requests.get(f'{BASE_URL}/player/stats?player_id={player_id}', headers=headers)
    if response.status_code != 200:
        print(f"Erro ao obter estatísticas: {response.text}")
        return
    
    stats = response.json()
    player = stats['player']
    player_stats = stats['stats']
    
    print(f"Jogador ID {player_id}:")
    print(f"  HP: {player['hp']}")
    print(f"  Ataque: {player['attack']}")
    print(f"  Área atual: {player['current_area']}")
    print(f"  Dinheiro: {player['money']}")
    print(f"  XP: {player['xp']}")
    print(f"  Nível: {player_stats['level']}")
    print(f"  Progresso para próximo nível: {player_stats['xp_percentage']:.1f}%")
    
    print("\nTeste da API concluído com sucesso!")

if __name__ == "__main__":
    test_api()
