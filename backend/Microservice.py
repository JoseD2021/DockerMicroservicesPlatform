import os
import uuid

class MicroserviceManager:
    BASE_DIR = "/tmp/microservices"

    def __init__(self, client):
        self.client = client
        self.microservices = []
        
    def add_microservice(self, name, desc, lang, code):
        newMs = Microservice(name, desc, lang, code)
        newMs.create(self.client)
        
        self.microservices.append(newMs)
        
    def get_microservices(self):
        return self.microservices
    
    def delete(self, ms_id): 
        try:
            container = self.client.containers.get(ms_id)
            container.stop()
            container.remove()
        except Exception as e:
            print(f"Error interno en delete: {e}")
    

class Microservice:
    def __init__(self, name, description, language, code):
        self.name = name.replace(" ", "_")
        self.description = description
        self.language = language
        self.code = code
        self.project_id = str(uuid.uuid4())
        self.image_tag = f"ms_{self.name.lower()}_{self.project_id[:6]}"

    def create(self, client):
        self.image(client)
        self.deploy_container(client)
        
        return
    
    def image(self, client):
        # 1. Crear carpeta única
        path = os.path.join(MicroserviceManager.BASE_DIR, self.project_id)
        os.makedirs(path, exist_ok=True)
        self.project_path = path

        # 2. Crear archivos según lenguaje
        if self.language == "py":
            self._setup_python(path)
        else:
            raise ValueError("Lenguaje no soportado")
            
        """ if self.language == "js": mover arriba cuando se implemente
            self._setup_js(path) """
        
        # 3. Build de imagen
        image, logs = client.images.build(
            path=path,
            tag=self.image_tag,
            rm=True
        )

        return image.id
    
    def _setup_python(self, path):
        if(not self.code_validations()):
            raise ValueError("Código no válido")
        # main.py
        with open(os.path.join(path, "main.py"), "w") as f:
            f.write(f"""from flask import Flask
app = Flask(__name__)

@app.route("/{self.name}")
{self.code}

app.run(host="0.0.0.0", port=8000)
""")

        # requirements.txt
        with open(os.path.join(path, "requirements.txt"), "w") as f:
            f.write("flask\n")

        # Dockerfile
        dockerfile = """\
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["python", "main.py"]
"""
        with open(os.path.join(path, "Dockerfile"), "w") as f:
            f.write(dockerfile)
    
    # TODO: Implementar setup para JS
    def _setup_js(self, path):
        pass
    
    def deploy_container(self, client):
        nombre_contenedor = self.image_tag
        
        container = client.containers.run(
            self.image_tag,
            name=nombre_contenedor,
            detach=True,
            network="dockermicroservicesplatform_plataforma-net",

            # Traefik
            labels={
                "traefik.enable": "true",
                f"traefik.http.routers.{self.name}.rule": f"PathPrefix(`/{self.name}`)",
                f"traefik.http.routers.{self.name}.priority": "100",
                f"traefik.http.services.{self.name}.loadbalancer.server.port": "8000",
                "name": self.name,
                "description": self.description,
                "language": self.language,
                "code": self.code
            },

            mem_limit="128m",
            nano_cpus=500000000,
        )
        
        print("Creando contenedor:", nombre_contenedor)
        
        return {
            "container_id": container.id,
            "url": f"/{self.name}"
        }
    
    
    def code_validations(self):
        if not self.code.strip():
            return False
                
        return True