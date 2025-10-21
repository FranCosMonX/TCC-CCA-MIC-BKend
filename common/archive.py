import os, subprocess
from services.germini import obter_configuracao

def criar_diretorios(nome:str):
    """
    Função utilizada para criar diretórios dentro de uma localidade informada pelo usuário
    
    Args:
        nome (str): `<string>` contendo o nome + extensão.
    """
    user_config = obter_configuracao()
    
    """Cria os diretórios 'temporario' e 'executavel' se eles não existirem."""
    uri = user_config['diretorio']
    diretorio_novo = os.path.join(uri, nome)

    if not os.path.exists(diretorio_novo):
        os.makedirs(diretorio_novo)
        print(f"Diretório '{diretorio_novo}' criado com sucesso.")

def salvar_arquivo(diretorio:str, nome_arquivo: str, conteudo: str):
    """
    Salva o conteúdo em um arquivo no diretório 'temporario'.
    O arquivo é sobrescrito se já existir.

    Args:
        nome_arquivo (str): O nome do arquivo a ser salvo (ex: `'meu_codigo.c'`).
        conteudo (str): O conteúdo a ser escrito no arquivo.
    """
    caminho_completo = os.path.join(diretorio, nome_arquivo)
    
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso em '{caminho_completo}'.")
    except IOError as e:
        print(f"Erro ao salvar o arquivo '{nome_arquivo}': {e}")

def criar_arquivo_bat(caminho, text:str):
    with open(caminho, encoding='UTF-8', mode='w') as arq:
        arq.write(text)

    print(f'Arquivo bat criado com exito')

def execute_bat(uri):
    resultado = subprocess.run(uri, capture_output=True, text=True, shell=True)

    print("Saída do arquivo .bat:")
    print(resultado.stdout)  # Exibe a saída padrão
    
# criar_arquivo_bat(BAT_TEXT_INICIAL)
# execute_bat()