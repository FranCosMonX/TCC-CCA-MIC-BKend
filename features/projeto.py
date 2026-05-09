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
        
    print(f"Projeto '{nome}' criado com sucesso em {project_path}")

  except SistemaError as sys_err:
    raise AmbienteError(str(sys_err))
  except Exception as e:
    # Log de erro real para o desenvolvedor e erro genérico para a camada superior
    print(f"Erro detalhado: {e}")
    raise UsuarioError("Impossível criar o projeto. Verifique os dados de configuração.")

def gravar_codigo(codigo: str, nome_arquivo: str = None):
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
    
    print(f"Código gravado com sucesso em: {nome_arquivo}")
  except Exception as e:
    print(f"Erro ao gravar arquivo: {e}")
    raise SistemaError("Falha crítica ao tentar gravar o código no sistema de arquivos.")

def compilar():
    """
    Placeholder para futura implementação de compilação.
    """
    pass