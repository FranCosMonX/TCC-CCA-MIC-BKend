from google import genai
from google.genai import types
from common.exceptions import (
  UsuarioError,
  SistemaError,
  JsonError,
  IAError,
  RequisicaoError
)
from common.prompt import (
  instrucao_modelo_chat,
  gerar_instrucao_chat,
  alterar_prompt_gerar_arquivo,
  obter_prompt_atual
)
from features.registro import (
  registrar_mensagem_chat
)
import json, os, time

modelo_default = "gemini-2.5-flash" 

client = None
chat = None  

def verificar_conexao(contem_dados=False, chave = None, modelo = None):
  """Verifica a conexão com a API. Caso não esteja configurada mesmo com dados salvos, será feita a reconfiguração para reconectar."""

  if not client and contem_dados:
    print("DEBUG - CONEXÃO COM IA PERDIDA, TENTANDO CONEXTAR NOVAMENTE.")
    if chave is None or modelo is None:
      return False
    
    atualiza_api_key_ou_modelo(chave, modelo)
    return True

  try:
    if not client: return False
    for _ in client.models.list(config={'page_size': 1}):
      break
    print(f'DEBUG - CONEXÃO FEITA.')

    return True
  except Exception as e:
    print(f"DEBUG - ERROR gemini.py em verificar_conexao: {e}")
    return False

def atualiza_api_key_ou_modelo(chave: str, modelo=modelo_default):
  """Atualiza a chave de API e reinicia os objetos de conexão."""
  global client, chat, modelo_default
  modelo_default = modelo

  try:
    client = genai.Client(api_key=chave)
    
    if not verificar_conexao():
      raise UsuarioError("Chave de API inválida.")

    config = _gerar_config_sistema()
    
    chat = client.chats.create(model=modelo_default, config=config)
    
    print("DEBUG - Chave de API atualizada e chat reiniciado.")
  except Exception as e:
    raise UsuarioError(f"DEBUG - ERROR gemini.py em atualiza_api_key_ou_modelo: ao configurar a API de IA: {e}")

def _gerar_config_sistema():
  """Auxiliar para montar a instrução de sistema baseada no BD."""
  
  gerar_instrucao_chat()

  return types.GenerateContentConfig(
    system_instruction=instrucao_modelo_chat,
    temperature=0.9
  )

def Enviar_Mensagem(mensagem: str):
  """Envia mensagem no chat principal (conversa humana)."""
  registrar_mensagem_chat("usuario", mensagem)

  tempo_espera = 30 * 1000
  try:
    if not chat:
      raise SistemaError("Chat não iniciado. Verifique a API Key.")
    response = chat.send_message(mensagem)
    return response
  except Exception as e:
    if e.code == 503:
      print(f"DEBUG - Erro ao enviar mensagem para a IA com código 503. Tentando reenviar após 30 segundos.")
      time.sleep(tempo_espera)
      try:
        response = chat.send_message(mensagem)
        return response
      except Exception as e2:
        raise IAError(f"Problema em reenviar a requisição para a IA.\n\n{e2.message}")

    print(f"DEBUG - Erro ao enviar mensagem para a IA: {e}")
    raise IAError(f"Problemas ao enviar a requisição para a IA.\n\n {e.message}")

def alterarPrompting(apenas_mudanca: str):
  """Injeta uma instrução de sistema no meio da conversa."""
  try:
    # No SDK atual, enviamos como uma mensagem que o modelo entende como comando
    msg_sistema = f"SISTEMA: O usuário alterou as escolhas: {apenas_mudanca}. Considere os novos pedidos. NÃO CITE ESTA MENSAGEM."
    Enviar_Mensagem(msg_sistema)
  except Exception as e:
    raise IAError(f"Erro ao atualizar prompt: {e}")

def historico():
  """Retorna o objeto de histórico do chat."""
  try:
    return chat.get_history() if chat else []
  except:
    return []

def salva_historico():
  """Salva o histórico formatado em um arquivo txt."""
  URI_BASE = os.getcwd()
  try:
    with open(os.path.join(URI_BASE, "historico.txt"), mode="w", encoding="utf-8") as arquivo:
      for msg in chat.get_history():
        arquivo.write(f"{msg.role.upper()}: {msg.parts[0].text}\n")
    return True
  except Exception as e:
    print(f"DEBUG - Erro ao salvar histórico: {e}")
    return False

def solicitar_codigo_em_json():
  """
  Usa um segundo modelo (especialista em JSON) para processar 
  o histórico da conversa e gerar os arquivos do projeto.
  """
  
  # 1. Transformamos o histórico em um bloco de texto descritivo na criação de um prompt aceitavel
  hist = historico()
  prompt = alterar_prompt_gerar_arquivo(hist)

  # 2. Configuração estrita para JSON
  config_json = types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.1, # Temperatura baixa para evitar erros no JSON
    system_instruction="Você é um gerador de arquivos JSON para sistemas embarcados. Retorne APENAS o JSON solicitado, sem explicações e NUNCA responda como MARKDOWN."
  )

  try:
    # Chamada direta (sem chat) para o modelo de arquivos
    # Usamos o mesmo modelo ou um diferente se preferir (ex: Pro)
    resposta = client.models.generate_content(
      model=modelo_default,
      contents=prompt,
      config=config_json
    )

    # print(resposta.text)
    try:
      dados_json = json.loads(resposta.text)
      
      with open("resumo_conversa_final.json", "w", encoding="utf-8") as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)
      
      return dados_json
    except json.JSONDecodeError as e:
      print(f"DEBUG - JSON Inválido: {resposta.text}")
      raise JsonError("A IA não gerou um JSON válido.")

  except Exception as e:
    raise RequisicaoError(f"Erro na geração dos arquivos JSON: {e}")

def iniciar():
  """Inicia o processo de saudação e configuração inicial."""
  # O prompt de sistema já foi definido no 'atualiza_api_key_ou_modelo'
  # Aqui apenas enviamos o gatilho inicial se necessário.
  print(f"prompt atual: {obter_prompt_atual()}")

  mensagem = f"{obter_prompt_atual()}SISTEMA: Configurações definidas. Por favor, confirme se está pronto. O chat com o usuário irá iniciar."
  registrar_mensagem_chat("sistema", mensagem)
  return Enviar_Mensagem(mensagem)