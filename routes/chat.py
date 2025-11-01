import json

from flask import Blueprint, jsonify, request
from services.germini import (
  Enviar_Mensagem
)

chat_bp = Blueprint("chat", __name__)

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