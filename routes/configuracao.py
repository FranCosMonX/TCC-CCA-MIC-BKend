from flask import Blueprint, request, jsonify
from bd import (
  atualizar_apelido,
  atualiza_chave_acesso_ai,
  atualizar_dadosConf_gerais,
  atualizar_dados_mic,
  criar_config_default,
  edit_validacao_api_key,
  init_db,
  obter_configuracao,
  get_mic_by_id,
  get_all_mic,
  resetar_configs,
  tem_modelo_da_ia
)
from common.exceptions import (
  AmbienteError,
  UsuarioError,
)
from features.ambiente import (
  preparando_ambiente,
)
from services.germini import atualiza_api_key_ou_modelo, alterarPrompting, iniciar

configuracao_bp = Blueprint("configuracao", __name__)

@configuracao_bp.route('/init')
def inicializacao_de_dados():
  """
  Primeiro Endpoint que deverá ser chamado para a inicialização do Banco de Dados.

  Returns:
  
    201: Dados salvos com sucesso.
    500: Problemas com o backend.
  """
  
  try:
    configuracao = obter_configuracao()
    
    if configuracao['id_microcontrolador'] is not None or configuracao['key_ai_api'] is not None or configuracao['diretorio'] is not None:
      return jsonify({
        'mensagem': 'Já existe arquivo e dados salvos.'
      }), 200
    
    return jsonify({
      'mensagem': 'Os arquivos já existem, mas falta pendências de dados.'}), 204
  except:
    try:
      init_db()
      criar_config_default()

      return jsonify({
        'mensagem': 'Banco de Dados inicializado com êxito.'
      }), 201
    except Exception as e:
      print(f"DEBUG = ERROR: {e}")
      return jsonify({
        'mensagem': 'Houve um problema ao executar o script de criação do Banco de Dados local.'
      }), 500
      
@configuracao_bp.route('/RemoverConfiguracao', methods=['DELETE'])
def remover_configuracao():
  """
  Usado para remover todas as configurações salvas no banco de dados.
  """
  
  try:
    resetar_configs()
    return jsonify({
      'mensagem': 'Dados resetados com sucesso.'
    }), 200
  except:
    return jsonify({
      'mensagem': 'Houve um problema ao resetar os dados.'
    }), 500

@configuracao_bp.route('/CarregarConfiguracao', methods=['POST'])
def carregar_configuracao():
  """
  É necessário que tenha o arquivo de banco de dados gerado.
  """
  configuracao = obter_configuracao()
  mensagem = ""
  execucao = [configuracao['id_microcontrolador'] is not None, configuracao['key_ai_api'] is not None, configuracao['diretorio'] is not None]
  try:
    preparando_ambiente(configuracao['id_microcontrolador'])
    mensagem += "Ambiente de execução configurado com exito."
    execucao[0] = True
  except Exception as e:
    mensagem += 'Não há dados suficientes para preparar o ambiente de execução de código.'
  
  try:
    atualiza_api_key_ou_modelo(configuracao['key_ai_api'])
    mensagem += "Conexão com a IA realizada com êxito."
    execucao[1] = True
  except Exception as e:
    mensagem += "Não há dados suficientes para tentar se conectar a API da IA."
  
  if not configuracao['diretorio']:
    mensagem += "O campo diretório se encontra vazio, preencha o campo corretamente."
  else:
    execucao[2] = True
  
  if execucao[0] or execucao[1] or execucao[2]:
    return jsonify({
      'mensagem': mensagem
    }), 200
  else:
    try:
      resetar_configs()
      return jsonify({
        'mensagem': "Não foi possivel realizar esta ação. Atualize os dados."
      }), 400
    except Exception as e:
      return jsonify({
        'mensagem': e
      }), 500

