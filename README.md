# Descripción
Plataforma de Microservicios basada en `Traefik v3.6.11`, `Nginx Alpine` y `Python v3.12`.

La dashboard cueta con la capacidad de:
* Crear microservicios con dos lenguajes de programación: `javascript` usando NodeJS + Express y `python` usando Flask.
* Listar microservicios creados, que estén presentes en el host.
* Deshabilitar, habilitar, o eliminar microservicios a conveniencia con botones.

Inicie la plataforma clonando el repositorio y ejecutando docker compose:
```
docker compose up -d
```

## Ejemplos
Los siguientes ejemplos pueden ser copiados y usados en el campo de **código fuente** en la creación de microservicios.
### Python
```python
def suma(a=0, b=0):
    a = int(a)
    b = int(b)
    res = a + b

    return {"result": res, "text": f"La suma de {a} + {b} es: {res}"}
```
Endpoint ejemplo: `http://localhost/sumar?a=15&b=15`

### Javascript
```javascript
function saludo(nombre) {
	if(!nombre) return {"text": "Nombre no definido"}
	return {"text": `Hola, ${nombre}`}
}
```
Endpoint ejemplo: `http://localhost/saludo?nombre=Carlos`

# Arquitectura
Diagrama de arquitectura
# Video
Link de video
