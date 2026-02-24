"Lag en temp klasse som bare er idle og ikke gjør noe som helst egentlig, er bare brukt for å teste raft implementasjonen"

from flask import Flask, request


class LocalController:
    def __init__(self, host, port):
        self.running = True
        self.host = host
        self.port = port
        self.address = f"{self.host}:{self.port}"
        self.app = Flask(__name__)
        self.setup_routes()


    def setup_routes(self):
        @self.app.route("/")
        def home():
            return "Node running"

        @self.app.route("/kill", methods=["POST"])
        def kill():
            return self.killLocalController()



    def killLocalController(self):
        self.running = False


        func = request.environ.get("werkzeug.server.shutdown")
        if func:
            func()

        return f"Trying to kill node - Running status: {self.running}"


    def start(self):

        if self.running == True:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=True, 
                use_reloader=False)
        


if __name__ == "__main__":
    controller = LocalController("c6-8", "66666")
    controller.start()