import re, os

BAT_TEXT_INICIAL = """@echo off
echo Verificando existencia da arduino-cli
echo.
arduino-cli --version
IF %ERRORLEVEL% NEQ 0 (
    echo Arduino CLI nao instalado. Será instalado em breve em 5 segundos
    timout 5 /nobreak
    echo.
    winget install "Arduino CLI"
    echo Arduino CLI instalado com exito.
    goto fim
) ELSE {
    echo Arduino CLI ja esta instalado
}
:fim
arduino-cli --version
"""

SCRIPT_INICIALIZAR_MIC = """
@echo off
arduino-cli config init
"""

def construir_script_placa(placa:str):
    if re.search(r'ESP32'):
        SCRIPT_INICIALIZAR_MIC = """
        arduino-cli core install arduino:esp32
        """
    elif re.search(r'Arduino'):
        SCRIPT_INICIALIZAR_MIC = """
        arduino-cli core install arduino:avr
        """
    
    with open('config_mic.ino', 'r', encoding='utf-8') as arq:
        arq.write(SCRIPT_INICIALIZAR_MIC)

def construir_script_criar_projeto(uri, nome:str):
  """
  Criar projetos arduinos limpos com o nome do arquivo principal sendo o nome do projeto.
  
  Args:
    uri: contem a URI onde estará a pasta do projeto
    nome (`str`): nome da pasta que conterá todos os arquivos de código do projeto.
  """
  if not os.path.exists(os.path.join(uri,nome)):
    os.mkdir(os.path.join(uri,nome))
    
  CODE = f"""
  cd {uri}
  arduino-cli sketch new {nome}
  """
  
  with open(os.path.join(uri,str(nome+'.ino')), 'w', encoding='utf-8') as arq:
    arq.write(CODE)
    
  return os.path.join(uri,str(nome+'.ino'))