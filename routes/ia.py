from flask import Blueprint, jsonify, request
from bd import add_modelo_ia, obter_modelo_por_nome_ia, obter_modelos_disponiveis, obter_modelo_por_id, obter_ias_disponiveis, tem_modelo_da_ia, atualiza_chave_acesso_ai, edit_validacao_api_key, obter_configuracao
from common.exceptions import UsuarioError
from services.germini import atualiza_api_key_ou_modelo, verificar_conexao

ia_bp = Blueprint("ia", __name__)

@ia_bp.route('/ia/reconectar', methods=['POST'])
def reconectar():
  try:
    configuracao = obter_configuracao()
    modelo_bd = configuracao.get('modelo_disponivel')
    api_key_bd = configuracao.get('key_ai_api')
    nome_ia_bd = configuracao.get('nome_ia')

    mensagem_error = ""
    if modelo_bd is None:
      mensagem_error += "Falta escolher um modelo de IA para ser utilizado."
    if api_key_bd is None:
      mensagem_error += "Falta informar a Chave de acesso para se conectar a API da IA."
    if nome_ia_bd is None:
      mensagem_error += "Não foi informado qual a IA será utilizada."

    if mensagem_error != "":
      resultado_v_conecxao = verifica_conexao()
      if resultado_v_conecxao:
        return jsonify({
          'mensagem': mensagem_error
        }), 400
      else:
        return jsonify({
          'mensagem': "Não foi possivel obter uma resposta da API da IA."
        }), 404

    resposta = verificar_conexao(True,api_key_bd, modelo_bd)

    if resposta:
      return jsonify({'mensagem': 'conexão recuperada.'}), 200
    else:
      return jsonify({'mensagem': 'não foi possivel se conectar novamente, tente novamente mais tarde.'})
  except Exception as e:
    return jsonify({
      'mensagem': e
    })

@ia_bp.route('/ia/verificaConexao', methods=['POST'])
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
  modelo = request.json.get('modelo')

  if ia is None or modelo is None or ia == "" or modelo == "":
    return jsonify({
      'mensagem': "Faltam dados para verificar a conexão com o servidor da IA."
    }), 400

  id_modelo_ia = tem_modelo_da_ia(ia, modelo)
  if id_modelo_ia is None:
    return jsonify({
      'mensagem': "A aplicação só suporta a ligação com alguns modelos no momoento."
    }), 400

  print(id_modelo_ia)
  try:
    atualiza_api_key_ou_modelo(api, modelo)
    atualiza_chave_acesso_ai(id_modelo_ia, api)
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

@ia_bp.route('/ia/adicionarModelo', methods=['POST'])
def adicionarModeloIA():
  nome_ia = request.json.get('nome_ia')
  modelo = request.json.get('modelo')

  campos_faltantes = []
  if nome_ia is None or nome_ia == "":
    campos_faltantes.append("nome_ia")

  if modelo is None or modelo =="":
    campos_faltantes.append("modelo")

  if len(campos_faltantes) > 0:
    return jsonify({
      "mensagem": "Solicitação incompleta devido a falta de informações.",
      "campos": campos_faltantes
    }), 404
  
  try:
    add_modelo_ia(nome_ia, modelo)
    return jsonify({
      "mensagem": "Modelo de IA salvo com sucesso."
    }), 200
  except UsuarioError as e:
    print(e)
    return jsonify({
      'mensagem': "Houve um problema em salvar os dados fornecidos. O nome do modelo é a provável causa."
    }), 400
  except:
    return jsonify({
      'mensagem': "Houve algum problema em salvar os dados da IA."
    }), 500

@ia_bp.route('/ias', methods=['GET'])
def obter_ias_registradas():
  resultado = obter_ias_disponiveis()
  if resultado is None:
    return jsonify("Nenhum modelo de IA registrado"), 404
  return jsonify(resultado), 200

@ia_bp.route('/ias/modelos', methods=['GET'])
def obter_modelos_de_ia_disponiveis():
  resultado = obter_modelos_disponiveis()
  if resultado is None:
    return jsonify("Nenhum modelo de IA registrado"), 404
  return jsonify(resultado), 200

@ia_bp.route('/ias/nome/<nome_ia>', methods=['GET'])
def obter_dados_por_nome_ia(nome_ia):
  try:
    lista = obter_modelo_por_nome_ia(str(nome_ia))
  
    if lista is None:
      return jsonify({
        "mensagem": f"Não há modelos disponíveis para a IA {nome_ia}." 
      }), 404
    
    return jsonify({
      "mensagem": "Modelos encontrados com sucesso.",
      "modelos": lista
    }), 200
      
  except Exception as e:
    print(f"DEBUG - {e}")
    return jsonify({
      "mensagem": "Houve um problema inesperado no servidor."
    }), 500

@ia_bp.route('/ias/id/<id_ia>', methods=['GET'])
def obter_modelo_por_ia_id(id_ia):
  try:
    resultado = obter_modelo_por_id(id_ia)
    if resultado is None:
      return jsonify({"mensagem": "IA não encontrada"}), 400
    return jsonify(resultado), 200
  except Exception as e:
    print(f"DEBUG - {e}")
    return jsonify({
      "mensagem": "Houve um problema inesperado no servidor."
    }), 500