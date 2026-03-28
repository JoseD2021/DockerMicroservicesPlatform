# Descripción
Descripción de proyecto.

## Ejemplos
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
