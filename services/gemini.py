"""
Classe utilizada para controlar a interação entre usuário e a IA da Google chamada Gemini.

- **Não há interação com banco de dados.**
- **Não há o registro das mensagens no banco de dados, com exceção da instrução e input inicial para o chat mas sé feito atraves de uma função intermediaria.**
"""
from google import genai
from google.genai.errors import ClientError, APIError
from core.Modelo_de_resposta import Projeto_Arduino_Base
from pathlib import Path
import json, os, time
from common.exceptions import (
  UsuarioError,
  SistemaError,
  JsonError,
  IAError,
  RequisicaoError
)
from common.prompt import (
  gerar_instrucao_chat,
  obter_instrucao_chat,
  gerar_prompt_json_project,
  obter_prompt_json_project
)
from utils.registro import (
  registrar_mensagem_chat, obter_registro_as_str
)

# modelo_default = "gemini-2.5-flash" 
client = None
chat_model = None
chat = None
conexao_ok = False

def alterar_api_key(api_key : str = None):
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

  client = genai.Client(api_key=api_key)

def alterar_modelo(modelo : str = None):
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
  global chat_model
  if not modelo or len(modelo) == 0:
    raise UsuarioError("É necessário informar o modelo para continuar.")
  
  chat_model = modelo
  
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
  if client is None or chat_model is None:
    conexao_ok = False
    return conexao_ok
  
  try:
    for _ in client.models.list(config={'page_size': 1}):
      break
    
    conexao_ok = True
    return conexao_ok
  except ClientError as e:
    raise UsuarioError(e.message)
  except APIError as e:
    raise IAError(e.message)
  except Exception as e:
    raise SistemaError(f"Houve um problema ao testar a conexão. {e}")
  
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
  if not chat_model or not client:
    raise UsuarioError("É necessário informar a API Key e Modelo a ser utilizado no chat.")
  if not conexao_ok:
    raise UsuarioError("Não foi possivel se conectar ao sistema da IA. Verifique a conexão antes de iniciar o Chat.")
  if not chat:
    raise SistemaError("É necessário a abertura de sessão de chat para continuar interagindo com a IA.")
  if not historico:
    raise SistemaError("Está tentando carregar o contexto anterior com dados vazios.")
  if len(historico) == 0:
    raise UsuarioError("Não há dados salvos.")
  
  try:
    chat.send_message(f"MENSAGEM DO SISTEMA: Considere as configurações e conversas salvas na sessão anterior para continuar ajudando o usuário.\n{historico}")
  except ClientError as e:
    raise UsuarioError(e.message)
  except APIError as e:
    raise IAError(e.message)
  except Exception as e:
    raise RequisicaoError(f"Erro ao enviar o contexto para a IA.")

