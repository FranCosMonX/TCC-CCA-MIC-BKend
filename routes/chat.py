import json

from flask import Blueprint, jsonify, request
from services.germini import (
  Enviar_Mensagem,
  solicitar_codigo_em_json
)
from common.exceptions import (
  JsonError
)
from features.ambiente import (
  instalar_bibliotecas
)
from features.projeto import (
  criar_projeto,
  gravar_codigo
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
  
  try:
    
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
  except:
    return json({'mensagem' : 'Probkemas genericos'}), 500
  
@chat_bp.route('/gerar', methods=['POST'])
def gerar_compilar_gravar():
  try:
    objeto_json = solicitar_codigo_em_json()
    if objeto_json['bibliotecas'] is not None and len(objeto_json['bibliotecas']) > 0:
      bibliotecas_instaladas: list = instalar_bibliotecas(objeto_json['bibliotecas'])
      print(bibliotecas_instaladas)
      
      mensagem = "Problema ao instalar a(s) biblioteca(s):"
      cont = 0 ; problema: bool = False
      for biblioteca_status in bibliotecas_instaladas:
        cont += 1
        if not biblioteca_status:
          problema = True
          mensagem += f" {objeto_json["bibliotecas"][cont - 1]}"
      
      if problema:
        jsonify ({
          'mensagem': 'Não foi possivel instalar todas as bibliotecas para a execução do código.',
          'resposta': mensagem
        }), 202
    
    codigos = objeto_json['codigos']
    for code_index in codigos:
      criar_projeto()
      gravar_codigo(code_index['codigo'],code_index['nome_arquivo'])
    return jsonify({'mensagem': 'solicitação recebida com sucesso.'}), 200
  except JsonError as jE:
    print(e)
    return jsonify({'mensagem': jE.mensagem}), 500
  except Exception as e:
    print(e)
    return jsonify({f'mensagem: {e}'}), 500