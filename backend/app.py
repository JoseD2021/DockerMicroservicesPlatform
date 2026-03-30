"""
Backend coordinador de microservicios dinamicos:
Funcionalidades:
 - Crear microservicios a partir de código (Python/JS)
 - Construir imágenes Docker automáticamente
 - Desplegar contenedores en una red compartida
 - Exponerlos mediante Traefik usando routing por path
 - listar, eliminar, habilitar/deshabilitar contenedores
"""
from Microservice import MicroserviceManager
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import docker

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost"}})

#Inicializamos Docker y el gestor de microservicios
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
    
    # Obtiene todos los contenedores en la red de la plataforma
    containers = client.containers.list(filters={"network": "plataforma-net"}, all=True)
    # Filtramos solo los contenedores que pertenecen a microservicios
    # los nombres de los contenedor empiezan por "ms_"
    containers = [
        c for c in containers
        if any(name.startswith("ms_") for name in c.name.split())
    ]
    
    #Se construye la respuesta usando los labels como de informacion para cada contenedor
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
    
    return jsonify(lista)

@app.route('/servicios/nuevo', methods=['POST'])
def crear_servicio():
    if client is None:
        return jsonify({"error": "No se pudo establecer un cliente Docker"}), 500
    
    #Extraemos datos del request JSON
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    lang = data.get('lang')
    code = data.get('code')
    
    if(not name or not description or not lang or not code):
        return jsonify({"error": "Faltan parámetros requeridos"}), 400    
    
    try:
        #El gestor se encarga de la creacion del microservicio
        #Incluye build de la imagen y despliegue del contenedor
        manager.add_microservice(name, description, lang, code)
        return jsonify({"mensaje": "Microservicio creado exitosamente", **data})
    
    #Error cuando el nombre esta duplicado
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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
        #Se detiene el contenedor sin eliminarlo, esto permite reactivarlo 
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