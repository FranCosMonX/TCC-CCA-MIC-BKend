import subprocess
import shutil
from pathlib import Path
from bd import obter_configuracao
from common.exceptions import UsuarioError, SistemaError, AmbienteError
from common.archive import criar_diretorios
from .ambiente import ARDUINO_CLI_EXE

def criar_projeto(nome: str = None):
  """
  Cria projetos Arduino limpos utilizando o arduino-cli.
  """
  try:
    configs = obter_configuracao()
    diretorio_base = configs.get('diretorio')
    nome_projeto = configs.get('nome_projeto')

    # Validações Iniciais
    if not diretorio_base:
      raise UsuarioError("Configuração incompleta: especifique o diretório base.")
    
    if not nome_projeto:
      raise UsuarioError("Configuração incompleta: nome do projeto não definido.")

    nome = nome or nome_projeto
    
    # Caminhos usando Pathlib (Moderno e Seguro)
    uri_executavel = Path(diretorio_base) / 'executavel'
    project_path = uri_executavel / nome

    # Garante que a pasta 'executavel' existe
    if not uri_executavel.exists():
      criar_diretorios('executavel')

    # Se o projeto já existe, removemos para garantir uma criação limpa (conforme a lógica original tentava fazer)
    if project_path.exists():
      try:
        shutil.rmtree(project_path) # Forma cross-platform de remover diretórios com conteúdo
      except Exception as e:
        raise SistemaError(f"Falha ao remover projeto antigo: {e}")

    # Execução do comando via lista (evita Shell Injection e problemas de aspas)
    comando = [ARDUINO_CLI_EXE, "sketch", "new", str(project_path)]
    
    # subprocess.run moderno
    resultado = subprocess.run(
      comando,
      capture_output=True,
      text=True,
      encoding='utf-8'
    )

    if resultado.returncode != 0:
      raise SistemaError(f"Erro no arduino-cli: {resultado.stderr}")
    
    resposta = f"Projeto '{nome}' criado com sucesso em {project_path}.\n"
    return resposta
  except SistemaError as sys_err:
    raise AmbienteError(str(sys_err))
  except Exception as e:
    raise UsuarioError("Impossível criar o projeto. Verifique os dados de configuração.")

def guardar_codigo(codigo: str, nome_arquivo: str = None):
  """
  Grava o código fonte no arquivo .ino do projeto.
  """
  configuracao = obter_configuracao()
  nome_projeto = configuracao.get('nome_projeto')
  
  # Define caminhos
  diretorio_base = Path(configuracao.get('diretorio', '')) / 'executavel'
  projeto_path = diretorio_base / nome_projeto

  # Verifica se o diretório do projeto existe
  if not projeto_path.exists():
    try:
      criar_projeto()
    except Exception:
      raise SistemaError(f"Pasta do projeto {nome_projeto} não encontrada e falha ao recriar.")

  # Define o nome do arquivo (default: nome_do_projeto.ino)
  if nome_arquivo is None:
    nome_arquivo = f"{nome_projeto}.ino"
  
  arquivo_final = projeto_path / nome_arquivo

  try:
    # Gravação usando gerenciador de contexto com encoding explícito
    with open(arquivo_final, mode='w', encoding='utf-8') as arq:
      arq.write(codigo)
    
    resposta = f"Código do projeto {nome_projeto} gravado com sucesso em: {nome_arquivo}.\n"
    return resposta
  except Exception as e:
    raise SistemaError(f"Falha crítica ao tentar gravar o código no sistema de arquivos. {e}")

def compilar_projeto():
  """
  Compila o projeto Arduino utilizando o arduino-cli.
  Retorna o log da compilação em caso de sucesso.
  """
  try:
    configs = obter_configuracao()
    diretorio_base = configs.get('diretorio')
    nome_projeto = configs.get('nome_projeto')
    fqbn = configs.get('fqbn') # Ex: arduino:esp32:esp32

    # 1. Validações de ambiente
    if not fqbn:
      raise UsuarioError("Microcontrolador não configurado (FQBN ausente).")
    
    uri_executavel = Path(diretorio_base) / 'executavel'
    project_path = uri_executavel / nome_projeto

    if not project_path.exists():
      raise SistemaError(f"Pasta do projeto não encontrada: {project_path}")

    print(f"Iniciando compilação para {fqbn}...")

    # 2. Construção do Comando
    # arduino-cli compile --fqbn <placa> <caminho_do_projeto>
    comando = [
      ARDUINO_CLI_EXE,
      "compile",
      "--fqbn", fqbn,
      str(project_path)
    ]

    # 3. Execução do subprocesso
    resultado = subprocess.run(
      comando,
      capture_output=True,
      text=True,
      encoding='utf-8'
    )

    # 4. Tratamento de Retorno
    if resultado.returncode != 0:
      # Erro de compilação (erro de sintaxe no código C++, bibliotecas faltando, etc)
      print("DEBUG - Erro de compilação detectado.")
      # Retornamos o stderr para que o usuário saiba o que deu errado no código
      raise AmbienteError(f"Erro de Compilação o projeto {nome_projeto}:\n\n{resultado.stderr}")

    print("DEBUG - Compilação concluída com sucesso!")
    return f"Projeto {nome_projeto} compilado com sucesso!\n\n{resultado.stdout}"
  except SistemaError as sys_err:
    # Erros de lógica de compilação ou sistema
    raise AmbienteError(str(sys_err.mensagem))
  except Exception as e:
    raise SistemaError(f"Falha interna ao tentar compilar o projeto {nome_projeto}: {e}")
  
def gravar_projeto():
  try:
    configs = obter_configuracao()
    diretorio_base = configs.get('diretorio')
    nome_projeto = configs.get('nome_projeto')
    fqbn = configs.get('fqbn')

    process = subprocess.run(
      [ARDUINO_CLI_EXE, 'board', 'list'],
      capture_output=True,
      text=True
    )

    if process.returncode != 0:
      raise AmbienteError('Houve um problema na configuração do ambiente utilizada na descoberta da porta USB.')
    dados_saida = process.stdout
    
    porta_USB = ""
    linhas = dados_saida.split("\n")
    for linha in linhas:
      print(linha)
      if "USB" in linha:
        dados = " ".join(linha.split()).split(" ")
        print(f"DEBUG - Usando {dados[0]} como porta para gravar o código")
        porta_USB = dados[0]
    
    if porta_USB == "":
      raise UsuarioError("Microcontrolador não está conectado, ou há multiplos aparelhos conextados nas portas USB.")

    uri_executavel = Path(diretorio_base) / 'executavel'
    project_path = uri_executavel / nome_projeto

    process = subprocess.run(
      [ARDUINO_CLI_EXE, 'upload', project_path, '-b', fqbn, '-p', porta_USB],
      capture_output=True,
      text=True
    )

    dados_saida = process.stdout
    if process.returncode != 0:
      raise AmbienteError(f'Houve um problema na configuração do ambiente utilizada na gravação do codigo no microcontrolador.\n\n{dados_saida}')

    return dados_saida
  except AmbienteError as aE:
    raise SistemaError(f"DEBUG - ERROR: Problema na configuração do ambiente. {aE.mensagem}")
  except UsuarioError as uE:
    raise UsuarioError(uE.mensagem)
  except Exception as e:
    raise SistemaError(f"DEBUG - ERROR projeto.py em gravar_projeto. {e}")