from flask import Flask, request, jsonify
from flask_cors import CORS
from common.archive import (
  criar_diretorios,
  criar_arquivo_bat,
  execute_bat
)
from bd import (
  atualizar_apelido,
  atualizar_dadosConf_gerais,
  atualizar_dados_mic,
  criar_config_default, 
  init_db, 
  obter_configuracao, 
)
from services.germini import (
  Enviar_Mensagem,
  alterarPrompting,
  verificar_conexao
)
import json

app = Flask(__name__)

@app.route('/initdb')
def initialize_database():
  init_db()
  criar_arquivo_bat()
  execute_bat()

  return jsonify({
    'mensagem': 'Requisitos iniciados com sucesso'
  }), 200

@app.route('/verifica_conexao')
def verifica_conexao():
  result = verificar_conexao()
  if result :
    return jsonify({
      'mensagem': 'Conectado com sucesso'
    }), 200
  else :
    return jsonify({
      'mensagem': 'Não foi possivel se conectar ao serviço de IA.'
    })

@app.route('/compile_exec')
def exec_comp():
  pass

@app.route('/configuracaoGeral', methods=['POST'])
def definir_conf_geral():
  """
  Descrição:
  
    Usado para mudar parâmetros do microcontrolador usados na conversa com a AI. É bastante importante para 
  Retorno:
  
    201: Dados salvos com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  try:
    criar_config_default()
  except Exception as e:
    return jsonify({'error': str(e)}), 500
  
  diretorio = request.json.get('diretorio')
  ai = request.json.get('ai')
  key_ai_api = request.json.get('key_ai_api')
  ver_codigo = request.json.get('ver_codigo')
  comentario_codigo = request.json.get('comentario_codigo')
  
  if not diretorio or not ai or not key_ai_api:
    return jsonify({
      'error': 'O caminho da pasta onde os arquivos serão salvos, a InteligÊncia Artificial que será usada e a chave de acesso para acessar a API da AI escolhida são obrigatórios.'
    }), 400
  
  try:
    msg = atualizar_dadosConf_gerais(diretorio,ai,key_ai_api,ver_codigo,comentario_codigo)
    alterarPrompting(f"comentario do código: {comentario_codigo}, visualizar codigo: {ver_codigo}")
    return jsonify({
      'mensagem': msg,
      'dados':{
        'diretorio': diretorio,
        'ai': ai,
        'key_ai_api': key_ai_api,
        'ver_codigo': ver_codigo,
        'comentario_codigo': comentario_codigo
      }
    }), 201
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/configuracaoMicrocontrolador', methods=['POST'])
def definir_conf_mic():
  """
  Descrição:
  
    Usado para mudar parâmetros do microcontrolador usados na conversa com a AI. É bastante importante para 
  Retorno:
  
    200: Parâmetros salvos com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  mic = request.json.get('microcontrolador')
  
  if not mic:
    return jsonify({
      'error': 'É necessário escolher o microcontrolador para continuar.'
    }), 400
  
  try:
    resultado = atualizar_dados_mic(mic)
    
    alterarPrompting(f"Microcontrolador: {mic}")
    return jsonify({'mensagem': resultado}), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500

# Rota para obter todos os dados
@app.route('/configuracao', methods=['GET'])
def get_dados():
  """
  Descrição:
  
    Usado para mudar parâmetros de configuração usados na conversa com a AI.
  Retorno:
  
    200: Parâmetros salvos com sucesso.
    500: Problemas com o backend.
  """
  try:
    resultado = obter_configuracao()
    return jsonify(resultado), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def emviar_mensagem():
  """
  Descrição:
  
    Usado para enviar uma solicitação para a AI.

  Retorno:
  
    200: Alterado com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  mensagem = request.json.get('mensagem')

  if not mensagem:
    return jsonify({
      'error': 'É necessário acrescentar alguma informação no chat.'
    }), 400
  
  resposta = Enviar_Mensagem(mensagem).text
  try:
    return jsonify({
      'mensagem': resposta
    }), 200
  except json.JSONDecodeError as e:
    print(f"{resposta}")
    return jsonify({
      'mensagem': resposta
    }), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500
  
@app.route('/usuario', methods=['POST'])
def definir_usr():
  """
  Descrição:
  
    Usado para atualizar ou criar o nome do usuário na aplicação. É usado apenas pela AI para se comunicar com o usuário.

  Retorno:
  
    200: Alterado com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
  """
  usr = request.json.get('usuario')
  
  if len(usr) < 2 or not usr:
    return jsonify({
      'error': 'O campo não pode ser nulo ou conter menos de 3 carcteres'
    }), 400
  
  try:
    resposta = atualizar_apelido(usr)
    alterarPrompting(f"usuário: {usr}")
    return jsonify({
      'mensagem': resposta
    }), 200
  except Exception as e:
    return jsonify({
      'error': f'{e}'
    }), 400
    
# COMPILAR

@app.route('/compile')
def compile():
  criar_diretorios('executavel')
  
  
  pass

# Iniciar a aplicação Flask
if __name__ == '__main__':
  CORS(app, resources={
    r"/*": {"origins": "http://localhost:5173"},
  })
  app.run(host='localhost', port=5000, debug=True)