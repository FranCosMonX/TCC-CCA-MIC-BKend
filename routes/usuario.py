from flask import Blueprint, jsonify, request
from bd import obter_configuracao, atualizar_apelido
from services.germini import alterarPrompting, iniciar

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route('/usuario', methods=['POST'])
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
  if configuracao['id_microcontrolador'] is None:
    return jsonify({
      'mensagem': 'Antes de começar, é necessário preparar o ambiente de trabalho.'
    }), 400
    
  if not configuracao['api_key_valid']:
    return jsonify({
      'mensagem': 'É necessário passar uma chave de acesso para a IA que seja válida'
    }), 400
  
  if usr is not None and (len(usr) < 2 or not usr):
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