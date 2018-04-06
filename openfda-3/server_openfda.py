import http.server
import socketserver

socketserver.TCPServer.allow_reuse_address = True

# --- Puerto donde lanzar el servidor
PORT = 8000

HTML1 = """
ASDFASDFASF

"""

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        # -- Envio de la respuesta al cliente

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


        mensaje = """
        <!DOCTYPE>
        <html>
        <body>
        """

        mensaje += "<p>" + "Hola mundo!" + "</p>"
        mensaje += "<ul>"
        mensaje += "<li>Recurso solicitado: {}</li>".format(self.path)
        mensaje += "</ul>"
        mensaje += "</body>"
        mensaje += "</html>"

        self.wfile.write(bytes(mensaje, "utf8"))
        print("Petición atendida!")
        return


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en puerto: {}".format(PORT))


try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Servidor detenido")
    httpd.server_close()

