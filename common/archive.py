import os, subprocess

BAT_TEXT_INICIAL = """@echo off
echo Verificando existencia da arduino-cli
echo.
arduino-cli --version
IF %ERRORLEVEL% NEQ 0 (
    echo Arduino CLI nao instalado. Será instalado em breve em 5 segundos
    timout 5 /nobreak
    echo.
    winget install "Arduino CLI"
    echo Arduino CLI instalado com êxito.
    exit
) ELSE {
    echo Arduino CLI já está instalado
    timout 10
}
arduino-cli --version
timout 5
"""

def criar_diretorios():
    """Cria os diretórios 'temporario' e 'executavel' se eles não existirem."""
    uri = r"C:\Users\franc\Documents"
    diretorio_executavel = os.path.join(uri, 'executavel')

    if not os.path.exists(diretorio_executavel):
        os.makedirs(diretorio_executavel)
        print(f"Diretório '{diretorio_executavel}' criado com sucesso.")

def salvar_arquivo(nome_arquivo: str, conteudo: str):
    """
    Salva o conteúdo em um arquivo no diretório 'temporario'.
    O arquivo é sobrescrito se já existir.

    Args:
        nome_arquivo (str): O nome do arquivo a ser salvo (ex: `'meu_codigo.c'`).
        conteudo (str): O conteúdo a ser escrito no arquivo.
    """
    diretorio_executavel = 'executavel'
    caminho_completo = os.path.join(diretorio_executavel, nome_arquivo)
    
    try:
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso em '{caminho_completo}'.")
    except IOError as e:
        print(f"Erro ao salvar o arquivo '{nome_arquivo}': {e}")

def criar_arquivo_bat(text: str):
    uri = r"C:\Users\franc\Documents\executavel.bat"

    with open(uri, encoding='UTF-8', mode='w') as arq:
        arq.write(text)

    print(f'Arquivo bat criado com exito')

def execute_bat():
    resultado = subprocess.run("C:/Users/franc/Documents/executavel.bat", capture_output=True, text=True, shell=True)

    print("Saída do arquivo .bat:")
    print(resultado.stdout)  # Exibe a saída padrão
    
criar_arquivo_bat(BAT_TEXT_INICIAL)
execute_bat()