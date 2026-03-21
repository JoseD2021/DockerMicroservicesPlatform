from flask import Flask, jsonify, request
import docker

app = Flask(__name__)


try:
    client = docker.from_env()
except Exception as e:
    print(f"Error de conexión: {e}")

@app.route('/')
def home():
    return jsonify({"mensaje": "Backend Orquestador con Flask activo"})

@app.route('/servicios', methods=['GET'])
def listar_servicios():
    containers = client.containers.list(all=True)
    lista = [{"id": c.id[:10], "nombre": c.name, "estado": c.status} for c in containers]
    return jsonify(lista)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)