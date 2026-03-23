from flask import Flask, jsonify
from flask_cors import CORS
import docker

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost", "http://api.localhost"]}})

try:
    client = docker.from_env()
except Exception as e:
    print(f"Error de conexión: {e}")
    client = None

@app.route('/')
def home():
    return jsonify({"mensaje": "Backend Orquestador con Flask activo"})

@app.route('/servicios', methods=['GET'])
def listar_servicios():
    if client is None:
        return jsonify({"error": "No se pudo establecer un cliente Docker"}), 500
    
    containers = client.containers.list()
    lista = [{"id": c.id[:10], "nombre": c.name, "estado": c.status} for c in containers]
    return jsonify(lista)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)