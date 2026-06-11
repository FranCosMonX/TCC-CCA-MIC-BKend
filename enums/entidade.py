from enum import StrEnum

class Entidade(StrEnum):
  USUARIO = 'usuario'
  SISTEMA = 'sistema'
  ASSISTENTE_DO_SISTEMA = 'assistente_do_sistema'
  IA = 'ia'
  IA_MODEL_CREATE_JSON = 'ia_model_create_json'

  def __str__(self):
    return self.value