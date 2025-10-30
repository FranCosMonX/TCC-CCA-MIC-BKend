from flask import Flask, request, jsonify
from flask_cors import CORS
from common.archive import (
  criar_diretorios
)
from common.exceptions import (
  UsuarioError,
  SistemaError
)
from bd import (
  atualizar_apelido,
  atualiza_chave_acesso_ai,
  atualizar_dadosConf_gerais,
  atualizar_dados_mic,
  atualiza_config_default,
  criar_config_default,
  edit_validacao_api_key,
  init_db, 
  obter_configuracao,
)
from services.germini import (
  Enviar_Mensagem,
  alterarPrompting,
  atualiza_api_key,
  carregar_dados_salvos,
  iniciar,
)
from features.ambiente import (
  preparando_ambiente
)
import json

app = Flask(__name__)
CORS(app,
     resources={
      r"/*": {"origins": "http://localhost:5173"},
    }
  )

@app.route('/initdb')
def initialize_database():
  """
  Primeiro Endpoint que deverá ser chamado para a inicialização do Banco de Dados.

  Returns:
  
    201: Dados salvos com sucesso.
    500: Problemas com o backend.
  """
  
  try:
    configuracao = obter_configuracao()
    
    if configuracao['id_microcontrolador'] is not None or configuracao['key_ai_api'] is not None or configuracao['diretorio'] is not None:
      return jsonify({
        'mensagem': 'Já existe arquivo e dados salvos.'
      }), 200
    
    return jsonify({
      'mensagem': 'teste'}), 204
  except:
    try:
      init_db()
      criar_config_default()

      return jsonify({
        'mensagem': 'Banco de Dados inicializado com êxito.'
      }), 201
    except Exception as e:
      print("===================================")
      print(e)
      return jsonify({
        'mensagem': 'Houve um problema ao executar o script de criação do Banco de Dados local.'
      }), 500

@app.route('/RemoverConfiguracao', methods=['POST'])
def remover_configuracao():
  """
  Usado para remover todas as configurações salvas no banco de dados.
  """
  
  try:
    atualiza_config_default()
    # init_db()
    # criar_config_default()
    return jsonify({
      'mensagem': 'Dados resetados com sucesso.'
    }), 200
  except:
    return jsonify({
      'mensagem': 'Houve um problema ao resetar os dados.'
    }), 500

@app.route('/CarregarConfiguracao', methods=['POST'])
def carregar_configuracao():
  """
  É necessário que tenha o arquivo de banco de dados gerado.
  """
  configuracao = obter_configuracao()
  mensagem = ""
  execucao = [configuracao['id_microcontrolador'] is not None, configuracao['key_ai_api'] is not None, configuracao['diretorio'] is not None]
  try:
    preparando_ambiente(configuracao['id_microcontrolador'])
    mensagem += "Ambiente de execução configurado com exito."
    execucao[0] = True
  except Exception as e:
    mensagem += 'Não há dados suficientes para preparar o ambiente de execução de código.'
  
  try:
    atualiza_api_key(configuracao['key_ai_api'])
    mensagem += "Conexão com a IA realizada com êxito."
    execucao[1] = True
  except Exception as e:
    mensagem += "Não há dados suficientes para tentar se conectar a API da IA."
  
  if not configuracao['diretorio']:
    mensagem += "O campo diretório se encontra vazio, preencha o campo corretamente."
  else:
    execucao[2] = True
  
  if execucao[0] or execucao[1] or execucao[2]:
    return jsonify({
      'mensagem': mensagem
    }), 200
  else:
    try:
      atualiza_config_default()
      return jsonify({
        'mensagem': "Não foi possivel realizar esta ação. Atualize os dados."
      }), 400
    except Exception as e:
      return jsonify({
        'mensagem': e
      }), 500

