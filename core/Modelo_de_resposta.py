"""
Modelos de resposta para a geração do código fonte.
"""
from typing import List
from pydantic import BaseModel, ConfigDict

class Codigo_Fonte_Base (BaseModel):
  id: int
  nome_arquivo: str
  codigo: str

class Projeto_Arduino_Base (BaseModel):
  """
  Modelo de resposta JSON suportadoo pelo GEMINI
  """
  numero_de_arquivos: int
  nome_projeto: str
  bibliotecas: List[str]
  codigos: List[Codigo_Fonte_Base]

class Codigo_Fonte_ChatGPT (Codigo_Fonte_Base):
  model_config = ConfigDict(extra='forbid')

class Projeto_Arduino_ChatGPT (Projeto_Arduino_Base):
  """
  Modelo de resposta JSON suportadoo pelo ChatGPT
  """
  model_config = ConfigDict(extra='forbid')
  codigos: List[Codigo_Fonte_ChatGPT]