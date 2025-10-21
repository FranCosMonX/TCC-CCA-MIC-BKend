from bd import obter_configuracao
from common.exceptions import UsuarioError, SistemaError
import subprocess

def criar_projeto(nome:str):
  """
  Criar projetos arduinos limpos com o nome do arquivo principal sendo o nome do projeto.
  
  Args:
    nome (`str`): nome da pasta que conterá todos os arquivos de código do projeto.
    
  Dependente:
    URI: Salvo no Banco de Dados.
  """
  try:
    configs = obter_configuracao()
    URI = configs['diretorio']
    
    BAT_COMAND = f"""
    @echo off
    cd {URI}
     arduino-cli sketch new {nome}
    """
    
    retorno = subprocess.run(
      BAT_COMAND,
      shell=True,
      text=True
    )
    
    if retorno.stderr:
      raise SistemaError("Houve um erro ao executar o comando BAT para a criação do projeto.")
      
  except SistemaError as sys_err:
    raise SistemaError(sys_err.mensagem)
  except Exception as e:
    raise UsuarioError("Impossivel criar o projeto. Não há dados salvos ou houve problema ao salva-los.")

def compilar():
  pass

def gravar():
  pass