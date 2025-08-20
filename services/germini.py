from google import genai

api_key = 'AIzaSyBU5alLRsjSR5qUYaEntVvfRHtxHAUMDY8'

cliente = genai.Client(api_key=api_key)

def test():
  response = cliente.models.generate_content(
    model='gemini-2.5-flash',
    contents="Fale que isso é um teste de conexão"
  )

  print(response.text)

test()