import http.server
import http.client
import socketserver
import json

# -- Puerto donde lanzar el servidor
PORT = 8000
INDEX_FILE = "index.html"
socketserver.TCPServer.allow_reuse_address = True

# -- Parametros de configuracion
REST_SERVER_NAME = "api.fda.gov"  # -- Nombre del servidor REST
REST_RESOURCE_NAME = "/drug/label.json"
headers = {'User-Agent': 'http-client'}


# Clase con nuestro manejador. Es una clase derivada de BaseHTTPRequestHandler
# Esto significa que "hereda" todos los metodos de esta clase. Y los que
# nosotros consideremos los podemos reemplazar por los nuestros
class TestHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # GET. Este metodo se invoca automaticamente cada vez que hay una
    # peticion GET por HTTP. El recurso que nos solicitan se encuentra
    # en self.path
    def do_GET(self):

        print("Recurso pedido: {}".format(self.path))

        message = ""  # type: str

        if self.path == "/":
            print("PAGINA INDICE")
            with open(INDEX_FILE, "r") as f:
                message = f.read()
        elif self.path == "/ListDrugs":
            print("Listado de farmacos solicitado: ListDrugs!")

            # Lanar la peticion a openFDA
            # Establecer la conexion con el servidor
            conn = http.client.HTTPSConnection(REST_SERVER_NAME)

            # Enviar un mensaje de solicitud
            conn.request("GET", REST_RESOURCE_NAME, None, headers)

            # Obtener la respuesta del servidor
            r1 = conn.getresponse()

            # r1.status == 404:
            #   print("ERROR. Recurso {} no encontrado".format(REST_RESOURCE_NAME))
            #   exit(1)

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

            # Por ejemplo, podemos saber el numero de objetos totales en la base de datos y los devueltos
            # en esta busqueda
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
            id = drugs['id']

            # Proposito: drugs.purpose[0]
            proposito = drugs['purpose'][0]

            print("")
            print("Nombre: {}".format(nombre))
            print("Marca: {}".format(marca))
            print("Fabricante: {}".format(fabricante))
            print("Id: {}".format(id))
            print("Proposito: {}".format(proposito))

            message = (' <!DOCTYPE html>\n'
                       '<html lang="es">\n'
                       '<head>\n'
                       '    <meta charset="UTF-8">\n'
                       '</head>\n'
                       '<body>\n'
                       '\n'
                       '<ul>\n')

            message += "<li>{}</li>\n".format(nombre)

            message += ('</ul>\n'
                        '\n'
                        '<a href="/">Home</a>'
                        '</body>\n'
                        '</html>')

        # La primera linea del mensaje de respuesta es el
        # status. Indicamos que OK
        self.send_response(200)

        # En las siguientes lineas de la respuesta colocamos las
        # cabeceras necesarias para que el cliente entienda el
        # contenido que le enviamos (que sera HTML)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Enviar el mensaaje completo
        self.wfile.write(bytes(message, "utf8"))
        return


# ----------------------------------
# El servidor comienza a aqui
# ----------------------------------
# Establecemos como manejador nuestra propia clase
Handler = TestHTTPRequestHandler

# -- Configurar el socket del servidor, para esperar conexiones de clientes
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

# Entrar en el bucle principal
# Las peticiones se atienden desde nuestro manejador
# Cada vez que se ocurra un "GET" se invoca al metodo do_GET de
# nuestro manejador
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("Interrumpido por el usuario")

print("")
print("Servidor parado")
