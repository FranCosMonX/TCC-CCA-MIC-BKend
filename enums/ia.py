"""
Contem todos os Enums relacionados a IA da aplicação
"""
from enum import StrEnum

class IAName(StrEnum):
  """
Armazena o nome das IAs usadas nessa aplicação da mesma forma como armazenado no Banco de Dados.
"""
  GEMINI = 'Gemini'
  CHATGPT = 'ChatGPT'

  def __str__(self):
    return self.value