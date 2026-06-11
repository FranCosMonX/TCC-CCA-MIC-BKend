from flask import Blueprint, jsonify, request
from bd import atualizar_apelido, obter_configuracao
from common.prompt import alterar_prompt_atual

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
  apelido_bd = configuracao.get('apelido')
  
  if usr is not None and (len(usr) < 2 or not usr):
    return jsonify({
      'mensagem': 'O campo não pode ser nulo ou conter menos de 3 carcteres'
    }), 400
  
  try:
    if apelido_bd != usr:
      atualizar_apelido(usr)
      alterar_prompt_atual(f"nome de usuário: {usr}")
      
    return jsonify({
      'mensagem': "Dados do usuário alterados com êxito."
    }), 200
  except Exception as e:
    return jsonify({
      'error': f'{e}'
    }), 400