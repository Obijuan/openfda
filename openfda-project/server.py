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

    def openfda_req(self, limit=1, search_str=""):
        """Realizar una peticion a openFPGA"""

        # Crear la cadena con la peticion
        req_str = "{}?limit={}".format(REST_RESOURCE_NAME, limit)

        # Si hay que hacer busqueda, añadirla a la cadena de peticion
        if search_str != "":
            req_str += "&{}".format(search_str)

        print("Recurso solicitado: {}".format(req_str))

        conn = http.client.HTTPSConnection(REST_SERVER_NAME)

        # Enviar un mensaje de solicitud
        conn.request("GET", req_str, None, headers)

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
        return json.loads(drugs_json)

    def req_index(self):
        """Devolver el mensaje con la página indice"""

        with open(INDEX_FILE, "r") as f:
            index_html = f.read()

        return index_html

    def req_listdrugs(self, limit):
        """Devolver el mensaje con la peticion del listado de fármacos"""
        # Lanzar la peticion a openFDA
        # Establecer la conexion con el servidor
        drugs = self.openfda_req(limit)

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

        message = (' <!DOCTYPE html>\n'
                   '<html lang="es">\n'
                   '<head>\n'
                   '    <meta charset="UTF-8">\n'
                   '</head>\n'
                   '<body>\n'
                   '<p>Nombre. Marca. Fabricante. ID. Propósito</p>'
                   '\n'
                   '<ul>\n')

        # Campo RESULTS: contiene los resultados de la busqueda
        # drugs.results[0]
        for drug in drugs['results']:

            # Nombre del componente principal: drugs.openfda.substance_name[0]
            if drug['openfda']:
                nombre = drug['openfda']['substance_name'][0]

                # Marca: drugs.openfda.brand_name[0]
                marca = drug['openfda']['brand_name'][0]

                # Nombre del fabricante: drugs.openfda.manufacturer_name[0]
                fabricante = drug['openfda']['manufacturer_name'][0]
            else:
                nombre = "Desconocido"
                marca = "Desconocido"
                fabricante = "Desconocido"

            # Identificador: drugs.id
            id = drug['id']

            # Proposito: drugs.purpose[0]
            try:
                proposito = drug['purpose'][0]
            except KeyError:
                proposito = "Desconocido"

            message += "<li>{}. {}. {}. {}. {}</li>\n".format(nombre, marca, fabricante, id, proposito)

        # Parte final del html
        message += ('</ul>\n'
                    '\n'
                    '<a href="/">Home</a>'
                    '</body>\n'
                    '</html>')

        return message

    def req_listcompanies(self, limit):

        # Lanzar la peticion a openFDA
        # Establecer la conexion con el servidor
        drugs = self.openfda_req(limit)

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

        message = (' <!DOCTYPE html>\n'
                   '<html lang="es">\n'
                   '<head>\n'
                   '    <meta charset="UTF-8">\n'
                   '</head>\n'
                   '<body>\n'
                   '<p>Fabricantes</p>'
                   '\n'
                   '<ul>\n')

        # Campo RESULTS: contiene los resultados de la busqueda
        # drugs.results[0]
        for drug in drugs['results']:

            # Nombre del componente principal: drugs.openfda.substance_name[0]
            if drug['openfda']:

                try:
                    message += "<li>{}</li>".format(drug['openfda']['manufacturer_name'][0])
                except KeyError:
                    pass

        # Parte final del html
        message += ('</ul>\n'
                    '\n'
                    '<a href="/">Home</a>'
                    '</body>\n'
                    '</html>')

        print("Aqui llega...")
        return message

    # GET. Este metodo se invoca automaticamente cada vez que hay una
    # peticion GET por HTTP. El recurso que nos solicitan se encuentra
    # en self.path
    def do_GET(self):

        print("Recurso pedido: {}".format(self.path))

        message = ""  # type: str

        # Dividir entre el endpoint y los parametros
        recurso_list = self.path.split("?")
        endpoint = recurso_list[0]
        if len(recurso_list) > 1:
            params = recurso_list[1]
        else:
            params = ""

        print("Endpoint: {}, params: {}".format(endpoint, params))

        # -- Valores por defecto de los parametros
        limit = 1

        # Obtener los parametros
        if params:
            print("Hay parametros")
            parse_limit = params.split("=")
            if parse_limit[0] == "limit":
                limit = int(parse_limit[1])
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")



        # -- Pagina INDICE
        if endpoint == "/":

            message = self.req_index()

        # -- Listado de farmacos
        elif endpoint == "/listDrugs":

            print("Listado de farmacos solicitado: ListDrugs!")
            message = self.req_listdrugs(limit)

        elif endpoint == "/ListCompanies":

            print("Listado de empresas")
            message = self.req_listcompanies(limit=10)

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
