from common.exceptions import SistemaError
from typing import Literal
from bd import criar_registro_chat, obter_registros_chat

def registrar_mensagem_chat(entidade: Literal['usuario', 'ia', 'sistema', 'ia_model_create_json'] = None, mensagem: str = None):
  """
  Função utilizada para registrar toda e qualquer mensagem no sistema que será mostrado para o usuário.
  """
  if not entidade or not mensagem:
    raise SistemaError("Houve um problema ao registrar mensagem de chat. A mensagem ou a entidade se encontra nula ou inexistente.")
  
  try:
    criar_registro_chat(entidade, mensagem)
  except Exception as e:
    raise SistemaError("Houve um problema em salvar a mensagem do chat no Banco de Dados.")
  
def obter_registro_as_str():
  """
  Usado para obter o registro salvo da conversa como uma string.
  """
  registro_completo = obter_registros_chat()

  output = ""
  for registro in registro_completo:
    output += f"entidade: {registro.get('entidade')}, conteudo: {registro.get('mensagem')}\n" 
  return output