@app.route('/verificaConexao', methods=['POST'])
def verifica_conexao():
  """
  Usado para verificar a conexão com a AI. É enviado uma requisição simples.
  Returns:
  
    200: Conexão bem sucedida.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  ia = request.json.get('ia')
  api = request.json.get('key_ai_api')

  if ia != "Germini":
    return jsonify({
      'mensagem': "A aplicação só suporta a ligação com o Germini no momento."
    }), 400

  try:
    atualiza_api_key(api)
    atualiza_chave_acesso_ai(ia, api)
    edit_validacao_api_key(True)
    return jsonify({
      'mensagem': 'Conectado com sucesso'
    }), 200
  except UsuarioError as errU:
    return jsonify({
      'mensagem': errU.mensagem
    }), 400
  except Exception as e:
    return jsonify({
      'mensagem': 'Houve um problema em armazenar chave da API_KEY.'
    }), 500

@app.route('/configuracaoGeral', methods=['POST'])
def definir_conf_geral():
  """
  Descrição:
  
    Usado para mudar parâmetros do microcontrolador usados na conversa com a AI. É bastante importante para 
  Returns:
  
    201: Dados salvos com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  
  nome_projeto = request.json.get('nome_projeto')
  diretorio = request.json.get('diretorio')
  key_ai_api = request.json.get('key_ai_api')
  ver_codigo = request.json.get('ver_codigo')
  comentario_codigo = request.json.get('comentario_codigo')
  
  configuracao = obter_configuracao()
  status_chave_verificada = configuracao['api_key_valid']
  chave_verificada = configuracao["key_ai_api"]
  
  print(f'chave verificada: {status_chave_verificada}')
  if not status_chave_verificada:
    return jsonify({
      'mensagem': "Primeiro verifique se a chave de acesso é válida.",
      'campo': 'key_ai_api'
    }), 400
    
  if  chave_verificada != key_ai_api:
    return jsonify({
      'mensagem': "Houve a alteração da chave de acesso após confirmar sua validação. Inclua a mesma ou valide uma nova.",
      'campo': 'key_ai_api'
    }), 400
    
  if not nome_projeto:
    return jsonify({
      'mensagem': 'O campo não pode ser nulo',
      'campo': 'nomeDoProjeto'
    }), 400
  
  if not diretorio or len(diretorio) < 3:
    return jsonify({
      'mensagem': 'O caminho onde os arquivos serão salvos é invalido.',
      'campo': 'diretorio'
    }), 400
  
  try:
    msg = atualizar_dadosConf_gerais(nome_projeto, diretorio,ver_codigo,comentario_codigo)
    alterarPrompting(f"comentario do código: {comentario_codigo}, visualizar codigo: {ver_codigo}, o nome do projeto é: {nome_projeto}")
    return jsonify({
      'mensagem': msg,
      'dados':{
        'diretorio': diretorio,
        'key_ai_api': key_ai_api,
        'ver_codigo': ver_codigo,
        'comentario_codigo': comentario_codigo,
        'nome_projeto': nome_projeto
      }
    }), 200
  except Exception as e:
    print(f"{e}")
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
  id_mic = request.json.get('id_microcontrolador')
  mic = request.json.get('microcontrolador')
  
  if not mic:
    return jsonify({
      'mensagem': 'É necessário escolher o microcontrolador para continuar.'
    }), 400
  
  try:
    carregar_dados_salvos()
  except UsuarioError as userError:
    return jsonify({
      'mensagem': userError.mensagem
    }), 400
  except SistemaError as sysError:
    return jsonify({
      'mensagem': "Houve um erro inesperado no sistema. Contacte o desenvolvedor."
    }), 500
  
  try:
    resultado = atualizar_dados_mic(id_mic,mic)
    alterarPrompting(f"Microcontrolador: {mic}")
  except Exception as e:
    print(e)
    return jsonify({'mensagem': str(e)}), 500
  
  try:
    preparando_ambiente(id_mic)
  except Exception as e:
    print(e)
    return jsonify({'error': str(e)}), 500
  
  return jsonify({'mensagem': "Ambiente de trabalho configurado com êxito."}), 200

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
  
  configuracao = obter_configuracao()
  if configuracao['microcontrolador'] is None:
    return jsonify({
      'mensagem': 'Antes de começar, é necessário preparar o ambiente de trabalho.'
    }), 400
    
  if not configuracao['api_key_valid']:
    return jsonify({
      'mensagem': 'É necessário passar uma chave de acesso para a IA que seja válida'
    }), 400
  
  if len(usr) < 2 or not usr:
    return jsonify({
      'mensagem': 'O campo não pode ser nulo ou conter menos de 3 carcteres'
    }), 400
  
  try:
    resposta = atualizar_apelido(usr)
    alterarPrompting(f"usuário: {usr}")
    iniciar()
    return jsonify({
      'mensagem': resposta
    }), 200
  except Exception as e:
    print(e)
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
  app.run(host='localhost', port=5000, debug=True)