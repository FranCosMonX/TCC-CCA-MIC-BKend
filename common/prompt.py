from bd import obter_configuracao
from common.exceptions import UsuarioError

instrucao_modelo_chat = ""
prompt_atual = ""
prompt_gerar_arquivo = ""

def gerar_instrucao_chat():
  global instrucao_modelo_chat
  configuracao = obter_configuracao()
  instrucao_modelo_chat = f"""Você é uma assistente de sistemas embarcados para microcontroladores.
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

def alterar_prompt_atual(apenas_mudanca: str, prompt_limpo: bool = False):
  global prompt_atual

  if prompt_limpo:
    prompt_atual = ""
  
  prompt_atual += f"SISTEMA: O usuário alterou as escolhas: {apenas_mudanca}. Considere os novos pedidos. NÃO CITE ESTA MENSAGEM.\n"
  return prompt_atual

def obter_prompt_atual():
  global prompt_atual
  return prompt_atual

def alterar_prompt_gerar_arquivo(historico):
  global prompt_gerar_arquivo
  configuracao = obter_configuracao()

  if len(historico) == 0:
    raise UsuarioError("Não houve interação com o chat para ser gerado um código fonte. Dados Nulos.")

  contexto_historico = ""
  for msg in historico:
    contexto_historico += f"{msg.role}: {msg.parts[0].text}\n"

  print(contexto_historico)
  prompt_gerar_arquivo = f"""
  Com base no histórico abaixo, gere os códigos necessários para o projeto. O arquivo principal do projeto tem o mesmo nome do Projeto independentemente do conteudo, assim como instruido logo a seguir. Nunca troque o nome do projeto e arquivo principal.
  
  HISTÓRICO:
  {contexto_historico}
  
  ESTRUTURA JSON OBRIGATÓRIA RESPEITANDO CHAVES:
  {{
    "numero_de_arquivos": int,
    "nome_projeto": "{configuracao['nome_projeto']}",
    "bibliotecas": ["biblioteca1", "biblioteca2"],
    "codigos": [
      {{
        "id": int,
        "nome_arquivo": "{configuracao['nome_projeto']}.ino",
        "codigo": "string_do_codigo_aqui"
      }}
    ]
  }}
  Regras: Microcontrolador {configuracao['nome_microcontrolador']}.
  """
  return prompt_gerar_arquivo