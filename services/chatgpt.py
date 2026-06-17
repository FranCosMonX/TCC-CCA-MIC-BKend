"""
Classe utilizada para controlar a interação entre usuário e a IA da OpenAI chamada ChatGPT.

- **Não há interação com banco de dados.**
- **Não há o registro das mensagens no banco de dados, com exceção da instrução e input inicial para o chat.**
"""
from common.archive import salvar_arquivo
from common.exceptions import UsuarioError, IAError, SistemaError, RequisicaoError
from common.prompt import gerar_instrucao_chat, gerar_prompt_json_project, obter_prompt_json_project
from utils.registro import registrar_mensagem_chat
from openai import OpenAI, AuthenticationError, APIStatusError, APIConnectionError
from core.Modelo_de_resposta import Projeto_Arduino_ChatGPT
from pathlib import Path
import os, json

client = None
client_model = None
current_client_id: int | None = None
response = None
conexao_ok = False

def alterar_api_key(api_key: str = None):
  """
  Usado apenas para alterar a  API Key da IA usado. 
  
  - **Não é feito o teste de conexão.**
  - **Não registra a api_key no banco de dados ou arquivo.**
  - **Não registra a alteração.**
  
  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.

  Returns:
    `void`: Se tido correr bem.
  """
  global client

  if not api_key or len(api_key) == 0:
    raise UsuarioError("É necessário informar a API Key para continuar.")
  
  client = OpenAI(api_key=api_key)

def alterar_modelo(modelo: str):
  """
  Usado apenas para alterar o modelo de IA usado.

  - **Não é feito o teste de conexão.**
  - **Não registra o modelo de IA no banco de dados ou arquivo.**
  - **Não registra a alteração.**
  
  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.

  Returns:
    `void`: Se tido correr bem.
  """
  global client_model

  if not modelo or len(modelo) == 0:
    raise UsuarioError("É necessário informar o modelo para continuar.")
  
  client_model = modelo

def testar_conexao():
  """
  Para que possa ser enviado uma requisição para a IA, é necessário que a API Key e modelo jjá estejam definidos.
  
  - **Apenas verifica a conexão.**
  - **Não registra a alteração.**

  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.
    IAError : Problemas com a API da IA.
    
  Returns:
    valor (`boolean`) : status de conexão com a IA
  """
  global conexao_ok
  if not client or not client_model:
    return False
  
  try:
    client.responses.create(
      model='gpt-4o-mini',
      input="Isso é apenas um teste de conexão com a API da OpenAI. Não precisa responder com textoo."
    )

    print('DEBUG - Conexão com o GPT realizado com sucesso.')
    conexao_ok = True
    return conexao_ok
  except AuthenticationError as e:
    raise UsuarioError(e.message)
  except APIStatusError as e:
    raise IAError(e.message)
  except APIConnectionError as e:
    raise IAError(e.message)
  except Exception as e:
    raise IAError(f"Houve um problema ao tentar se conectar com a IA em chatgpt.py testar_conexao(): {e}")

def carregar_contexto_anterior(historico : str = None):
  """
  Usado para carregar o contexto da conversa anterior á desconexão com a IA para uma nova sessão.

  - **Apenas verifica a conexão.**
  - **Não registra a alteração.**

  Params:
    historico (`string`) : contendo o histórico não nulo e não vazio salvo.

  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.
    IAError : Problemas com a API da IA.
    SistemaError : Inconsistência lógica no passo a passo para iniciar o chat.

  Returns:
    Object (`NoneType`) : se tudo der certo, não retorna nada.
  """
  global current_client_id

  if not client_model or not client:
    raise UsuarioError("É necessário informar a API Key e Modelo a ser utilizado no chat.")
  if not conexao_ok:
    raise UsuarioError("Não foi possivel se conectar ao sistema da IA. Verifique a conexão antes de iniciar o Chat.")
  if not historico or len(historico) == 0:
    raise SistemaError("Está tentando carregar o contexto anterior com dados vazios.")
  
  try:
    enviar_mensagem(f"MENSAGEM DO SISTEMA: Considere as configurações e conversas salvas na sessão anterior para continuar ajudando o usuário.\n{historico}")

  except UsuarioError as e:
    raise UsuarioError(e.message)
  except IAError as e:
    raise IAError(e.mensagem)
  except SistemaError as e:
    raise SistemaError(e.mensagem)
  except Exception as e:
    print (e)
    raise RequisicaoError(f"Erro ao enviar o contexto para a IA.")
    
