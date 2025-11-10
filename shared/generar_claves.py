"""
Script de utilidad para generar un par de claves manualmente
y exportarlas en diferentes formatos.
"""

import sys
import os

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto


def main():
    print("=" * 60)
    print("Generador de Claves ECDSA - Notario Digital")
    print("=" * 60)
    print()
    
    # Crear instancia
    crypto = NotarioCrypto()
    
    # Generar claves
    print("🔑 Generando par de claves ECDSA (SECP256R1)...")
    crypto.generar_par_claves()
    print("✅ Claves generadas exitosamente")
    print()
    
    # Preguntar si cifrar con contraseña
    usar_password = input("¿Deseas proteger la clave privada con contraseña? (s/n): ").lower()
    password = None
    
    if usar_password == 's':
        password = input("Ingresa la contraseña: ")
        confirm = input("Confirma la contraseña: ")
        
        if password != confirm:
            print("❌ Las contraseñas no coinciden")
            return
        
        print("🔒 Se usará contraseña para cifrar la clave privada")
    
    # Rutas
    keys_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
    os.makedirs(keys_dir, exist_ok=True)
    
    private_path = os.path.join(keys_dir, 'notario_private.pem')
    public_path = os.path.join(keys_dir, 'notario_public.pem')
    
    # Guardar claves
    print()
    print("💾 Guardando claves...")
    crypto.guardar_clave_privada(private_path, password)
    crypto.guardar_clave_publica(public_path)
    
    print(f"✅ Clave privada guardada en: {private_path}")
    print(f"✅ Clave pública guardada en: {public_path}")
    print()
    
    # Mostrar clave pública
    print("=" * 60)
    print("Clave Pública (puede compartirse):")
    print("=" * 60)
    print(crypto.exportar_clave_publica_str())
    
    print("=" * 60)
    print("✅ Proceso completado")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - NUNCA compartas la clave privada")
    print("   - Guarda la clave privada en un lugar seguro")
    print("   - La clave pública puede compartirse libremente")
    print("=" * 60)


if __name__ == "__main__":
    main()
