from flask import Blueprint, jsonify, request
from common.exceptions import UsuarioError, IAError, SistemaError
from enums.ia import IAName
from utils.registro import obter_registro_as_str
from bd import (
  obter_modelo_por_nome_ia,
  obter_modelos_disponiveis,
  obter_modelo_por_id,
  obter_ias_disponiveis,
  tem_modelo_da_ia,
  atualiza_chave_acesso_ai,
  edit_validacao_api_key,
  obter_configuracao
)
from services.gemini import (
  alterar_api_key as alterar_api_key_gemini,
  alterar_modelo as alterar_modelo_gemini,
  testar_conexao as testar_conexao_gemini,
  conexao_ok as conexao_ok_gemini,
  carregar_contexto_anterior as carregar_contexto_anterior_gemini
)
from services.chatgpt import (
  alterar_api_key as alterar_api_key_chatgpt,
  alterar_modelo as alterar_modelo_chatgpt,
  testar_conexao as testar_conexao_chatgpt,
  conexao_ok as conexao_ok_chatgpt,
  carregar_contexto_anterior as carregar_contexto_anterior_chagpt
)

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

    if nome_ia_bd == IAName.GEMINI:
      print(f"conexao: {conexao_ok_gemini}")
      if not conexao_ok_gemini:
        alterar_api_key_gemini(api_key_bd)
        alterar_modelo_gemini(modelo_bd)
      resposta = testar_conexao_gemini()
    elif nome_ia_bd == IAName.CHATGPT:
      print(f"conexao: {conexao_ok_chatgpt}")
      if not conexao_ok_chatgpt:
        alterar_api_key_chatgpt(api_key_bd)
        alterar_modelo_chatgpt(modelo_bd)
      resposta = testar_conexao_chatgpt()
    else:
      edit_validacao_api_key(False)
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    
    if resposta:
      return jsonify({'mensagem': 'conexão recuperada.'}), 200
    else:
      return jsonify({'mensagem': 'não foi possivel se conectar novamente, tente novamente mais tarde.'})
  except UsuarioError as errU:
    return jsonify({
      'mensagem': errU.mensagem
    }), 400
  except IAError as iE:
    edit_validacao_api_key(False)
    return jsonify({
      'mensagem': f'Houve um problema inesperado com relação aos serviços de IA. {iE}'
    }), 500
  except SistemaError as sE:
    # print(sE)
    return jsonify({
      'mensagem': sE.mensagem
    }), 500
  except Exception as e:
    return jsonify({
      'mensagem': e
    })

@ia_bp.route('/ia/verificaConexao', methods=['POST'])
def verifica_conexao():
  """
  Usado para verificar a conexão com a AI. É enviado uma requisição simples.
  
  Raises:
    200: Conexão bem sucedida.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
  ia_param = request.json.get('ia')
  api_key_param = request.json.get('key_ai_api')
  modelo_param = request.json.get('modelo')

  if ia_param is None or modelo_param is None or ia_param == "" or modelo_param == "":
    return jsonify({
      'mensagem': "Faltam dados para verificar a conexão com o servidor da IA."
    }), 400

  id_modelo_ia = tem_modelo_da_ia(ia_param, modelo_param)
  if id_modelo_ia is None:
    return jsonify({
      'mensagem': "A aplicação só suporta a ligação com alguns modelos no momoento."
    }), 400

  try:
    if ia_param == IAName.GEMINI:
      alterar_api_key_gemini(api_key_param)
      alterar_modelo_gemini(modelo_param)
      testar_conexao_gemini()
    elif ia_param == IAName.CHATGPT:
      alterar_api_key_chatgpt(api_key_param)
      alterar_modelo_chatgpt(modelo_param)
      testar_conexao_chatgpt()
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    
    atualiza_chave_acesso_ai(id_modelo_ia, api_key_param)
    edit_validacao_api_key(True)
    return jsonify({
      'mensagem': 'Conectado com sucesso'
    }), 200
  except UsuarioError as errU:
    return jsonify({
      'mensagem': errU.mensagem
    }), 400
  except IAError as iE:
    edit_validacao_api_key(False)
    return jsonify({
      'mensagem': f'Houve um problema inesperado com relaçãõ aos serviços de IA. {iE}'
    }), 500
  except Exception as e:
    return jsonify({
      'mensagem': f'Houve um problema em armazenar chave da API_KEY. {e}'
    }), 500

@ia_bp.route('/ia/carregar_contexto_anterior', methods=['POST'])
def carregar_contexto_anterior_route():
  """
  Usado para enviar o histórico de mensagens para a IA criada após a reconexão (nova sessão de conversas)

  Raises:
    200: Contexto enviado com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
  registro = obter_registro_as_str()

  if not registro or len(registro) == 0:
    return jsonify({'mensagem': 'Não foi encontrado registro de conversa anterior.'}), 404

  configuracao = obter_configuracao()
  nome_ia_db = configuracao.get('nome_ia')

  try:
    if nome_ia_db == IAName.GEMINI:
      carregar_contexto_anterior_gemini(registro)
    elif nome_ia_db == IAName.CHATGPT:
      carregar_contexto_anterior_chagpt(registro)
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404

    return jsonify({'mensagem': 'Contexto enviado para a nova sessão de chat.'}), 200
  except UsuarioError as errU:
    return jsonify({
      'mensagem': errU.mensagem
    }), 400
  except IAError as iE:
    edit_validacao_api_key(False)
    return jsonify({
      'mensagem': f'Houve um problema inesperado com relaçãõ aos serviços de IA. {iE}'
    }), 500
  except SistemaError as sE:
    # print(sE)
    return jsonify({
      'mensagem': sE.mensagem
    }), 500
  except Exception as e:
    return jsonify({
      'mensagem': f'Houve um problema em armazenar chave da API_KEY. {e}'
    }), 500


@ia_bp.route('/ias', methods=['GET'])
def obter_ias_registradas():
  """
  Usado para obter todas as IAs cujos modelos são compatíveis com a aplicação.
  
  Raises:
    200 (Object Json): Solicitação atendida.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
  resultado = obter_ias_disponiveis()
  if resultado is None:
    return jsonify("Nenhum modelo de IA registrado"), 404
  return jsonify(resultado), 200

@ia_bp.route('/ias/modelos', methods=['GET'])
def obter_modelos_de_ia_disponiveis():
  """
  Usado para obter todos os modelos de uma IA em especifica, cujo o nome é passado pelo cliente.

  Raises:
    200 (Object Json): Solicitação atendida.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
  resultado = obter_modelos_disponiveis()
  if resultado is None:
    return jsonify("Nenhum modelo de IA registrado"), 404
  return jsonify(resultado), 200

@ia_bp.route('/ias/nome/<nome_ia>', methods=['GET'])
def obter_dados_por_nome_ia(nome_ia):
  """
  usado para obter o modelo por nome da IA passado pelo cliente.
  
  Raises:
    200 (Object Json): Solicitação atendida.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
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
  """
  Usado para obter o modelo por ID passado c=pelo cliente.

  Raises:
    200 (Object Json): Solicitação atendida.
    400: Campo ou alguma entrada de usuário incorreta.
    404: Recurso não existe.
    500: Problemas com o backend.
  """
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