def solicitar_codigo_fonte(historico : str = None):
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
  
  if not historico or len(historico) == 0:
    raise UsuarioError("É necessário ter interação primeiro antes de gerar o código.")

  gerar_prompt_json_project(historico)
  try:
    resposta = client.models.generate_content(
      model=chat_model,
      contents="Me retorne o objeto solicitado de acordo com o histórico de conversa do usuárioo. É importante que todo o código gerado seja integro.",
      config={
          'system_instruction': obter_prompt_json_project(),
          'temperature': 0.2,
          'response_mime_type': 'application/json',
          'response_schema': Projeto_Arduino_Base
        }
    )

    try:
      dados_json = json.loads(resposta.text)
      
      with open(SOURCE_RESPONSE_PATH / "resumo_conversa_final.json", "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)
      
      registrar_mensagem_chat('sistema', 'Os arquivos do proojeto foram gerados.')
      registrar_mensagem_chat('ia_model_create_json', resposta.text)
      return dados_json
    except json.JSONDecodeError as e:
      print(f"DEBUG - JSON Inválido: {resposta.text}")
      raise JsonError("A IA não gerou um JSON válido.")

  except ClientError as e:
    raise UsuarioError(e.message)
  except APIError as e:
    raise IAError(e.message)
  except Exception as e:
    raise RequisicaoError(f"Erro na geração dos arquivos JSON: {e}")
  
def enviar_mensagem(mensagem : str = None):
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
  if not chat or not client or not conexao_ok:
    raise SistemaError("Houve uma inconsistência ao tentar enviar uma mensagem para a IA. Conexão não foi testada, mas o chat está registrado como iniciado.")
  
  if not mensagem or len(mensagem) == 0:
    raise UsuarioError("Houve a tentativa de enviar uma mensagem vazia para a IA.")
  
  try:
    response = chat.send_message(mensagem)

    return response.text
  except ClientError as e:
    raise UsuarioError(e.message)
  except APIError as e:
    tempo_espera = 30*1000

    if e.code == 503:
      print(f"DEBUG - Erro ao enviar mensagem para a IA com código 503. Tentando reenviar após 30 segundos.")
      time.sleep(tempo_espera)
      try:
        response = chat.send_message(mensagem)
        return response.text
      except Exception as e2:
        if e2.code == 429:
          raise IAError(f"Houve um problema ao enviar a requisição para a IA devido ao limite de solicitações atingido..")
        raise IAError(f"Problema em reenviar a requisição para a IA.\n\n{e2.message}")
    elif e.code == 429:
      raise IAError(f"Houve um problema ao enviar a requisição para a IA devido ao limite de solicitações atingido..")

    print(f"DEBUG - Erro ao enviar mensagem para a IA: {e}")

    raise IAError(e.message)
  except Exception as e:
    raise SistemaError(f"Problema ao iniciar o chat em gemini.py enviar_mensagem(). {e}")
  
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
  global chat

  if not chat_model or not client:
    raise UsuarioError("É necessário informar a API Key e Modelo a ser utilizado no chat.")
  if not conexao_ok:
    raise UsuarioError("Não foi possivel se conectar ao sistema da IA. Verifique a conexão antes de iniciar o Chat.")
  
  try:
    if not chat:
      gerar_instrucao_chat()
      PROMPT_START = "MENSAGEM DO SISTEMA: O Chat irá iniciar. Lembre-se sempre das regras passadas. Responda apenas com um OK."

      chat = client.chats.create(
        model=chat_model,
        config={
          'system_instruction': obter_instrucao_chat(),
          'temperature': 0.2
        }
      )

      if len(obter_registro_as_str()) == 0:
        registrar_mensagem_chat('sistema', obter_instrucao_chat())
        registrar_mensagem_chat('sistema', PROMPT_START)
        chat.send_message(message=PROMPT_START)
      # if len(obter_registro_as_str()) == 0:
      #   registrar_mensagem_chat('sistema', obter_instrucao_chat())
      #   registrar_mensagem_chat('sistema', PROMPT_START)
      # else:
      #   print('degub - registrouu mudança')
      #   registrar_mensagem_chat('sistema', obter_prompt_atual())
  except ClientError as e:
    raise UsuarioError(e.message)
  except APIError as e:
    raise IAError(e.message)
  except Exception as e:
    print(e)
    raise SistemaError(f"Problema ao iniciar o chat em gemini.py iniciar_chat(). {e}")

# def verificar_conexao(contem_dados=False, chave = None, modelo = None):
#   """
#   Verifica a conexão com a API. Caso não esteja configurada mesmo com dados salvos, será feita a reconfiguração para reconectar.
  
#   Returns:
#     resultado (`boolean`) : informando se está conectado ou não ao serviço de IA.
#   """

#   if not client and contem_dados:
#     print("DEBUG - CONEXÃO COM IA PERDIDA, TENTANDO CONEXTAR NOVAMENTE.")
#     if chave is None or modelo is None:
#       return False
    
#     atualiza_api_key_ou_modelo(chave, modelo)
#     return True

#   try:
#     if not client: return False
#     for _ in client.models.list(config={'page_size': 1}):
#       break
#     print(f'DEBUG - CONEXÃO FEITA.')

#     return True
#   except Exception as e:
#     print(f"DEBUG - ERROR gemini.py em verificar_conexao: {e}")
#     return False

# def atualiza_api_key_ou_modelo(chave: str, modelo=modelo_default):
#   """Atualiza a chave de API e reinicia os objetos de conexão."""
#   global client, chat, modelo_default
#   modelo_default = modelo

#   try:
#     client = genai.Client(api_key=chave)
    
#     if not verificar_conexao():
#       raise UsuarioError("Chave de API inválida.")

#     config = _gerar_config_sistema()
    
#     chat = client.chats.create(model=modelo_default, config=config)
    
#     print("DEBUG - Chave de API atualizada e chat reiniciado.")
#   except Exception as e:
#     raise UsuarioError(f"DEBUG - ERROR gemini.py em atualiza_api_key_ou_modelo: ao configurar a API de IA: {e}")

# def _gerar_config_sistema():
#   """Auxiliar para montar a instrução de sistema baseada no BD."""
  
#   gerar_instrucao_chat()

#   return types.GenerateContentConfig(
#     system_instruction=instrucao_modelo_chat,
#     temperature=0.9
#   )

# def Enviar_Mensagem(mensagem: str):
#   """Envia mensagem no chat principal (conversa humana)."""

#   tempo_espera = 30 * 1000
#   try:
#     if not chat:
#       raise SistemaError("Chat não iniciado. Verifique a API Key.")
#     response = chat.send_message(mensagem)
#     return response
#   except Exception as e:
#     if e.code == 503:
#       print(f"DEBUG - Erro ao enviar mensagem para a IA com código 503. Tentando reenviar após 30 segundos.")
#       time.sleep(tempo_espera)
#       try:
#         response = chat.send_message(mensagem)
#         return response
#       except Exception as e2:
#         if e2.code == 429:
#           raise IAError(f"Houve um problema ao enviar a requisição para a IA devido ao limite de solicitações atingido..")
#         raise IAError(f"Problema em reenviar a requisição para a IA.\n\n{e2.message}")
#     elif e.code == 429:
#       raise IAError(f"Houve um problema ao enviar a requisição para a IA devido ao limite de solicitações atingido..")

#     print(f"DEBUG - Erro ao enviar mensagem para a IA: {e}")
#     raise IAError(f"Problemas ao enviar a requisição para a IA.\n\n {e.message}")

# def alterarPrompting(apenas_mudanca: str):
#   """Injeta uma instrução de sistema no meio da conversa."""
#   try:
#     # No SDK atual, enviamos como uma mensagem que o modelo entende como comando
#     msg_sistema = f"SISTEMA: O usuário alterou as escolhas: {apenas_mudanca}. Considere os novos pedidos. NÃO CITE ESTA MENSAGEM."
#     Enviar_Mensagem(msg_sistema)
#   except Exception as e:
#     raise IAError(f"Erro ao atualizar prompt: {e}")

# def historico():
#   """Retorna o objeto de histórico do chat."""
#   try:
#     return chat.get_history() if chat else []
#   except:
#     return []

# def salva_historico():
#   """Salva o histórico formatado em um arquivo txt."""
#   URI_BASE = os.getcwd()
#   try:
#     with open(os.path.join(URI_BASE, "historico.txt"), mode="w", encoding="utf-8") as arquivo:
#       for msg in chat.get_history():
#         arquivo.write(f"{msg.role.upper()}: {msg.parts[0].text}\n")
#     return True
#   except Exception as e:
#     print(f"DEBUG - Erro ao salvar histórico: {e}")
#     return False

# def solicitar_codigo_em_json():
#   """
#   Usa um segundo modelo (especialista em JSON) para processar 
#   o histórico da conversa e gerar os arquivos do projeto.
#   """
  
#   # 1. Transformamos o histórico em um bloco de texto descritivo na criação de um prompt aceitavel
#   hist = historico()
#   prompt = alterar_prompt_gerar_arquivo(hist)

#   # 2. Configuração estrita para JSON
#   config_json = types.GenerateContentConfig(
#     response_mime_type="application/json",
#     temperature=0.1, # Temperatura baixa para evitar erros no JSON
#     system_instruction="Você é um gerador de arquivos JSON para sistemas embarcados. Retorne APENAS o JSON solicitado, sem explicações e NUNCA responda como MARKDOWN."
#   )

#   try:
#     # Chamada direta (sem chat) para o modelo de arquivos
#     # Usamos o mesmo modelo ou um diferente se preferir (ex: Pro)
#     resposta = client.models.generate_content(
#       model=modelo_default,
#       contents=prompt,
#       config=config_json
#     )

#     # print(resposta.text)
#     try:
#       dados_json = json.loads(resposta.text)
      
#       with open("resumo_conversa_final.json", "w", encoding="utf-8") as f:
#         json.dump(dados_json, f, indent=2, ensure_ascii=False)
      
#       return dados_json
#     except json.JSONDecodeError as e:
#       print(f"DEBUG - JSON Inválido: {resposta.text}")
#       raise JsonError("A IA não gerou um JSON válido.")

#   except Exception as e:
#     raise RequisicaoError(f"Erro na geração dos arquivos JSON: {e}")

# def iniciar():
#   """Inicia o processo de saudação e configuração inicial."""
#   # O prompt de sistema já foi definido no 'atualiza_api_key_ou_modelo'
#   # Aqui apenas enviamos o gatilho inicial se necessário.
#   print(f"prompt atual: {obter_prompt_atual()}")

#   mensagem = f"{obter_prompt_atual()}SISTEMA: Configurações definidas. Por favor, confirme se está pronto. O chat com o usuário irá iniciar."
#   registrar_mensagem_chat("sistema", mensagem)
#   return Enviar_Mensagem(mensagem)