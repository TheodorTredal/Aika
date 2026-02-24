"Lag en temp klasse som bare er idle og ikke gjør noe som helst egentlig, er bare brukt for å teste raft implementasjonen"

from flask import Flask, request, jsonify



class LocalController:
    def __init__(self, host, port):
        self.alive = True
        self.host = host
        self.port = port
        self.address = f"{self.host}:{self.port}"
        self.app = Flask(__name__)
        self.setup_routes()


    def setup_routes(self):
        @self.app.route("/")
        def home():
            return "Node alive"

        @self.app.route("/kill", methods=["POST"])
        def kill():
            self.alive = False
            return  jsonify({"status": f"{self.host}:{self.port} killed"})

        @self.app.route("/restart", methods=["POST"])
        def restart():
            self.alive = True
            return jsonify({"status": f"{self.host}:{self.port} restarted"})


    def init(self):
        '''The node is always running, if alive is set to False, 
        the node is for all intents and purposes not shutdown and can be considered killed / crashed'''
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True, 
            use_reloader=False)
        


        

if __name__ == "__main__":
    controller = LocalController("c6-8", "66666")
    controller.init()