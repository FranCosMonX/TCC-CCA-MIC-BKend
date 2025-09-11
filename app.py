from flask import Flask, request, jsonify
from flask_cors import CORS
from bd import (
  atualizar_apelido,
  atualizar_dadosConf_gerais,
  atualizar_dados_mic,
  criar_config_default, 
  init_db, 
  obter_configuracao, 
)
from services.germini import Enviar_Mensagem, alterarPrompting
import sqlite3

app = Flask(__name__)

@app.route('/initdb')
def initialize_database():
  init_db()
  return 'database inicializado'

@app.route('/configuracao/apelido', methods=['POST'])
def definir_apelido():
  try:
    criar_config_default()
  except Exception as e:
    return jsonify({'error': str(e)}), 500
  
  apelido = request.json.get('apelido')
  
  if not apelido:
    return jsonify({
      'error': 'Para atualizar o apelido, é necessário que seja passado um nome válido.'
    })
  try:
    resultado = atualizar_apelido(apelido)
    return jsonify({'mensagem': resultado}), 201
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/configuracaoGeral', methods=['POST'])
def definir_conf_geral():
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
  try:
    resultado = obter_configuracao()
    return jsonify(resultado), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def emviar_mensagem():
  mensagem = request.json.get('mensagem')
  print('executou')
  if not mensagem:
    return jsonify({
      'error': 'É necessário acrescentar alguma informação no chat.'
    }), 400
  
  resposta = Enviar_Mensagem(mensagem)
  print(resposta)
  return jsonify({
      'mensagem': resposta.text
    }), 200
  
@app.route('/usuario', methods=['POST'])
def definir_usr():
  usr = request.json.get('usuario')
  
  if len(usr) < 2 or not usr:
    return jsonify({
      'error': 'O campo não pode ser nulo ou conter menos de 3 carcteres'
    }), 400
  
  try:
    resposta = atualizar_apelido(usr)
    return jsonify({
      'mensagem': resposta
    }), 200
  except Exception as e:
    print(e)
    return jsonify({
      'error': f'{e}'
    }), 400

# Iniciar a aplicação Flask
if __name__ == '__main__':
  CORS(app, resources={
    r"/*": {"origins": "http://localhost:5173"},
  })
  app.run(host='localhost', port=5000, debug=True)