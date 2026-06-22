from flask import Blueprint, jsonify, request
from bd import get_all_mic, obter_configuracao
from services.gemini import solicitar_codigo_fonte as solicitar_codigo_fonte_gemini
from services.chatgpt import solicitar_codigo_fonte as solicitar_codigo_fonte_chatgpt
from utils.projeto import compilar_projeto, gravar_projeto
from utils.registro import registrar_mensagem_chat, obter_registro_as_str
from utils.ambiente import (
  instalar_bibliotecas
)
from utils.projeto import (
  criar_projeto,
  guardar_codigo
)
from common.exceptions import (
  UsuarioError,
  SistemaError, 
  AmbienteError,
  JsonError
)
from enums.ia import IAName
from enums.entidade import Entidade

microcontrolador_bp = Blueprint("microcontrolador", __name__)

@microcontrolador_bp.route('/microcontrolador', methods=['GET'])
def obter_microcontroladores():
  """
  Usado para obter todos os microcontroladores disponiveis na aplicação.
  
  Raises:
    200 : Parâmetros salvos com sucesso.
    500 : Problemas com o backend.
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
  Tem o objetivo de solicitar a geração do código-fonte para a IA, instalar as bibliotecas utilizadas no código além da criação dos arquivos referentes ao projeto.

  Raises:
    200 : Parâmetros salvos com sucesso.
    202 : Instalação de bibliotecas incompletas
    400 : Erro do lado do usuário / cliente
    404 : Não existe o recurso solicitado.
    500 : Houve algum erro no sistema
  """
  try:
    configuracao = obter_configuracao()

    nome_ia_bd = configuracao.get('nome_ia')

    objeto_dict = None
    registro = obter_registro_as_str()
    if nome_ia_bd == IAName.GEMINI:
      objeto_dict = solicitar_codigo_fonte_gemini(registro)
    elif nome_ia_bd == IAName.CHATGPT:
      objeto_dict = solicitar_codigo_fonte_chatgpt(registro)
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
        return jsonify ({
          'mensagem': f'Não foi possivel instalar todas as bibliotecas para a execução do código. {mensagem}',
        }), 202
    
    mensagem = ""
    codigos = objeto_dict['codigos']
    criar_projeto()
    for code_index in codigos:
      mensagem += guardar_codigo(code_index['codigo'],code_index['nome_arquivo'])

    registrar_mensagem_chat(Entidade.ASSISTENTE_DO_SISTEMA, mensagem)
    return jsonify({'mensagem': mensagem}), 200
  except JsonError as jE:
    print(f"DEBUG - ERROR {jE.mensagem}")
    return jsonify({'mensagem': jE.mensagem}), 500
  except Exception as e:
    print(f"DEBUG - ERROR {e}")
    return jsonify({f'mensagem: {e}'}), 500
  
@microcontrolador_bp.route('/compilar', methods=['POST'])
def compilar_codigo():
  """
  Utilizado para compilar o projeto recém criado.

  Raises:
    200 : projeto compilado com sucesso
    400 : Erro do lado do usuário / cliente
    409 : Solicitação entendida mas não realizada devido a problemas internos ou falta de recursos.
    500 : Houve algum erro no sistema
  """
  try:
    configuracao = obter_configuracao()
    if configuracao['diretorio'] in ['', None]:
      return jsonify({
        'mensagem': 'É necessário que o projeto esteja criado no diretório especificado nas configurações gerais.'
      }), 400
    
    resultado = compilar_projeto()
    registrar_mensagem_chat(Entidade.ASSISTENTE_DO_SISTEMA, resultado)
    return jsonify({
      'mensagem': resultado
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
  """
  Utilizado para gravar o projeto compilado previamente, no microcoontrolador
  
  Raises:
    200 : projeto gravado com sucesso
    400 : Erro do lado do usuário / cliente
    500 : Houve algum erro no sistema
  """
  try:
    resultado = gravar_projeto()
    registrar_mensagem_chat(Entidade.ASSISTENTE_DO_SISTEMA, resultado)
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