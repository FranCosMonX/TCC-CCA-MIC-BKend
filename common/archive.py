from bd import obter_configuracao
from common.exceptions import SistemaError, UsuarioError
from pathlib import Path
import os

def criar_diretorios(nome:str):
  """
  Função utilizada para criar diretórios dentro de uma localidade informada pelo usuário
  
  Args:
    nome (str): `<string>` contendo o nome + extensão.
      
  Exceptions:
    SistemaError: erro inesperado.
    UsuarioError: O usuário passou o caminho errado.
  """
    
  try:
    user_config = obter_configuracao()
    if os.path.exists(user_config['diretorio']):
      raise UsuarioError("Impossivel criar o diretório de execução pois o caminho passado é inválido.")
    
    """Cria os diretórios 'executavel' se eles não existirem."""
    uri = user_config['diretorio']
    diretorio_novo = os.path.join(uri, nome)

    if not os.path.exists(diretorio_novo):
      os.makedirs(diretorio_novo)
      print(f"Diretório '{diretorio_novo}' criado com sucesso.")
  except Exception as e:
    SistemaError(f"Erro inesperado na função criar diretório: {e}")

def salvar_arquivo(diretorio:str, nome_arquivo: str, conteudo: str, diretorio_do_projeto:bool= False):
  """
  Salva o conteúdo em um arquivo no diretório 'temporario'.
  O arquivo é sobrescrito se já existir.

  Args:
    diretorio (`string`) : Diretorio onde o arquivo será salvo
    nome_arquivo (`string`): O nome do arquivo a ser salvo (ex: `'meu_codigo.c'`).
    conteudo (`string`): O conteúdo a ser escrito no arquivo.
    diretorio_do_projeto (`boolean`) : Se o diretório leva em consideração onde o projeto está armazenado. Se `True`, as pastas do diretório passado serão criados com base na URI do projeto. Se `False`, o arquivo será salvo no diretório passado e já existente.
  
  Exceptions:
    SistemaError: erro inesperado.
  """

  if diretorio_do_projeto and not os.path.exists(diretorio):
    os.makedirs(Path(diretorio))

  if not os.path.exists(diretorio):
    SistemaError(f"Archive.py em salvar_arquivo: O diretório {diretorio} não existe.")
  
  caminho_completo = os.path.join(diretorio, nome_arquivo)
  print(f'DEBUG - CRIANDO ARQUIVO: {caminho_completo}')
  try:
    with open(caminho_completo, 'w', encoding='utf-8') as f:
      f.write(conteudo)
  except Exception as e:
    SistemaError(f"Erro ao salvar o arquivo '{nome_arquivo}': {e}")

def criar_arquivo_bat(caminho: str, text:str):
  """
  Necessário para criar arquivos bats emum caminho especificado.

  Args:
    caminho (str): _description_
    text (str): _description_
  Exceptions:
    SistemaError: Erro possivelmente esperado caso o caminho passado não exista.
  """
  try:
    with open(caminho, encoding='UTF-8', mode='w') as arq:
      arq.write(text)
  except:
    SistemaError("Houve um erro ao criar o arquivo bat no caminho especificado.")