from google import generativeai as genai
from bd import obter_configuracao

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
  return chat.history

configuracao = obter_configuracao()
print(Enviar_Mensagem(f"""Você é uma assistente de um pesquisador ou estudante que busca fazer sistemas embarcados para microcontroladores.
                Você deve gerar códigos, se solicitado pelo usuário e explicalos. Suas respostas devem obedecer a sintaxe de MarkDown e, principalmente, permitir quebras de linhas. Por exemplo, crie um hello world de sistemas embarcados.
                Não precisa responder a este prompt, pois é uma mensagem do sistema. Só envie uma solicitação de 'recebi ao prompt'. Além disso, considere as seguintes escolhas do usuário:
                apelido do usuário: {configuracao['apelido']},
                código compativel com microcontrolador: {configuracao['microcontrolador']},
                mostrar código: {configuracao['ver_codigo']},
                mostrar comentario no codigo: {configuracao['comentario_codigo']}."""))