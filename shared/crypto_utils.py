"""
Módulo de utilidades criptográficas para el Notario Digital.
Implementa ECDSA para firmas digitales y SHA-256 para hashing.
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import hashlib
import base64
from datetime import datetime
import json


class NotarioCrypto:
    """
    Clase principal para operaciones criptográficas del Notario Digital.
    Utiliza ECDSA (Elliptic Curve Digital Signature Algorithm) con curva SECP256R1.
    """
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generar_par_claves(self):
        """
        Genera un nuevo par de claves ECDSA usando la curva SECP256R1.
        
        Returns:
            tuple: (clave_privada, clave_publica)
        """
        self.private_key = ec.generate_private_key(
            ec.SECP256R1(),  # Curva elíptica segura
            default_backend()
        )
        self.public_key = self.private_key.public_key()
        return self.private_key, self.public_key
    
    def guardar_clave_privada(self, filepath, password=None):
        """
        Guarda la clave privada en formato PEM, opcionalmente cifrada.
        
        Args:
            filepath (str): Ruta donde guardar la clave
            password (str, optional): Contraseña para cifrar la clave
        """
        if self.private_key is None:
            raise ValueError("No hay clave privada generada")
        
        encryption_algorithm = serialization.NoEncryption()
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
        
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        with open(filepath, 'wb') as f:
            f.write(pem)
    
    def cargar_clave_privada(self, filepath, password=None):
        """
        Carga una clave privada desde un archivo PEM.
        
        Args:
            filepath (str): Ruta del archivo de clave privada
            password (str, optional): Contraseña si la clave está cifrada
        """
        with open(filepath, 'rb') as f:
            pem_data = f.read()
        
        pwd = password.encode() if password else None
        self.private_key = serialization.load_pem_private_key(
            pem_data,
            password=pwd,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def guardar_clave_publica(self, filepath):
        """
        Guarda la clave pública en formato PEM.
        
        Args:
            filepath (str): Ruta donde guardar la clave pública
        """
        if self.public_key is None:
            raise ValueError("No hay clave pública generada")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(filepath, 'wb') as f:
            f.write(pem)
    
    def cargar_clave_publica(self, filepath):
        """
        Carga una clave pública desde un archivo PEM.
        
        Args:
            filepath (str): Ruta del archivo de clave pública
        """
        with open(filepath, 'rb') as f:
            pem_data = f.read()
        
        self.public_key = serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
    
    def calcular_hash_archivo(self, filepath):
        """
        Calcula el hash SHA-256 de un archivo.
        
        Args:
            filepath (str): Ruta del archivo a hashear
            
        Returns:
            str: Hash SHA-256 en formato hexadecimal
        """
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            # Leer en bloques para archivos grandes
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def firmar_hash(self, hash_hex, timestamp=None):
        """
        Firma un hash usando ECDSA con la clave privada del notario.
        
        Args:
            hash_hex (str): Hash en formato hexadecimal
            timestamp (str, optional): Timestamp ISO format. Si no se provee, usa el actual
            
        Returns:
            dict: Recibo digital con {timestamp, hash, firma}
        """
        if self.private_key is None:
            raise ValueError("No hay clave privada cargada")
        
        # Usar timestamp actual si no se provee
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Crear el mensaje a firmar: hash + timestamp
        mensaje = f"{hash_hex}|{timestamp}".encode()
        
        # Firmar con ECDSA
        firma = self.private_key.sign(
            mensaje,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Codificar firma en base64 para facilitar transmisión
        firma_b64 = base64.b64encode(firma).decode()
        
        return {
            "timestamp": timestamp,
            "hash": hash_hex,
            "firma": firma_b64
        }
    
    def verificar_firma(self, recibo, clave_publica=None):
        """
        Verifica la autenticidad de un recibo digital.
        
        Args:
            recibo (dict): Recibo con {timestamp, hash, firma}
            clave_publica: Clave pública a usar (opcional, usa la cargada si no se provee)
            
        Returns:
            bool: True si la firma es válida, False en caso contrario
        """
        try:
            # Usar la clave pública provista o la interna
            pub_key = clave_publica if clave_publica else self.public_key
            
            if pub_key is None:
                raise ValueError("No hay clave pública disponible")
            
            # Reconstruir el mensaje original
            mensaje = f"{recibo['hash']}|{recibo['timestamp']}".encode()
            
            # Decodificar la firma
            firma = base64.b64decode(recibo['firma'])
            
            # Verificar la firma
            pub_key.verify(
                firma,
                mensaje,
                ec.ECDSA(hashes.SHA256())
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Error en verificación: {e}")
            return False
    
    def exportar_clave_publica_str(self):
        """
        Exporta la clave pública como string PEM.
        
        Returns:
            str: Clave pública en formato PEM
        """
        if self.public_key is None:
            raise ValueError("No hay clave pública generada")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return pem.decode()
    
    def importar_clave_publica_str(self, pem_str):
        """
        Importa una clave pública desde string PEM.
        
        Args:
            pem_str (str): Clave pública en formato PEM
        """
        self.public_key = serialization.load_pem_public_key(
            pem_str.encode(),
            backend=default_backend()
        )


def guardar_recibo(recibo, filepath):
    """
    Guarda un recibo digital en formato JSON.
    
    Args:
        recibo (dict): Recibo a guardar
        filepath (str): Ruta donde guardar el recibo
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recibo, f, indent=2, ensure_ascii=False)


def cargar_recibo(filepath):
    """
    Carga un recibo digital desde un archivo JSON.
    
    Args:
        filepath (str): Ruta del archivo de recibo
        
    Returns:
        dict: Recibo cargado
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
