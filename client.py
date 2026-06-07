import socket
import threading
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

HOST = '127.0.0.1'
PORT = 55555

# --- 1. GÉNÉRATION DES CLÉS RSA DU CLIENT ---
print("[*] Génération de tes clés de chiffrement RSA (2048 bits)...")
cle_privee = rsa.generate_private_key(public_exponent=65537, key_size=2048)
cle_publique = cle_privee.public_key()

# Sérialisation de la clé publique pour pouvoir l'envoyer sur le réseau
cle_publique_bytes = cle_publique.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

cle_publique_destinataire = None
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def chiffrer_message(message_clair, public_key):
    """Chiffre le message avec AES, puis chiffre la clé AES avec RSA."""
    # Génération d'une clé AES unique pour ce message
    aes_key = os.urandom(32)  # AES-256
    iv = os.urandom(16)       # Vecteur d'initialisation
    
    # Chiffrement du texte avec AES
    encryptor = Cipher(algorithms.AES(aes_key), modes.CFB(iv)).encryptor()
    ciphertext = encryptor.update(message_clair.encode('utf-8')) + encryptor.finalize()
    
    # Chiffrement de la clé AES avec la clé publique RSA du destinataire
    cle_aes_chiffree = public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
    # On package le tout proprement : longueur_clé_RSA (256 octets) + IV (16 octets) + Clé_AES_Chiffrée + Message_Chiffré
    return iv + cle_aes_chiffree + ciphertext

def dechiffrer_message(donnees_chiffrees, private_key):
    """Découpe le paquet, déchiffre la clé AES avec RSA, puis le message avec AES."""
    iv = donnees_chiffrees[:16]
    cle_aes_chiffree = donnees_chiffrees[16:272]  # RSA 2048 produit un bloc de 256 octets
    ciphertext = donnees_chiffrees[272:]
    
    # Déchiffrement de la clé AES via la clé privée RSA
    aes_key = private_key.decrypt(
        cle_aes_chiffree,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    
    # Déchiffrement du texte brut via AES
    decryptor = Cipher(algorithms.AES(aes_key), modes.CFB(iv)).decryptor()
    message_clair = decryptor.update(ciphertext) + decryptor.finalize()
    return message_clair.decode('utf-8')

def recevoir():
    global cle_publique_destinataire
    while True:
        try:
            donnees = client.recv(4096)
            if not donnees:
                break
            
            # Si on reçoit une clé publique (reconnaissable à son header PEM)
            if b"-----BEGIN PUBLIC KEY-----" in donnees:
                cle_publique_destinataire = serialization.load_pem_public_key(donnees)
                print("\n[+] Clé publique du correspondant reçue ! Sécurité activée.")
            else:
                # C'est un message chiffré
                texte_clair = dechiffrer_message(donnees, cle_privee)
                print(f"\n[Correspondant] : {texte_clair}")
        except Exception as e:
            print(f"\n[-] Erreur de réception ou déchiffrement: {e}")
            client.close()
            break

def envoyer():
    global cle_publique_destinataire
    # Étape cruciale : On commence par envoyer notre clé publique dès la connexion
    client.send(cle_publique_bytes)
    
    while True:
        message = input("")
        if message.lower() == 'exit':
            client.close()
            break
        
        if cle_publique_destinataire is None:
            print("[!] En attente de la clé publique de l'autre utilisateur...")
            continue
            
        donnees_chiffrees = chiffrer_message(message, cle_publique_destinataire)
        client.send(donnees_chiffrees)

# Démarrage des threads pour gérer l'envoi et la réception en même temps
thread_recevoir = threading.Thread(target=recevoir)
thread_recevoir.start()

thread_envoyer = threading.Thread(target=envoyer)
thread_envoyer.start()