from common.exceptions import SistemaError
from bd import criar_registro_chat

def registrar_mensagem_chat(entidade = None, mensagem: str = None):
  """
  Função utilizada para registrar toda e qualquer mensagem no sistema que será mostrado para o usuário.
  """
  if not entidade or not mensagem:
    raise SistemaError("Houve um problema ao registrar mensagem de chat. A mensagem ou a entidade se encontra nula ou inexistente.")
  
  try:
    criar_registro_chat(entidade, mensagem)
  except Exception as e:
    raise SistemaError("Houve um problema em salvar a mensagem do chat no Banco de Dados.")