import inspect, os

class UsuarioError(Exception):
  def __init__(self, mensagem=None):
    if mensagem is None:
      mensagem="Houve um problema ao tentar utilizar algumdado fornecido pelo usuário."
    self.mensagem = mensagem
    super().__init__(self.mensagem)

  def __str__(self):
    return f"{self.mensagem}"
class SistemaError(Exception):
  def __init__(self, mensagem=None):
    if mensagem is None:
      mensagem="Houve um problema genérico no sistema backend."
      
    frame = inspect.stack()[1]
    caminho = os.path.abspath(frame.filename)
    linha = frame.lineno
    funcao = frame.function
    
    self.mensagem = mensagem
    self.caminho = caminho
    self.linha = linha
    self.funcao = funcao
    
    super().__init__(self.__str__())

  def __str__(self):
    return (
      f"{self.mensagem}\n"
      f"→ Local: {self.caminho}:{self.linha} (função '{self.funcao}')"
    )
class AmbienteError(SistemaError):
  def __init__(self, mensagem=None):
    if mensagem is None:
      mensagem="Houve um problema genérico na preparação do ambiente de execução."
    super().__init__(mensagem)
class IAError(SistemaError):
  def __init__(self, mensagem=None):
    if mensagem is None:
      mensagem="Houve um problema genérico com alguma funcionalidade de IA."
    super().__init__(mensagem)
class JsonError(SistemaError):
  def __init__(self, mensagem=None):
    if mensagem is None:
      mensagem="Houve um problema genérico com algum Objeto JSON."
    super().__init__(mensagem)
class RequisicaoError(IAError):
  def __init__(self, mensagem=None):
    super().__init__(mensagem)
  