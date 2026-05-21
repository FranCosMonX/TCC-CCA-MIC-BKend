from flask import Blueprint, jsonify, request
from bd import get_all_mic

microcontrolador_bp = Blueprint("microcontrolador", __name__)

@microcontrolador_bp.route('/microcontrolador', methods=['GET'])
def obter_microcontroladores():
  """
  Descrição:
  
    Usado para obter todos os microcontroladores disponiveis na aplicação.
  
    200: Parâmetros salvos com sucesso.
    500: Problemas com o backend.
  """
  try:
    resultadoo = get_all_mic()
    return jsonify({
      'mensagem': "Dados obtidos com sucesso.",
      'Microcontroladores': resultadoo
    }), 200
  except Exception as e:
    print(f"DEBUG - ERROR: {e}")
    return jsonify({
      'mensagem': e
    }), 500