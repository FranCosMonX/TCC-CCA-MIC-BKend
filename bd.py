"""
### Descrição

Contém algumas das interações diretas com o Banco de Dados, tais como INSERT e SELECT contendo diversos parâmetros diferentes.
"""
from flask import Flask
from common.exceptions import SistemaError, UsuarioError
import sqlite3

app = Flask(__name__)
DATABASE = 'database.bd'

def get_db():
  """
  ### Descrição
  
  Conenctar o Banco de Dados. Importante ser executado ao menos uma vez para que possa ser criado o arquivo do Banco de Dados.
  """
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  return db

def init_db():
  """
  ### Descrição
  
  Contém os códigos necessários para executar os arquivos de geração de tabelas do SQLite.
  """
  with app.app_context():
    db = get_db()
    with app.open_resource('./models/configuracao.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()
    
def criar_config_default():
  """
  ### Descrição
  Cria um indice contendo os dados
  `apelido, diretorio, microcontrolador, ai, key_ai_api = None, None, None, None, None` e `ver_codigo, comentario_codigo = False, False`
  
  ### Exceções
  Caso dê algum erro na criação, deverá gerar uma exceção do Banco de Dados ou da própria aplicação.
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM configuracao')
    resultado = cursor.fetchall()
    
    if len(resultado) == 0:
      cursor.execute('INSERT INTO configuracao(apelido,diretorio,microcontrolador,ia,key_ai_api,ver_codigo,comentario_codigo,api_key_valid,id_microcontrolador) VALUES (?,?,?,?,?,?,?,?,?)',
                     (None, None, None, None, None, 0, 0, 0, None))
      db.commit()
    else:
      print('Já tem uma configuração salva.')
  except sqlite3.Error as e:
    raise Exception(f'error: {str(e)}')
  finally:
    db.close()
    print('funcao finalizada')
    
def obter_configuracao():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM configuracao')
    dados = cursor.fetchall()
    print([dict(row) for row in dados])
    db.close()
    
    if len(dados) == 0:
      raise Exception(f'Não há configurações salvas. Registre algo primeiro.')
    
    config = dados[0]
    return {
      "id": config["id"],
      "apelido": config["apelido"],
      "diretorio": config["diretorio"],
      "microcontrolador": config["microcontrolador"],
      "id_microcontrolador": config["id_microcontrolador"],
      "ia": config["ia"],
      "key_ai_api": config["key_ai_api"],
      "api_key_valid": config["api_key_valid"],
      "ver_codigo": config["ver_codigo"],
      "comentario_codigo": config["comentario_codigo"],
    }
  except Exception as e:
    raise Exception(f'error: {str(e)}')

def atualiza_chave_acesso_ai(api_key:str):
  """
  Unica forma de atualizar a chave de acesso da AI.
  
  Exceptions:
    Generico (Exception): informando que houve um erro de Sistema (500).
  
  Returns:
    Mensagem (str): Informando que os dados foram salvos
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE configuracao SET key_ai_api = ? WHERE id = ?', (api_key, 1))
    db.commit()
    return 'Dados salvos com sucesso.'
  except Exception as e:
    raise Exception(f'Erro: {str(e)}')
  finally:
    db.close()

def edit_validacao_api_key(status):
  """
  Unica forma de atualizar o status chave de acesso válido da AI.
  
  Exceptions:
    Generico (Exception): informando que houve um erro de Sistema (500).
  
  Returns:
    Mensagem (str): Informando que os dados foram salvos
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE configuracao SET api_key_valid = ? WHERE id = ?', (status, 1))
    db.commit()
    return 'Dados salvos com sucesso.'
  except Exception as e:
    raise Exception(f'Erro: {str(e)}')
  finally:
    db.close()
  
def atualizar_dadosConf_gerais(diretorio, ai, ver_codigo, comentario_codigo):
  """
  Usado para atualizar apenas os dados a seguir.
  
  Params:
    Diretório (str): onde será armazenado todos os códigos salvos
    Ai (str): O nome da Inteligência Artificial utilizada
    Ver_codigo (bool): Informando se a AI precisará fornecer os códigos no chat
    Comentario_codigo (bool): Informando se a AI precisará explicar o código no chat
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE configuracao SET diretorio = ?, ia = ?, ver_Codigo = ?, comentario_codigo = ? WHERE id = ?', (diretorio, ai, ver_codigo, comentario_codigo, 1,) )
    db.commit()
    
    return 'Dados salvos com sucesso.'
  except Exception as e:
    raise Exception(f'Erro: {str(e)}')
  finally:
    db.close()

def atualizar_dados_mic(id_microcontrolador, microcontrolador):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE configuracao SET id_microcontrolador = ?, microcontrolador = ? WHERE id = ?', (id_microcontrolador, microcontrolador, 1) )
    db.commit()
    
    return 'Dados atualizados com sucesso!'
  except Exception as e:
    print(f'error: {e}')
    raise Exception(f'Erro: {str(e)}')
  finally:
    db.close()
    
def atualizar_apelido(apelido):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM configuracao')
    dados = cursor.fetchall()
    if (
        dados[0]['microcontrolador'] in ['', None] or
        #dados[0]['api_key_valid'] in [0] or
        dados[0]['key_ai_api'] in ['', None] or
        dados[0]['diretorio'] in ['', None]
      ):
      raise Exception(f'Não poderá presseguir sem adicionar as seguintes informações necessárias: Microcontrolador, Chave da API (com validação) e diretório')
    
    
    cursor.execute('UPDATE configuracao SET apelido = ? WHERE id = ?', (apelido, 1) )
    db.commit()
    db.close()
    return 'Apelido salvo com sucesso!'
  except Exception as e:
    print('erro aqui')
    print(str(e))
    raise Exception(f'Erro: {str(e)}')