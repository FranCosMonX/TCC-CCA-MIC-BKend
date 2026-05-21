from flask import Flask

from .configuracao import configuracao_bp
from .chat import chat_bp
from .ia import ia_bp
from .microcontrolador import microcontrolador_bp
from .usuario import usuario_bp

def registrar_blueprints(app:Flask):
  """Função para registrar todos os BluePrints da aplicação"""
  app.register_blueprint(configuracao_bp, url_prefix="/api")
  app.register_blueprint(chat_bp, url_prefix="/api")
  app.register_blueprint(ia_bp, url_prefix="/api")
  app.register_blueprint(microcontrolador_bp, url_prefix="/api")
  app.register_blueprint(usuario_bp, url_prefix="/api")