from flask import Flask
from flask_cors import CORS
from routes import registrar_blueprints

app = Flask(__name__)
registrar_blueprints(app)
CORS(app#,
    #  resources={
    #   r"/*": {"origins": "http://localhost:5173"},
    # }
  )


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)