@configuracao_bp.route('/configuracaoGeral', methods=['POST'])
def definir_conf_geral():
  """
  Descrição:
  
    Usado para mudar parâmetros do microcontrolador usados na conversa com a AI. É bastante importante para 
  Returns:
  
    201: Dados salvos com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  nome_projeto = request.json.get('nome_projeto')
  diretorio = request.json.get('diretorio')
  key_ai_api = request.json.get('key_ai_api')
  ver_codigo = request.json.get('ver_codigo')
  comentario_codigo = request.json.get('comentario_codigo')
  
  configuracao = obter_configuracao()
  status_chave_verificada = configuracao['api_key_valid']
  chave_verificada = configuracao["key_ai_api"]
  
  if not status_chave_verificada:
    return jsonify({
      'mensagem': "Primeiro verifique se a chave de acesso é válida.",
      'campo': 'key_ai_api'
    }), 400
    
  if  chave_verificada != key_ai_api:
    return jsonify({
      'mensagem': "Houve a alteração da chave de acesso após confirmar sua validação. Inclua a mesma ou valide uma nova.",
      'campo': 'key_ai_api'
    }), 400
    
  if not nome_projeto:
    return jsonify({
      'mensagem': 'O campo não pode ser nulo',
      'campo': 'nome_projeto'
    }), 400
  
  if not diretorio or len(diretorio) < 3:
    return jsonify({
      'mensagem': 'O caminho onde os arquivos serão salvos é invalido.',
      'campo': 'diretorio'
    }), 400
  print("passouu final")
  try:
    msg = atualizar_dadosConf_gerais(nome_projeto, diretorio,ver_codigo,comentario_codigo)
    alterarPrompting(f"comentario do código: {comentario_codigo}, visualizar codigo: {ver_codigo}, o nome do projeto é: {nome_projeto}")
    return jsonify({
      'mensagem': msg,
      'dados':{
        'diretorio': diretorio,
        'key_ai_api': key_ai_api,
        'ver_codigo': ver_codigo,
        'comentario_codigo': comentario_codigo,
        'nome_projeto': nome_projeto
      }
    }), 200
  except Exception as e:
    print(f"{e}")
    return jsonify({'error': str(e)}), 500

@configuracao_bp.route('/configuracaoMicrocontrolador', methods=['POST'])
def definir_conf_mic():
  """
  Descrição:
  
    Usado para mudar parâmetros do microcontrolador usados na conversa com a AI. É bastante importante para 
  Retorno:
  
    200: Parâmetros salvos com sucesso.
    400: Campo ou alguma entrada de usuário incorreta.
    500: Problemas com o backend.
  """
  id_mic = request.json.get('id_microcontrolador')
  
  if not id_mic:
    return jsonify({
      'mensagem': 'É necessário escolher o microcontrolador para continuar.'
    }), 400
  
  dados_mic = get_mic_by_id(id_mic)
  print(dados_mic)
  try:
    atualizar_dados_mic(id_mic)
    alterarPrompting(f"Microcontrolador: {dados_mic['nome']}, {dados_mic['fqbn']}")
  except Exception as e:
    print(e)
    return jsonify({'mensagem': str(e)}), 500
  
  try:
    preparando_ambiente(dados_mic['fqbn'])
    return jsonify({'mensagem': "Ambiente de trabalho configurado com êxito."}), 200
  except UsuarioError as uE:
    return jsonify({'mensage,': uE.mensagem}), 400
  except AmbienteError as aE:
    return jsonify({'mensagem': 'Houve um problema ao tentar preparar o ambiente de execução.'}), 500
  except Exception as e:
    print(e)
    return jsonify({'error': str(e)}), 500
  
# Rota para obter todos os dados
@configuracao_bp.route('/configuracao', methods=['GET'])
def get_dados():
  """
  Descrição:
  
    Usado para mudar parâmetros de configuração usados na conversa com a AI.
  Retorno:
  
    200: Parâmetros salvos com sucesso.
    500: Problemas com o backend.
  """
  try:
    resultado = obter_configuracao()
    return jsonify(resultado), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500