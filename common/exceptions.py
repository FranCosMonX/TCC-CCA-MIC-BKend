class UsuarioError(Exception):
  def __init__(self, mensagem):
    super().__init__(mensagem)
    self.mensagem = mensagem

  def __str__(self):
    return f"{self.mensagem}"
  
class SistemaError(Exception):
  def __init__(self, mensagem):
    super().__init__(mensagem)
    self.mensagem = mensagem

  def __str__(self):
    return f"{self.mensagem}"
