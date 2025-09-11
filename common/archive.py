import os

def criar_diretorios():
    """Cria os diretórios 'temporario' e 'executavel' se eles não existirem."""
    uri = r"C:\Users\franc\Documents"
    diretorio_temporario = os.path.join(uri, 'temporario')
    diretorio_executavel = os.path.join(uri, 'executavel')

    if not os.path.exists(diretorio_temporario):
        os.makedirs(diretorio_temporario)
        print(f"Diretório '{diretorio_temporario}' criado com sucesso.")

    if not os.path.exists(diretorio_executavel):
        os.makedirs(diretorio_executavel)
        print(f"Diretório '{diretorio_executavel}' criado com sucesso.")

def salvar_arquivo_temporario(nome_arquivo: str, conteudo: str):
    """
    Salva o conteúdo em um arquivo no diretório 'temporario'.
    O arquivo é sobrescrito se já existir.

    Args:
        nome_arquivo (str): O nome do arquivo a ser salvo (ex: 'meu_codigo.c').
        conteudo (str): O conteúdo a ser escrito no arquivo.
    """
    diretorio_temporario = 'temporario'
    caminho_completo = os.path.join(diretorio_temporario, nome_arquivo)
    
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso em '{caminho_completo}'.")
    except IOError as e:
        print(f"Erro ao salvar o arquivo '{nome_arquivo}': {e}")