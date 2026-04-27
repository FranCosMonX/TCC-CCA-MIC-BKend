from flask import Blueprint, jsonify, request
from bd import add_modelo_ia, obter_modelo_por_nome_ia, obter_modelos_disponiveis, obter_modelo_por_id, obter_ias_disponiveis

ia_bp = Blueprint("ia", __name__)

@ia_bp.route('/adicionarModelo', methods=['POST'])
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