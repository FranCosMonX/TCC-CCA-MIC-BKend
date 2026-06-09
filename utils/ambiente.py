from common.exceptions import SistemaError, AmbienteError, UsuarioError
import subprocess, os
from bd import obter_configuracao
from common.archive import salvar_arquivo, criar_diretorios
from pathlib import Path

ARDUINO_CLI_EXE = 'C:\\Program Files\\Arduino CLI\\arduino-cli.exe'
LOC_PATH = os.getcwd()

def preparando_ambiente(package_id:str=None):
  """
  Utilizado para instalar o arduino-cli e configurar a placa do microcontrolador usando o arduino-cli
  Params:
    id_microcontrolador (str): Identificador do pacote do microcontrolador usado pelo arduino-cli (não o ID dele para compilar = FQBN)
  Exceptions:
    SistemaError: Erros do sistema  
    UsuarioError: URI informada pelo o usuário é inválida.
    AmbienteError: Houve um problema ao configurar o ambiente.
  """
  if package_id is None:
    raise SistemaError("Parâmetro id_microcontrolador é nulo.")
  
  configuracao = obter_configuracao()
  if configuracao['diretorio'] is ['', None]:
    raise UsuarioError("É necessário definir parâmetros gerais antes de configurar o ambiente de execução.")
  
  URI_CONFIG = os.path.join(configuracao['diretorio'],'config')
  COMMAND = 'C:\\Program Files\\Arduino CLI\\arduino-cli.exe'
  comando_atualizar_index = ""
  if package_id == "esp32:esp32":
    local_arquivo = Path(os.getcwd()) / 'source' / 'package' / 'package_esp32_index.json'
    comando_atualizar_index = f"\"{COMMAND}\" core update-index --additional-urls file:///{local_arquivo}"
  else:
    comando_atualizar_index = f"""
    "{COMMAND}" core update-index
    
    "{COMMAND}" core install {package_id}
    """
  
  BAT_TEXT_INICIAL = f"""@echo off
  
  "{COMMAND}"
  IF %ERRORLEVEL% NEQ 0 (
      echo Arduino CLI nao instalado. Sera instalado em breve em 5 segundos
      
      winget install "Arduino CLI" --silent --accept-package-agreements --accept-source-agreements
      
      echo Arduino CLI instalado com exito.
      goto fim
  ) 

  echo Arduino CLI ja esta instalado

  :fim
  
  {comando_atualizar_index}
  
  exit /b 0
  """
  DIRETORIO_CONFIG = Path(configuracao.get('diretorio')) / 'config'
  if not os.path.exists(DIRETORIO_CONFIG):
    os.makedirs(DIRETORIO_CONFIG)
  # criar_diretorios("config")
  salvar_arquivo(URI_CONFIG, 'ambiente_inicial.bat', BAT_TEXT_INICIAL)
  
  retorno = subprocess.run(os.path.join(URI_CONFIG, 'ambiente_inicial.bat'), shell=True)

  if retorno.returncode != 0:
    raise AmbienteError("Erro ao executar Script para a instalação dos pacotes Arduino-CLI no terminal")
  
  print("DEBUG - Terminou de preparar o ambiente e de configurar a placa")

def instalar_bibliotecas(bibliotecas: list):
  """
  Função necessária para instalar as

  Args:
      bibliotecas (list): _description_
  """
  
  RETORNO = []
  for biblioteca in bibliotecas:
    CODIGO = ["arduino-cli", "lib", "install", biblioteca]
    print(CODIGO)
    retorno = subprocess.run(CODIGO, capture_output=True, text=True)

    def estaInstalado(text=str):
      return text.find("Installed") != -1 or text.find("installed") != -1
    RETORNO.append(estaInstalado(retorno.stdout))
    # print(retorno.stdout)
    # print(estaInstalado(retorno.stdout))
  
  return RETORNO