import os
from os import path
import re
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
    
    def disable(self, ms_id):
        try:
            container = self.client.containers.get(ms_id)
            container.stop()
        except Exception as e:
            print(f"Error interno en disable: {e}")


    def enable(self, ms_id):
        try:
            container = self.client.containers.get(ms_id)
            container.start()
        except Exception as e:
            print(f"Error interno en enable: {e}")
    

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
        elif self.language == "js":
            self._setup_js(path)
        else:
            raise ValueError("Lenguaje no soportado")
            
        
        # 3. Build de imagen
        image, logs = client.images.build(
            path=path,
            tag=self.image_tag,
            rm=True
        )

        return image.id
    
    def _setup_python(self, path):
        if not self.code_validations():
            raise ValueError("Código no válido")

        # Detección del nombre de la función de usuario (soporta def function() y lambda)
        func_match = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", self.code)
        func_name = func_match.group(1) if func_match else None

        # main.py
        with open(os.path.join(path, "main.py"), "w") as f:
            f.write(f"""from flask import Flask, request, jsonify
app = Flask(__name__)

{self.code}

@app.route("/{self.name}")
def handler():
    try:
        params = request.args.to_dict()
        if {str(func_name is not None)}:
            target = globals().get('{func_name}')
            if target is None or not callable(target):
                raise ValueError('Función no encontrada: {func_name}')
            result = target(**params)
        else:
            # Si no hay función, se espera que el código user declare `result`
            local_vars = {{}}
            exec(compile({repr(self.code)}, '<string>', 'exec'), globals(), local_vars)
            if 'result' not in local_vars:
                raise ValueError('No se declaró `result`')
            result = local_vars['result']
        return jsonify(result)
    except Exception as e:
        return jsonify({{"error": "Error ejecutando código", "detail": str(e)}}), 500

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
    

    def _setup_js(self, path):
        if not self.code_validations():
            raise ValueError("Código no válido")

        # Detección del nombre de la función de usuario (soporta function declaration y arrow function)
        func_match = re.search(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(|const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\(|let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\(", self.code)
        func_name = next((name for name in func_match.groups() if name), None) if func_match else None

        # main.js
        with open(os.path.join(path, "main.js"), "w") as f:
            f.write(f"""const express = require('express');
const app = express();

{self.code}

app.get('/{self.name}', async (req, res) => {{
    try {{
        const params = req.query;
        let result;
        if ({'true' if func_name else 'false'}) {{
            const runner = eval('{func_name}');
            if (typeof runner !== 'function') throw new Error('Función no encontrada: {func_name}');
            result = runner(...Object.values(params));
        }} else {{
            if (typeof result === 'undefined') throw new Error('No se definió result ni función en el código');
        }}
        res.json(result);
    }} catch (error) {{
        res.status(500).json({{ error: 'Error ejecutando código', detail: error.toString() }});
    }}
}});

app.listen(8000, () => {{
    console.log('🚀 Microservicio {self.name} corriendo en puerto 8000');
}});
""")

        # package.json
        with open(os.path.join(path, "package.json"), "w") as f:
            f.write("""{
  "name": "microservice",
  "version": "1.0.0",
  "main": "main.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
""")

        # Dockerfile
        dockerfile = """\
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 8000
CMD ["node", "main.js"]
"""
        with open(os.path.join(path, "Dockerfile"), "w") as f:
            f.write(dockerfile)
    
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