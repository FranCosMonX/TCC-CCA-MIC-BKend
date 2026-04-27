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

def add_modelo_ia(ia_name, modelo_disponivel):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO ia(nome_ia, modelo_disponivel) VALUES (?,?)', (ia_name, modelo_disponivel))
    db.commit()
    print('DEBUG - Modelo salvo como sucesso')
  except sqlite3.Error as e:
    raise Exception(f'error: {str(e)}')
  finally:
    db.close()
    print('funcao finalizada')

def obter_ias_disponiveis():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT nome_ia FROM ia")
    resultado = cursor.fetchall()

    ias_disponiveis = [dict(linha) for linha in resultado]
    resultado = []
    for index, ia in enumerate(ias_disponiveis):
      resultado.append({"aux_map_key":index, "nome_ia": ia['nome_ia']})
    return resultado
  except Exception as e:
    print(f"DEBUG - ERROR bd.py em obter_ias_disponiveis() - {e}")
    return None
  finally:
    db.close()

def obter_modelos_disponiveis():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ia")
    resultado = cursor.fetchall()

    ias_disponiveis = [dict(linha) for linha in resultado]
    print(ias_disponiveis)
    return ias_disponiveis
  except Exception as e:
    print(f"DEBUG - ERROR bd.py em obter_ias_disponiveis() - {e}")
    return None
  finally:
    db.close()
    
def obter_modelo_por_nome_ia(nome_ia:str):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM ia WHERE nome_ia = ?', (nome_ia,))
    resultado = cursor.fetchall()

    resultado = [dict(linha) for linha in resultado]
    
    if len(resultado) == 0:
      return None
    print(resultado)
    return resultado
  except Exception as e:
    raise Exception(f' DEBUG - error em obter_modelo_por_nome_ia em bd.py: {str(e)}')
  finally:
    db.close()
  
def obter_modelo_por_id(id):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT modelo_disponivel FROM ia WHERE id = ?', (id,))
    resultado = cursor.fetchone()

    if resultado is None:
      print("DEBUG - ID não encontrado.")
      return None
    resultado = dict(resultado)
    return resultado
  except Exception as e:
    raise Exception(f' DEBUG - error em obter_modelo_por_nome_ia em bd.py: {str(e)}')
  finally:
    db.close()

def tem_nome_ia(nome_ia: str):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT 1 FROM ia WHERE nome_ia = ?', (nome_ia,))
    resultado = cursor.fetchone()

    return resultado is not None
  except Exception as e:
    raise Exception(f' DEBUG - error em obter_modelo_por_nome_ia em bd.py: {str(e)}')
  finally:
    db.close()

def tem_modelo_da_ia(nome:str, modelo:str):
  """
  Utilizado para verificar e resgatar o id de um modelo de ia em especifico
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM ia WHERE nome_ia = ? and modelo_disponivel = ?', (nome,modelo,))
    resultado = cursor.fetchone()

    return None if resultado is None else dict(resultado)['id']
  except Exception as e:
    raise Exception(f' DEBUG - error em obter_modelo_por_nome_ia em bd.py: {str(e)}')
  finally:
    db.close()

def criar_config_default():
  """
  ### Descrição
  Cria um indice contendo os dados
  `apelido, diretorio, microcontrolador, id_ia, key_ai_api = None, None, None, None, None` e `ver_codigo, comentario_codigo = False, False`
  
  ### Exceções
  Caso dê algum erro na criação, deverá gerar uma exceção do Banco de Dados ou da própria aplicação.
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM configuracao')
    resultado = cursor.fetchall()
    
    if len(resultado) == 0:
      cursor.execute('INSERT INTO configuracao(nome_projeto,apelido,diretorio,microcontrolador,id_ia,key_ai_api,ver_codigo,comentario_codigo,api_key_valid,id_microcontrolador) VALUES (?,?,?,?,?,?,?,?,?,?)',
                     (None, None, None, None, None, None, 0, 0, 0, None))
      db.commit()
    else:
      print('Já tem uma configuração salva.')
  except sqlite3.Error as e:
    raise Exception(f'error: {str(e)}')
  finally:
    db.close()
    print('funcao finalizada')

def resetar_configs():
  """
  Usado para remover todos os dados de configuração salvos.

  Raises:
      SistemaError: Problema ao resetar os dados do arquivo.
  """
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE configuracao SET nome_projeto = ?, apelido = ?, diretorio = ?, microcontrolador = ?, id_ia = ?, key_ai_api = ?, ver_codigo = ?, comentario_codigo = ?, api_key_valid = ?, id_microcontrolador = ? WHERE id = ?', (None, None, None, None, None, None, False, False, False, None, 1))
    db.commit()
  except Exception as e:
    print(e)
    raise SistemaError("Problema ao atualizar os dados para default")
    
def obter_configuracao():
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM configuracao JOIN ia ON configuracao.id_ia = ia.id')
    dados = cursor.fetchone()
    db.close()
    
    if len(dados) == 0:
      raise Exception(f'Não há configurações salvas. Registre algo primeiro.')
    
    config = dict(dados)
    print(config)
    return config
  except Exception as e:
    raise Exception(f'error: {str(e)}')

def atualiza_chave_acesso_ai(ia, api_key:str):
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
    cursor.execute('UPDATE configuracao SET id_ia = ?, key_ai_api = ? WHERE id = ?', (ia, api_key, 1))
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
  
def atualizar_dadosConf_gerais(nome_projeto, diretorio, ver_codigo, comentario_codigo):
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
    cursor.execute('UPDATE configuracao SET nome_projeto = ?, diretorio = ?, ver_Codigo = ?, comentario_codigo = ? WHERE id = ?', (nome_projeto, diretorio, ver_codigo, comentario_codigo, 1,) )
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