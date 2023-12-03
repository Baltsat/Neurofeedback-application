from pythonosc import dispatcher
from pythonosc import osc_server

def callback(address, *args):
    print(f"Reçu un message OSC à l'adresse {address}: {args}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/muse/eeg", callback)

ip_address = "0.0.0.0"
port = 5000

server = osc_server.ThreadingOSCUDPServer((ip_address, port), dispatcher)

print(f"Écoute sur {ip_address}:{port}")
server.serve_forever()
