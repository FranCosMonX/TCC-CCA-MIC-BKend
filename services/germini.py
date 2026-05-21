from google import genai
from google.genai import types
from bd import obter_configuracao
from common.exceptions import UsuarioError, SistemaError, JsonError, IAError, RequisicaoError
import json
import os

modelo_default = "gemini-2.5-flash" 

client = None
chat = None  

def verificar_conexao():
  """Verifica a conexão com a API."""
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

  print(f" {modelo} {chave}")
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
  configuracao = obter_configuracao()
  instrucao = f"""Você é uma assistente de sistemas embarcados para microcontroladores.
  Regras:
  - Apelido do usuário: {configuracao['apelido']}
  - Microcontrolador: {configuracao['nome_microcontrolador']}
  - Ver código: {configuracao['ver_codigo']}
  - Comentários no código: {configuracao['comentario_codigo']}
  - Nome do projeto: {configuracao['nome_projeto']}
  - Linguagem de programação arduino (extensao .ino)
  - Responda apenas sobre programação e microcontroladores.
  - Use bibliotecas suportadas pelo arduino-cli.
  """
  return types.GenerateContentConfig(
    system_instruction=instrucao,
    temperature=0.9
  )

def Enviar_Mensagem(mensagem: str):
  """Envia mensagem no chat principal (conversa humana)."""
  try:
    if not chat:
      raise SistemaError("Chat não iniciado. Verifique a API Key.")
    response = chat.send_message(mensagem)
    return response
  except Exception as e:
    print(f"Erro ao enviar: {e}")
    raise IAError("Problemas ao enviar a requisição para a IA.")

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
  return chat.get_history() if chat else []

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
  configuracao = obter_configuracao()
  
  # 1. Transformamos o histórico em um bloco de texto descritivo
  contexto_historico = ""
  for msg in chat.get_history():
    contexto_historico += f"{msg.role}: {msg.parts[0].text}\n"

  # 2. Configuração estrita para JSON
  config_json = types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.1, # Temperatura baixa para evitar erros no JSON
    system_instruction="Você é um gerador de arquivos JSON para sistemas embarcados. Retorne APENAS o JSON solicitado, sem explicações e NUNCA responda como MARKDOWN."
  )

  prompt_final = f"""
  Com base no histórico abaixo, gere os códigos necessários para o projeto.
  
  HISTÓRICO:
  {contexto_historico}
  
  ESTRUTURA JSON OBRIGATÓRIA:
  {{
    "numero_de_arquivos": int,
    "nome_projeto": "{configuracao['nome_projeto']}",
    "bibliotecas": ["biblioteca1", "biblioteca2"],
    "codigos": [
      {{
        "id": int,
        "nome_arquivo": "main.ino",
        "codigo": "string_do_codigo_aqui"
      }}
    ]
  }}
  Regras: Microcontrolador {configuracao['microcontrolador']}.
  """
  
  try:
    # Chamada direta (sem chat) para o modelo de arquivos
    # Usamos o mesmo modelo ou um diferente se preferir (ex: Pro)
    resposta = client.models.generate_content(
      model=modelo_default,
      contents=prompt_final,
      config=config_json
    )

    print(resposta.text)
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
  return Enviar_Mensagem("Recebi as configurações. Por favor, confirme se está pronto.")