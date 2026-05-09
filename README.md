# Sistema Backend - CCA Mic

Sistema principal da aplicação CCA Mic (Construtor de Códigos Automáticos para Microcontroladores), desenvolvido de forma independente de um frontend específico. Essa característica é importante porque permite que diferentes interfaces possam ser utilizadas para acessar o sistema, ampliando a flexibilidade e a acessibilidade da aplicação. Dessa forma, o usuário pode realizar pesquisas e desenvolver projetos mesmo sem depender exclusivamente de um computador convencional.

O sistema faz parte de um protótipo de Trabalho de Conclusão de Curso (TCC) e tem como objetivo intermediar a comunicação entre o usuário e uma Inteligência Artificial, além de automatizar o desenvolvimento de Sistemas Embarcados. Com isso, o usuário não precisa configurar manualmente todo o ambiente de desenvolvimento para produzir seus projetos, reduzindo a complexidade do processo. Além disso, a aplicação oferece maior isolamento durante a execução, garantindo que a Inteligência Artificial não tenha acesso direto aos arquivos pessoais da máquina do usuário.

Por se tratar de um protótipo acadêmico, o sistema ainda não implementa mecanismos robustos de segurança para proteção contra acessos indevidos ou ataques de terceiros, principalmente quando configurado para acesso remoto ou disponibilizado online.

---

## Ambiente de Execução

O sistema foi desenvolvido utilizando o framework Flask em um ambiente virtual Python, com o VSCode como principal IDE. Entretanto, para preparar o ambiente de execução, basta utilizar o terminal do Windows e seguir os passos descritos abaixo:

- Estar no diretório onde se encontram todos os arquivos do projeto, incluindo o arquivo `requirements.txt`;

- Criar um ambiente virtual Python:
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