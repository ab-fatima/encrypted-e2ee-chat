import socket
import threading

# Configuration du serveur
HOST = '127.0.0.1'  # Localhost (pour tester sur ta machine)
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message, _client_envoyeur):
    """Envoie le message à tous les autres clients connectés."""
    for client in clients:
        if client != _client_envoyeur:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client):
    """Gère la connexion d'un client de manière indépendante."""
    while True:
        try:
            message = client.recv(4096)
            if not message:
                break
            # AJOUTE CETTE LIGNE POUR TOUT VOIR :
            print(f"[Serveur] Données chiffrées reçues : {message}")
            
            broadcast(message, client)
        except:
            clients.remove(client)
            client.close()
            break