# Para realizar la consulta, buscamos en el campo active_ingredient el nombre del principio activo de la aspirina
# La busqueda a realizar es: https://api.fda.gov/drug/label.json?search=active_ingredient:"acetylsalicylic"&limit=10

import http.client
import json

REST_SERVER = "api.fda.gov"
REST_RESOURCE = "/drug/label.json"
LIMIT = 100
QUERY = "/?search=active_ingredient:acetylsalicylic&limit={}".format(LIMIT)

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection(REST_SERVER)
conn.request("GET", REST_RESOURCE + QUERY, None, headers)

r1 = conn.getresponse()

if r1.status == 404:
    print("ERROR. Recurso {} no encontrado".format(REST_RESOURCE_NAME))
    exit(1)

print("  * {} {}".format(r1.status, r1.reason))

drugs_raw = r1.read().decode("utf-8")
conn.close()

aspirins = json.loads(drugs_raw)['results']

for aspirin in aspirins:
    print("* ID: {}".format(aspirin['id']))
    if aspirin['openfda']:
        manufacturer = aspirin['openfda']['manufacturer_name'][0]
        print("  * Fabricante: {}".format(manufacturer))
    else:
        print("  *Fabricante no disponible")
