from Microservice import MicroserviceManager
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import docker

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost"}})

try:
    client = docker.from_env()
    manager = MicroserviceManager(client)
except Exception as e:
    print(f"Error de conexión: {e}")
    client = None

@app.route('/')
def home():
    # return jsonify({"mensaje": "Backend Orquestador con Flask activo"})
    return redirect("http://localhost/") # 

@app.route('/servicios', methods=['GET'])
def listar_servicios():
    if client is None:
        return jsonify({"error": "No se pudo establecer un cliente Docker"}), 500
    
    containers = client.containers.list(filters={"network": "dockermicroservicesplatform_plataforma-net"}, all=True)
    containers = [
        c for c in containers
        if any(name.startswith("ms_") for name in c.name.split())
    ]
    
    
    lista = [{
            "id": c.id[:10],
            "nombre": c.name,
            "estado": c.status,
            "ms": {
                "name": c.labels.get("name", ""),
                "description": c.labels.get("description", ""),
                "language": c.labels.get("language", ""),
                "code": c.labels.get("code", "")
            }
        } for c in containers]
    # print(lista)
    return jsonify(lista)

@app.route('/servicios/nuevo', methods=['POST'])
def crear_servicio():
    if client is None:
        return jsonify({"error": "No se pudo establecer un cliente Docker"}), 500
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    lang = data.get('lang')
    code = data.get('code')
    
    if(not name or not description or not lang or not code):
        return jsonify({"error": "Faltan parámetros requeridos"}), 400    
    
    manager.add_microservice(name, description, lang, code)
    
    return jsonify({"mensaje": "Microservicio creado exitosamente", **data})

@app.route('/deletems/<ms_id>', methods=['DELETE'])
def deletems(ms_id):
    try:
        manager.delete(ms_id)
        return jsonify({"status": "success", "mensaje": f"Microservicio {ms_id} eliminado."})
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500
    
@app.route('/disablems/<ms_id>', methods=['POST'])
def disable_ms(ms_id):
    try:
        manager.disable(ms_id)
        return jsonify({"status": "success", "mensaje": f"Microservicio {ms_id} deshabilitado."})
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500


@app.route('/enablems/<ms_id>', methods=['POST'])
def enable_ms(ms_id):
    try:
        manager.enable(ms_id)
        return jsonify({"status": "success", "mensaje": f"Microservicio {ms_id} habilitado."})
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"status": "error", "mensaje": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)