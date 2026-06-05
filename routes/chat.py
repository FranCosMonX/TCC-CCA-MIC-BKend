import json

from flask import Blueprint, jsonify, request
from services.germini import (
  Enviar_Mensagem,
  iniciar,
  verificar_conexao
)
from services.chatgpt import (
  enviar_mensagem,
  iniciar_chat as iniciar_chat_com_gpt,
  testar_conexao
)
from enums.ia import IAName
from common.exceptions import (
  UsuarioError, IAError
)
from features.registro import (
  registrar_mensagem_chat
)
from bd import (
  obter_configuracao,
  excluir_registro_chat_de_conversa,
  obter_registros_chat
)

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

    mensagem_error = ""
    if nome_projeto_bd is None:
      mensagem_error += "É necessário informar o nome do projeto para começar."
    if not api_valid_bd:
      mensagem_error += "É necessário definir as configurações de conexão com a API da IA."
    if not ambiente_valid_bd:
      mensagem_error += "É necessário estar com o ambiente de desenvolvimento configurado. Escolha o microcontrolador para que o código possa ser gerado corretamente."

    if mensagem_error != "":
      return jsonify({
        'mensagem': "É necessário que corrija algumas pendências:\n" + mensagem_error
      }), 400
    
    if nome_ia_bd == IAName.GEMINI:
      verificar_conexao(True, configuracao.get('key_ai_api'), configuracao.get('modelo_disponivel'))
      iniciar()
    elif nome_ia_bd == IAName.CHATGPT:
      testar_conexao()
      iniciar_chat_com_gpt()
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    return jsonify({
      'mensagem': "Chat Iniciado"
    }), 200
  except UsuarioError as uE:
    return jsonify({
      'mensagem': str(uE)
    }), 400
  except IAError as iE:
    return jsonify({
      'mensagem': str(uE)
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
      resposta = Enviar_Mensagem(mensagem).text
    elif nome_ia_bd == IAName.CHATGPT:
      resposta = enviar_mensagem(mensagem)
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
  try:
    resultado = obter_registros_chat()
    return jsonify({
      'registro': resultado
    }), 200
  except Exception as e:
    return jsonify({'mensagem': f'ERROR: Houve um problema interno - {e}'}), 500

@chat_bp.route('/chat/remover/tudo', methods=['DELETE'])
def remover_tudo():
  try:
    excluir_registro_chat_de_conversa()
    return jsonify({'mensagem': 'exclusão feita com sucesso.'})
  except Exception as e:
    return jsonify({'mensagem': str(e)}),500