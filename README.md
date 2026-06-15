# Sistema Backend - CCA Mic

Sistema principal da aplicação CCA Mic (Construtor de Códigos Automáticos para Microcontroladores), desenvolvido de forma independente de um frontend específico. Essa característica é importante porque permite que diferentes interfaces possam ser utilizadas para acessar o sistema, ampliando a flexibilidade e a acessibilidade da aplicação. Dessa forma, o usuário pode realizar pesquisas e desenvolver projetos mesmo sem depender exclusivamente de um computador convencional.

O sistema faz parte de um protótipo de Trabalho de Conclusão de Curso (TCC) e tem como objetivo intermediar a comunicação entre o usuário e uma Inteligência Artificial, além de automatizar o desenvolvimento de Sistemas Embarcados. Com isso, o usuário não precisa configurar manualmente todo o ambiente de desenvolvimento para produzir seus projetos, reduzindo a complexidade do processo. Além disso, a aplicação oferece maior isolamento durante a execução, garantindo que a Inteligência Artificial não tenha acesso direto aos arquivos pessoais da máquina do usuário.

Vale citar um tutorial alterativo em [francosmonx.github.io/#/projetos/tutorial_cca_mic](https://francosmonx.github.io/#/projetos/tutorial_cca_mic)

# Arquitetura da Aplicação

O backend foi desenvolvido utilizando o framework **Flask** e atua como responsável por:

- Receber requisições do frontend;
- Intermediar chamadas para APIs de Inteligência Artificial;
- Processar respostas geradas pela IA;
- Preparar automaticamente ambientes de desenvolvimento;
- Gerar arquivos de código e configuração;
- Executar processos de compilação;
- Gravar o proojeto em um microcontroladores especificado.

A separação entre frontend e backend permite que a aplicação seja utilizada em diferentes plataformas e interfaces sem comprometer a lógica principal do sistema.

## Segurança e Limitações

Por se tratar de um protótipo acadêmico, o sistema ainda não implementa mecanismos robustos de segurança para ambientes de produção.

Atualmente:

- Não há proteção avançada contra acessos indevidos;
- Não existem mecanismos completos de autenticação;
- O sistema não foi projetado para exposição pública na internet;
- O uso remoto deve ser realizado com cautela.
- Necessidade do Windows ter o `winget`, para instalar o arduino-cli automaticamente.
- Perda do projeto criado com o mesmo nome do gerado posteriormente.

Portanto, recomenda-se utilizar o sistema apenas em ambientes controlados para fins acadêmicos, testes e desenvolvimento.

# Ambiente de Desenvolvimento

O sistema foi desenvolvido utilizando:

- Python v3.14;
  > A aplicação funciona corretamente com python na versão 3.13 e 3.14.
- Flask;
- Ambiente virtual (`venv`);
- VSCode como IDE principal.

## Ambiente de Execução

O sistema foi desenvolvido utilizando o framework Flask em um ambiente virtual Python, com o VSCode como principal IDE. Entretanto, para preparar o ambiente de execução, basta utilizar o terminal do Windows e seguir os passos descritos abaixo:

- O terminal deve ser aberto na raiz do projeto onde se encontram todos os arquivos da aplicação, incluindo o arquivo `requirements.txt` que contém as dependências;

- Criando um ambiente virtual Python para rodas a aplicação:
  ```console
  python -m venv venv
  ```

- Ativar o ambiente virtual:
  ```console
  .\venv\Scripts\activate
  ```

  > Caso deseje encerrar o ambiente virtual após os testes, utilize o comando `deactivate` no mesmo terminal.

- Instalar as dependências do sistema:
  ```console
  pip install -r requirements.txt
  ```

- Executar o sistema:
  ```console
  flask run
  ```

  > Para interromper a execução do sistema, pressione `CTRL + C`.

---

## Funcionalidades

O sistema tem como objetivo abstrair operações complexas para usuários que não possuem domínio técnico avançado sobre desenvolvimento de Sistemas Embarcados. Entre suas principais responsabilidades, destacam-se:

1. Intermediar a comunicação entre o usuário e a Inteligência Artificial, embora não impeça o envio de informações pessoais por meio de linguagem natural;

2. Preparar automaticamente o ambiente de desenvolvimento necessário para a aplicação discutida entre o usuário e a IA;

3. Gerar arquivos de código-fonte e arquivos de configuração necessários para compilação e execução do projeto;

4. Realizar a gravação do código no microcontrolador, desde que não existam erros de compilação, utilizando conexão USB por meio de comunicação serial.

---

# Integração com o Frontend

O backend foi projetado para funcionar em conjunto com o frontend do CCA MIC, desenvolvido utilizando React e Vite. 
> Frontend: [https://github.com/FranCosMonX/TCC-CCA-MIC-ftend](https://github.com/FranCosMonX/TCC-CCA-MIC-ftend)

Enquanto o frontend fornece a interface de interação com o usuário, o backend é responsável por executar toda a lógica de processamento, comunicação com APIs externas e manipulação do ambiente de desenvolvimento.

Essa separação permite maior modularidade e facilita futuras expansões da aplicação.