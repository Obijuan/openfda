# Ejemplo para obtener el id de un medicamento de openfda
# La API REST que vamos a usar es esta: https://api.fda.gov/drug/label.json

import http.client
import json

# -- Parametros de configuracion
REST_SERVER_NAME = "api.fda.gov"  # -- Nombre del servidor REST
REST_RESOURCE_NAME = "/drug/label.json"
headers = {'User-Agent': 'http-client'}
DEBUG = True

# Establecer la conexion con el servidor
conn = http.client.HTTPSConnection(REST_SERVER_NAME)

# Enviar un mensaje de solicitud
try:
    conn.request("GET", REST_RESOURCE_NAME, None, headers)
except:
    print("Error al solicitar recurso: {}{}".format(REST_SERVER_NAME, REST_RESOURCE_NAME))
    exit(1)

print("* Mensaje de solicitud enviado")

# Obtener la respuesta del servidor
r1 = conn.getresponse()

if r1.status == 404:
    print("ERROR. Recurso {} no encontrado".format(REST_RESOURCE_NAME))
    exit(1)

print("  * {} {}".format(r1.status, r1.reason))

# Leer el contenido en json, y transformarlo en una cadena
drugs_json = r1.read().decode("utf-8")
conn.close()


# ---- Procesar el contenido JSON
drugs = json.loads(drugs_json)

# -- Ahora drugs es un diccionario que contiene la respuesta recibida
# -- Necesitamos conocer su estructura para procesarlo correctamente

# Campo META, que contiene informacion sobre la busqueda
meta = drugs['meta']

# Por ejemplo, podemos saber el numero de objetos totales en la base de datos y los devueltos en esta busqueda
# Objetos totales: meta.results.total
# Objetos recibidos: meta.results.limit

total = meta['results']['total']
limit = meta['results']['limit']

print("* Objetos recibidos: {} / {}".format(limit, total))

# Campo RESULTS: contiene los resultados de la busqueda
# drugs.results[0]
drugs = drugs['results'][0]

# Nombre del componente principal: drugs.openfda.substance_name[0]
nombre = drugs['openfda']['substance_name'][0]

# Marca: drugs.openfda.brand_name[0]
marca = drugs['openfda']['brand_name'][0]

# Nombre del fabricante: drugs.openfda.manufacturer_name[0]
fabricante = drugs['openfda']['manufacturer_name'][0]

# Identificador: drugs.id
id = drugs['id'];

# Proposito: drugs.purpose[0]
proposito = drugs['purpose'][0]

print("")
print("Nombre: {}".format(nombre))
print("Marca: {}".format(marca))
print("Fabricante: {}".format(fabricante))
print("Id: {}".format(id))
print("Proposito: {}".format(proposito))

# -- Obtener 10 medicamentos
conn.request("GET", REST_RESOURCE_NAME + '?limit=10', None, headers)

# Obtener la respuesta del servidor
print ("")
print("* Consulta de 10 medicamentos")
r2 = conn.getresponse()

if r2.status == 404:
    print("ERROR. Recurso {} no encontrado".format(REST_RESOURCE_NAME))
    exit(1)

print("  * {} {}".format(r2.status, r2.reason))

# Leer el contenido en json, y transformarlo en una cadena
drugs_json = r2.read().decode("utf-8")

conn.close()

# ---- Procesar el contenido JSON
drugs = json.loads(drugs_json)
drugs = drugs['results']

for drug in drugs:
    print("* {}".format(drug['id']))


