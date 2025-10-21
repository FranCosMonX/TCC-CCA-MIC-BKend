import re, os



SCRIPT_INICIALIZAR_MIC = """
@echo off
"""

def construir_script_placa(id:str):
  """
  Responsável por instalar todos os recursos necessários para compilar e gravar os códigos no microcontrolador.
  Vale ressaltar que a instalação de drives necessitam de permissão do usuário local onde o backend
  estará sendo executado.
  
  Args:
    id (str): FQBN - Identificador da placa no ambiente de compilação e execução do arduino.
  """
  if re.search(r'arduino:esp32'):
    SCRIPT_INICIALIZAR_MIC = """
    arduino-cli core install arduino:esp32
    """
  elif re.search(r'arduino:avr'):
    SCRIPT_INICIALIZAR_MIC = """
    arduino-cli core install arduino:avr
    """
  
  with open('config_mic.bat', 'r', encoding='utf-8') as arq:
    arq.write(SCRIPT_INICIALIZAR_MIC)