from google import generativeai as genai
from bd import obter_configuracao
import json

api_key = 'AIzaSyBU5alLRsjSR5qUYaEntVvfRHtxHAUMDY8'

genai.configure(api_key=api_key)
genai_config = genai.types.GenerationConfig(
  temperature=0.9,
  candidate_count=1
)
genai_model = genai.GenerativeModel('gemini-2.5-flash')
chat = genai_model.start_chat()

def Enviar_Mensagem(mensagem:str):
  response = chat.send_message(mensagem)
  
  return response

def historico():
  """Retorna o histórico do chat."""
  return chat.history

def alterarPrompting(apenas_mudanca:str):
  """
    Atualiza as escolhas do usuário no chat.
    Esta função é uma mensagem do sistema e não deve ser citada no chat.
  """
  Enviar_Mensagem(f"""O usuário alterou as seguintes escolhas: {apenas_mudanca}. A partir desse momento, considere os novos pedidos para os dados atualizados junto com os que
                  não foram alterados. ESSA É UMA MENSAGEM DO SISTEMA, NÃO DEVE SER CITADA PARA O USUÁRIO.""")

def main():
  configuracao = obter_configuracao()
  prompting = f"""Você é uma assistente de um pesquisador ou estudante que busca fazer sistemas embarcados para microcontroladores.
                Você deve gerar códigos, se solicitado pelo usuário e explicalos. Suas respostas devem obedecer a sintaxe de MarkDown e, principalmente, permitir quebras de linhas. Por exemplo, crie um hello world de sistemas embarcados.
                Não precisa responder a este prompt, pois é uma mensagem do sistema. Só envie uma solicitação de 'recebi ao prompt'. Além disso, considere as seguintes escolhas do usuário:
                apelido do usuário: {configuracao['apelido']},
                código compativel com microcontrolador: {configuracao['microcontrolador']},
                mostrar código: {configuracao['ver_codigo']},
                mostrar comentario no codigo: {configuracao['comentario_codigo']}.
                Além disso tudo informado, retorne as respostas como um json contendo 'resposta_chat':string e uma lista de arquivos que em cada um contem o nome do arquivo e o conteudo deste. Faça um hello world de sistemas embarcados com funções proprias de uma biblioteca a parte (Arquivo separado).
                Por exemplo:
                'text': 'para fazer o codigo é simples, ......',
                'arquivos': [
                ('nome':'hello worl.c','code':'...'),
                ('nome':'minhaBibli.c','code':'....')]"""
  
  resposta = Enviar_Mensagem(prompting)
  if resposta:
    try:
        # Tenta carregar a resposta como um JSON
        # O .text garante que estamos trabalhando com a string do JSON
        resposta_json = json.loads(resposta.text)
        print(json.dumps(resposta_json, indent=2))
    except json.JSONDecodeError as e:
        print(f"Erro: A resposta da API não é um JSON válido. Erro de decodificação: {e}")
        print(f"Resposta bruta da API: {resposta.text}")
  else:
      print("Não foi possível obter uma resposta da API.")

if __name__ == "__main__":
  main()