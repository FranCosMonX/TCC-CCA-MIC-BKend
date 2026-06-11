from flask import Blueprint, jsonify, request
from services.gemini import (
  enviar_mensagem as enviar_mensagem_gemini,
  iniciar_chat as iniciar_chat_gemini,
  testar_conexao as testar_conexao_gemini,
  alterar_api_key as alterar_api_key_gemini,
  alterar_modelo as alterar_modelo_gemini
)
from services.chatgpt import (
  enviar_mensagem as enviar_mensagem_chatgpt,
  iniciar_chat as iniciar_chat_chatgpt,
  testar_conexao as testar_conexao_chatgpt,
  alterar_api_key as alterar_api_key_chatgpt,
  alterar_modelo as alterar_modelo_chatgpt
)
from enums.ia import IAName
from common.exceptions import (
  UsuarioError, IAError
)
from utils.registro import (
  registrar_mensagem_chat,
  obter_registro_as_str
)
from bd import (
  obter_configuracao,
  excluir_registro_chat_de_conversa,
  obter_registros_chat
)
import json

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/IniciarChat', methods=['POST'])
def iniciar_chat_route():
  """
  Descrição
  
    Usado para iniciar o chat, enviando todos os prompts para a IA. Caso tenha dados salvos, a conexão será feita, se ainda não estiver.
    
  Retorno:
  
    200: Iniciado com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  try:
    configuracao = obter_configuracao()
    api_valid_bd = configuracao.get('api_key_valid')
    ambiente_valid_bd = configuracao.get('ambiente_configurado')
    nome_projeto_bd = configuracao.get('nome_projeto')
    nome_ia_bd = configuracao.get('nome_ia')
    modelo_bd = configuracao.get('modelo_disponivel')
    api_key_bd = configuracao.get('key_ai_api')

    mensagem_error = ""
    if nome_projeto_bd is None:
      mensagem_error += "É necessário informar o nome do projeto para começar."
    if not api_valid_bd or not api_key_bd or not modelo_bd:
      mensagem_error += "É necessário definir as configurações de conexão com a API da IA."
    if not ambiente_valid_bd:
      mensagem_error += "É necessário estar com o ambiente de desenvolvimento configurado. Escolha o microcontrolador para que o código possa ser gerado corretamente."

    if mensagem_error != "":
      return jsonify({
        'mensagem': "É necessário que corrija algumas pendências:\n" + mensagem_error
      }), 400
    
    status_conectado = False
    if nome_ia_bd == IAName.GEMINI:
      status_conectado = testar_conexao_gemini()
      print(status_conectado)
      if status_conectado:
        iniciar_chat_gemini()
      else:
        alterar_api_key_gemini(api_key_bd)
        alterar_modelo_gemini(modelo_bd)
        status_conectado = testar_conexao_gemini()
        print(status_conectado)
        iniciar_chat_gemini()
    elif nome_ia_bd == IAName.CHATGPT:
      status_conectado = testar_conexao_chatgpt()
      if status_conectado:
        iniciar_chat_chatgpt()
      else:
        alterar_api_key_chatgpt(api_key_bd)
        alterar_modelo_chatgpt(modelo_bd)
        testar_conexao_chatgpt()
        iniciar_chat_chatgpt()
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    return jsonify({
      'mensagem': "Chat Iniciado"
    }), 200
  except UsuarioError as uE:
    print(f"{uE}")
    return jsonify({
      'mensagem': str(uE)
    }), 400
  except IAError as iE:
    print(f"{iE}")
    return jsonify({
      'mensagem': str(iE)
    }), 429
  except Exception as e:
    print(e)
    return jsonify({
      'mensagem': str(e)
    }), 500

@chat_bp.route('/chat', methods=['POST'])
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
  
  nome_ia_bd = obter_configuracao()['nome_ia']

  try:
    registrar_mensagem_chat("usuario", mensagem)
    resposta = None
    if nome_ia_bd == IAName.GEMINI:
      resposta = enviar_mensagem_gemini(mensagem)
    elif nome_ia_bd == IAName.CHATGPT:
      resposta = enviar_mensagem_chatgpt(mensagem)
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    
    registrar_mensagem_chat("ia", resposta)
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
  except IAError as iE:
    return json({'mensagem': iE.mensagem}), 400
  except UsuarioError as uE:
    return jsonify({
      'mensagem': str(uE)
    }), 400
  except Exception:
    return json({'mensagem' : 'Probkemas genericos'}), 500

@chat_bp.route('/chat/historico', methods=['GET'])
def obter_historico():
  """
  Usado para obter o histórico de mensagens da conversa com o usuário feita até então.

  Raises:
    200 (Object Json): Solicitação atendida.
    500: Problemas com o backend.
  """
  try:
    resultado = obter_registros_chat()
    return jsonify({
      'registro': resultado if resultado is not None and len(resultado) > 0 else []
    }), 200
  except Exception as e:
    return jsonify({'mensagem': f'ERROR: Houve um problema interno - {e}'}), 500

@chat_bp.route('/chat/registro/conversa_usuario', methods=['GET'])
def obter_registro_conversa_usuario_as_str_route():
  try:
    registro = obter_registro_as_str(True)
    
    return jsonify({'registro': registro}), 200
  except Exception as e:
    print(e)
    return jsonify({'mensagem': "Houve um problema ao tentar resgatar o registro de conversa do usuário"}), 500

@chat_bp.route('/chat/registro/remover_conversa', methods=['DELETE'])
def remover_tudo():
  """
  Usado para apagar toda a conversa feita com o usuário (TUDO)
  Raises:
    200 (Object Json): Solicitação atendida.
    500: Problemas com o backend.
  """
  try:
    excluir_registro_chat_de_conversa()
    return jsonify({'mensagem': 'Registro de conversa excluido com sucesso.'}), 200
  except Exception as e:
    return jsonify({'mensagem': str(e)}),500