def solicitar_codigo_fonte(historico: str = None):
  """
  Usado para solicitar a construução do código por meio de outra requisição separada da usada no chat, mas usando as conversas entre o usuário e IA para alimentar.

  Detalhes:
    - Temperatura: 0.1
    - Chat alimentado com o registro de mensagens entre o usuário e IA fornecido como parâmetro.
    - Modelo de IA: gpt-4o

  - **Apenas verifica a conexão.**
  - **Apenas registra o código gerado.**
  
  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.
    IAError : Problemas com a API da IA.
    SistemaError : Inconsistência lógica no passo a passo para iniciar o chat.

  Returns:
    Object (`dict`) : contendo os dados solicitados
  """
  SOURCE_RESPONSE_PATH = Path(os.getcwd()) / 'source' / 'response'
  gerar_prompt_json_project(historico)
  response = None
  try:
    response = client.responses.parse(
      model='gpt-4o',
      temperature=0.1,
      instructions=obter_prompt_json_project(),
      text_format=Projeto_Arduino_ChatGPT,
      input="Me retorne o objeto solicitado de acordo com o histórico de conversa do usuárioo. É importante que todo o código gerado seja integro."
    )

    print('DEBUG - RESPOSTA DA IA RECEBIDA\n\n')
    
    salvar_arquivo(
      SOURCE_RESPONSE_PATH,
      'response_arquivo_gerado.json',
      response.output_parsed.model_dump_json(),
      True
    )

    registrar_mensagem_chat('sistema', 'Os arquivos do proojeto foram gerados.')
    registrar_mensagem_chat('ia_model_create_json', response.output_parsed.model_dump_json())
    # print('DEBUG - ARQUIVO JSON GERADO.')
    return json.loads(response.output_parsed.model_dump_json())
  except AuthenticationError as e:
    raise UsuarioError(e.message)
  except APIStatusError as e:
    raise IAError(e.message)
  except APIConnectionError as e:
    raise IAError(e.message)
  except SistemaError as e:
    raise SistemaError(e.mensagem)
  except Exception as e:
    raise RequisicaoError(f"Houve um problema ao tentar se conectar com a IA em chatgpt.py solicitar_codigo_fonte(): {e}")

def enviar_mensagem(mensagem: str = None):
  """
  Usado para continuar a conversa com a IA inciada na função iniciar_chat()
  
  - **Apenas verifica a conexão.**
  - **Não registra a alteração.**

  Params:
    mensagem (`string`) : mensagem do usuário contendo uma string.

  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.
    IAError : Problemas com a API da IA.
    SistemaError : Inconsistência lógica no passo a passo para iniciar o chat.

  Returns:
    `string`: Texto fornecido pela IA em formato `string`.
  """
  global response
  global current_client_id

  if not conexao_ok or not client or not client_model:
    raise SistemaError("Houve uma inconsistência ao tentar enviar uma mensagem para a IA. Conexão não foi testada, mas o chat está registrado como iniciado.")
  
  if not mensagem or len(mensagem) == 0:
    raise UsuarioError("Houve a tentativa de enviar uma mensagem vazia para a IA.")
  
  try:
    response = client.responses.create(
      model=client_model,
      input=mensagem,
      instructions=gerar_instrucao_chat(),
      temperature=0.4,
      previous_response_id=current_client_id
    )
  except AuthenticationError as e:
    raise UsuarioError(e.message)
  except APIStatusError as e:
    raise IAError(e.message)
  except APIConnectionError as e:
    raise IAError(e.message)
  except Exception as e:
    raise IAError(f"Houve um problema ao tentar se conectar com a IA em chatgpt.py enviar_mensagem(): {e}")

  current_client_id = response.id
  return response.output_text

def iniciar_chat():
  """
  Função inicial usada para começar o chat, iniciando a conversa entre usuário e IA.

  - **Apenas verifica a conexão.**
  - **Registra apenas a instrução e input inicial e de configuração do sistema.**

  Raises:
    UsuarioError : Problemas decorridos por informações incompletas ou erradas do cliente ou do usuário.
    IAError : Problemas com a API da IA.

  Returns:
    `void`: Se tido correr bem.
  """
  global response
  global current_client_id
  print(f"CUrrenti client {current_client_id}")

  if not client or not client_model:
    raise UsuarioError("É necessário passar a API Key e modelo a ser usado pela IA.")
  if not conexao_ok:
    raise UsuarioError("Não foi possivel se conectar ao sistema da IA. Verifique a conexão antes de iniciar o Chat.")
  
  print(gerar_instrucao_chat())
  
  try:
    if current_client_id is None:
      INPUT = "MENSAGEM DO SISTEMA: O Chat irá iniciar. Lembre-se sempre das regras passadas. Responda apenas com um OK."
      response = client.responses.create(
        model=client_model,
        instructions=gerar_instrucao_chat(),
        input=INPUT,
        temperature=0.4
      )

      # if len(obter_registro_as_str()) == 0:
      #   registrar_mensagem_chat('sistema', obter_instrucao_chat())
      #   registrar_mensagem_chat('sistema', INPUT)
      # if len(obter_registro_as_str()) == 0:
      #   registrar_mensagem_chat('sistema', obter_instrucao_chat())
      #   registrar_mensagem_chat('sistema', INPUT)
      # else:
      #   registrar_mensagem_chat('sistema', obter_prompt_atual())

      current_client_id = response.id
    else:
      response = client.responses.create(
        model=client_model,
        instructions=gerar_instrucao_chat(),
        input="MENSAGEM DO SISTEMA: O Chat irá reiniciar. Lembre-se sempre das regras passadas. Responda apenas com um OK.",
        temperature=0.4,
        previous_response_id=current_client_id
      )
      current_client_id = response.id
      print(current_client_id)
  except AuthenticationError as e:
    raise UsuarioError(e.message)
  except APIStatusError as e:
    raise IAError(e.message)
  except APIConnectionError as e:
    raise IAError(e.message)
  except Exception as e:
    raise IAError(f"Houve um problema ao tentar se conectar com a IA em chatgpt.py iniciar_chat(): {e}")
  print('DEBUG - Chat iniciado com sucessoo.')