from bd import obter_configuracao
from common.exceptions import UsuarioError, SistemaError, AmbienteError
from common.archive import criar_diretorios
import subprocess, os
from .ambiente import ARDUINO_CLI_EXE

def criar_projeto(nome:str=None):
  """
  Criar projetos arduinos limpos com o nome do arquivo principal sendo o nome do projeto.
  
  Args:
    nome (`str`): nome da pasta que conterá todos os arquivos de código do projeto.
    
  Dependente:
    URI: Salvo no Banco de Dados.
  """
  try:
    configs = obter_configuracao()
    if configs['diretorio'] is None:
      raise UsuarioError("Não há dados suficientes para criar o projeto: especifique o diretório.")
    
    if configs['nome_projeto'] is None or len(configs['nome_projeto']) < 1:
      raise UsuarioError("Há dados faltando: nome de projeto.")
    
    if nome is None:
      nome = configs['nome_projeto']
      
    URI = os.path.join(configs['diretorio'], 'executavel')
    if not os.path.exists(URI):
      criar_diretorios('executavel')
      
    if not os.path.exists(os.path.join(URI, configs['nome_projeto'])):
      CODIGO_REMOVE = ['rmdir', '/s','/q',os.path.join(URI, configs['nome_projeto'])]
      
      retorno_slc_remove = subprocess.run(CODIGO_REMOVE, shell=True, stderr=True)
      if len(retorno_slc_remove.stderr) > 0:
        raise SistemaError("Houve um problema em remover o antigo projeto")
      
    PROJECT_URI = os.path.join(URI,f'{nome}')
    if not os.path.exists(PROJECT_URI):
      BAT_COMAND = f"""
      @echo off
      cd {URI}
      {ARDUINO_CLI_EXE} sketch new {nome}
      """
      
      retorno = subprocess.run(
        BAT_COMAND,
        shell=True,
        text=True
      )
    
      if retorno.stderr:
        raise SistemaError("Houve um erro ao executar o comando BAT para a criação do projeto.")
    else:
      print('projeto já existe.')
  except SistemaError as sys_err:
    raise AmbienteError(sys_err.mensagem)
  except Exception as e:
    raise UsuarioError("Impossivel criar o projeto. Não há dados salvos ou houve problema ao salva-los.")

def gravar_codigo(codigo:str, nome_arquivo:str=None):
  configuracao = obter_configuracao()
  
  DIRETORIO_BASE = os.path.join(configuracao['diretorio'],'executavel')
  if not os.path.exists(DIRETORIO_BASE):
    raise UsuarioError(f"Houve um problema ao encontrar o diretório: {DIRETORIO_BASE}")
  
  DIRETORIO_PROJOETO = os.path.exists(os.path.join(DIRETORIO_BASE, configuracao['nome_projeto']))
  if not os.path.exists(DIRETORIO_PROJOETO):
    try:
      CODIGO_DEL_PROJETO = ['rm', configuracao['nome_projeto']]
      retorno = subprocess.run(CODIGO_DEL_PROJETO, shell=True, stderr=True)
      if len(retorno.stderr) > 0:
        raise SistemaError(f"Houve um problema para remover a pasta {configuracao['nome_projeto']}")
      
      criar_projeto()
    except Exception as e:
      raise SistemaError("Houve um problema inesperado na função gravadr_codigo() em projeto.py.")

  if nome_arquivo is None:
    nome_arquivo = f"{configuracao['nome_projeto']}.ino"
  try:
    with open(os.path.join(DIRETORIO_PROJOETO, nome_arquivo, mode='w', encoding='utf-8',)) as arq:
      arq.write(codigo)
    
    print("código gravado")
  except Exception as e:
    raise SistemaError("Houve um problema inesperado ao tentar gravar o código no arquivo.")
  
def compilar():
  pass