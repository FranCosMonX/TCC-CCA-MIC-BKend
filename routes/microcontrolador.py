from flask import Blueprint, jsonify, request
from bd import get_all_mic, obter_configuracao
from features.projeto import compilar_projeto, gravar_projeto
from common.exceptions import (
  UsuarioError,
  SistemaError, 
  AmbienteError,
  JsonError
)
from services.germini import (
  solicitar_codigo_em_json
)
from services.chatgpt import solicitar_codigo_fonte
from features.ambiente import (
  instalar_bibliotecas
)
from features.projeto import (
  criar_projeto,
  guardar_codigo
)
from features.registro import registrar_mensagem_chat, obter_registro_as_str
from enums.ia import IAName

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
  
@microcontrolador_bp.route('/gerar', methods=['POST'])
def gerar():
  """
  Tem o objetivo de instalar as bibliotecas utilizadas no código além da criação dos arquivos.
  """
  try:
    configuracao = obter_configuracao()

    nome_ia_bd = configuracao.get('nome_ia')

    objeto_dict = None
    if nome_ia_bd == IAName.GEMINI:
      objeto_dict = solicitar_codigo_em_json()
    elif nome_ia_bd == IAName.CHATGPT:
      objeto_dict = solicitar_codigo_fonte(obter_registro_as_str())
    else:
      return jsonify({'mensagem': 'Houve um problema inesperado ao tentar identificar a IA escolhida pelo usuário.'}), 404
    
    if objeto_dict['bibliotecas'] is not None and len(objeto_dict['bibliotecas']) > 0:
      bibliotecas_instaladas: list = instalar_bibliotecas(objeto_dict['bibliotecas'])
      print(bibliotecas_instaladas)
      
      mensagem = "Problema ao instalar a(s) biblioteca(s):"
      cont = 0 ; problema: bool = False
      for biblioteca_status in bibliotecas_instaladas:
        cont += 1
        if not biblioteca_status:
          problema = True
          mensagem += f" {objeto_dict["bibliotecas"][cont - 1]}"
      
      if problema:
        jsonify ({
          'mensagem': f'Não foi possivel instalar todas as bibliotecas para a execução do código. {mensagem}',
        }), 202
    
    mensagem = ""
    codigos = objeto_dict['codigos']
    criar_projeto()
    for code_index in codigos:
      mensagem += guardar_codigo(code_index['codigo'],code_index['nome_arquivo'])

    registrar_mensagem_chat('sistema', mensagem)
    return jsonify({'mensagem': mensagem}), 200
  except JsonError as jE:
    print(f"DEBUG - ERROR {jE.mensagem}")
    return jsonify({'mensagem': jE.mensagem}), 500
  except Exception as e:
    print(f"DEBUG - ERROR {e}")
    return jsonify({f'mensagem: {e}'}), 500
  
@microcontrolador_bp.route('/compilar', methods=['POST'])
def compilar_codigo():
  try:
    configuracao = obter_configuracao()
    if configuracao['diretorio'] in ['', None]:
      return jsonify({
        'mensagem': 'É necessário que o projeto esteja criado no diretório especificado nas configurações gerais.'
      }), 400
    
    resultaado = compilar_projeto()
    return jsonify({
      'mensagem': resultaado
    }), 200
  except UsuarioError as uE:
    # print(uE)
    return jsonify({
      'mensagem': uE.mensagem
    }),400
  except AmbienteError as aE:
    # print(uE)
    return jsonify({
      'mensagem': aE.mensagem
    }),409
  except SistemaError as sE:
    # print(sE)
    return jsonify({
      'mensagem': sE.mensagem
    }), 500
  except Exception as e:
    # print(e)
    return jsonify({
      'mensagem': str(e)
    }), 500

@microcontrolador_bp.route("/gravar", methods=['POST'])
def gravar_codigo():
  try:
    resultado = gravar_projeto()

    return jsonify({
      'mensagem': resultado
    }), 200
  except UsuarioError as uE:
    return jsonify({
      'mensagem': uE.mensagem
    }),400
  except AmbienteError as aE:
    return jsonify({
      'mensagem': aE.mensagem
    }), 409
  except SistemaError as sE:
    return jsonify({
      'mensagem': sE.mensagem
    }), 500
  except Exception as e:
    return jsonify({
      'mensagem': str(e)
    }), 500