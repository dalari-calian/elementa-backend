from app import create_app, db
from app.models import Player

# cria a instância do aplicativo
app = create_app()

@app.shell_context_processor
def make_shell_context():
    # pode executar comandos shell durante a execução
    # do app
    return { 'db': db, 'Player': Player }


# flask db init >> executa a primeira vez
# flask db migrate >> executa sempre que tiver alteração nos objetos
# flask db upgrade >> executa sempre que tiver alteração nos objetos
# flask run >> é pra rodar a aplicação
