"""
Script de prueba automatizada para el Notario Digital.
Verifica que todos los componentes funcionen correctamente.
"""

import sys
import os
import time
import requests
import json

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto, guardar_recibo, cargar_recibo


def imprimir_seccion(titulo):
    """Imprime una sección formateada."""
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)


def test_crypto_local():
    """Prueba las funciones criptográficas locales."""
    imprimir_seccion("TEST 1: Funciones Criptográficas Locales")
    
    crypto = NotarioCrypto()
    
    # Test 1: Generar claves
    print("✓ Generando par de claves ECDSA...")
    crypto.generar_par_claves()
    print("  ✅ Claves generadas exitosamente")
    
    # Test 2: Calcular hash
    test_file = os.path.join(os.path.dirname(__file__), '..', 'test_document.txt')
    if not os.path.exists(test_file):
        print(f"  ⚠️  Archivo de prueba no encontrado: {test_file}")
        return False
    
    print(f"\n✓ Calculando hash SHA-256 del archivo de prueba...")
    hash_archivo = crypto.calcular_hash_archivo(test_file)
    print(f"  ✅ Hash calculado: {hash_archivo[:32]}...")
    
    # Test 3: Firmar
    print(f"\n✓ Firmando hash con ECDSA...")
    recibo = crypto.firmar_hash(hash_archivo)
    print(f"  ✅ Firma generada")
    print(f"     Timestamp: {recibo['timestamp']}")
    print(f"     Firma: {recibo['firma'][:50]}...")
    
    # Test 4: Verificar
    print(f"\n✓ Verificando firma...")
    es_valido = crypto.verificar_firma(recibo)
    if es_valido:
        print(f"  ✅ Firma válida - Verificación exitosa")
    else:
        print(f"  ❌ Firma inválida - ERROR")
        return False
    
    # Test 5: Verificar firma alterada (debe fallar)
    print(f"\n✓ Probando detección de alteración...")
    recibo_alterado = recibo.copy()
    recibo_alterado['hash'] = 'a' * 64  # Hash falso
    es_valido_alterado = crypto.verificar_firma(recibo_alterado)
    if not es_valido_alterado:
        print(f"  ✅ Alteración detectada correctamente")
    else:
        print(f"  ❌ No se detectó la alteración - ERROR")
        return False
    
    return True


def test_servidor_api():
    """Prueba el servidor API."""
    imprimir_seccion("TEST 2: Servidor API")
    
    api_url = "http://127.0.0.1:8000"
    
    # Test 1: Health check
    print("✓ Verificando estado del servidor...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Servidor activo y respondiendo")
        else:
            print(f"  ❌ Servidor respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ No se puede conectar al servidor")
        print(f"  ⚠️  Asegúrate de ejecutar: python server/api_server.py")
        return False
    
    # Test 2: Obtener clave pública
    print(f"\n✓ Obteniendo clave pública del notario...")
    response = requests.get(f"{api_url}/clave-publica", timeout=5)
    if response.status_code == 200:
        clave_publica = response.json()['clave_publica']
        print(f"  ✅ Clave pública obtenida ({len(clave_publica)} bytes)")
    else:
        print(f"  ❌ Error obteniendo clave pública")
        return False
    
    # Test 3: Notarizar
    print(f"\n✓ Notarizando un hash de prueba...")
    crypto = NotarioCrypto()
    test_file = os.path.join(os.path.dirname(__file__), '..', 'test_document.txt')
    hash_prueba = crypto.calcular_hash_archivo(test_file)
    
    response = requests.post(
        f"{api_url}/notarizar",
        json={"hash": hash_prueba},
        timeout=5
    )
    
    if response.status_code == 200:
        recibo = response.json()
        print(f"  ✅ Documento notarizado")
        print(f"     Timestamp: {recibo['timestamp']}")
        print(f"     Hash: {recibo['hash'][:32]}...")
        print(f"     Firma: {recibo['firma'][:50]}...")
    else:
        print(f"  ❌ Error en notarización: {response.text}")
        return False
    
    # Test 4: Verificar
    print(f"\n✓ Verificando recibo...")
    response = requests.post(
        f"{api_url}/verificar",
        json={
            "timestamp": recibo['timestamp'],
            "hash": recibo['hash'],
            "firma": recibo['firma']
        },
        timeout=5
    )
    
    if response.status_code == 200:
        resultado = response.json()
        if resultado['valido']:
            print(f"  ✅ Recibo verificado como válido")
        else:
            print(f"  ❌ Recibo marcado como inválido - ERROR")
            return False
    else:
        print(f"  ❌ Error en verificación: {response.text}")
        return False
    
    # Test 5: Verificar recibo alterado (debe fallar)
    print(f"\n✓ Probando detección de alteración en el servidor...")
    response = requests.post(
        f"{api_url}/verificar",
        json={
            "timestamp": recibo['timestamp'],
            "hash": 'a' * 64,  # Hash alterado
            "firma": recibo['firma']
        },
        timeout=5
    )
    
    if response.status_code == 200:
        resultado = response.json()
        if not resultado['valido']:
            print(f"  ✅ Alteración detectada correctamente por el servidor")
        else:
            print(f"  ❌ Servidor no detectó la alteración - ERROR")
            return False
    else:
        print(f"  ❌ Error: {response.text}")
        return False
    
    return True


def test_integracion_completa():
    """Prueba el flujo completo de notarización y verificación."""
    imprimir_seccion("TEST 3: Integración Completa")
    
    api_url = "http://127.0.0.1:8000"
    crypto = NotarioCrypto()
    
    # Archivo de prueba
    test_file = os.path.join(os.path.dirname(__file__), '..', 'test_document.txt')
    
    # 1. Calcular hash del archivo
    print("✓ Paso 1: Usuario calcula hash del archivo localmente...")
    hash_archivo = crypto.calcular_hash_archivo(test_file)
    print(f"  ✅ Hash: {hash_archivo}")
    
    # 2. Enviar solo el hash al servidor (privacidad)
    print(f"\n✓ Paso 2: Enviar SOLO el hash al servidor (no el archivo)...")
    response = requests.post(
        f"{api_url}/notarizar",
        json={"hash": hash_archivo},
        timeout=5
    )
    
    if response.status_code != 200:
        print(f"  ❌ Error en notarización")
        return False
    
    recibo = response.json()
    print(f"  ✅ Recibo digital recibido")
    
    # 3. Guardar recibo
    print(f"\n✓ Paso 3: Guardar recibo digital...")
    receipts_dir = os.path.join(os.path.dirname(__file__), '..', 'receipts')
    os.makedirs(receipts_dir, exist_ok=True)
    
    recibo_path = os.path.join(receipts_dir, 'test_recibo.json')
    recibo_completo = {
        "timestamp": recibo['timestamp'],
        "hash": recibo['hash'],
        "firma": recibo['firma'],
        "archivo_original": "test_document.txt"
    }
    guardar_recibo(recibo_completo, recibo_path)
    print(f"  ✅ Recibo guardado en: {recibo_path}")
    
    # 4. Simular verificación posterior
    print(f"\n✓ Paso 4: Verificación posterior del documento...")
    
    # Cargar recibo guardado
    recibo_cargado = cargar_recibo(recibo_path)
    
    # Calcular hash del archivo actual
    hash_actual = crypto.calcular_hash_archivo(test_file)
    
    # Verificar que el hash coincide
    if hash_actual != recibo_cargado['hash']:
        print(f"  ❌ El archivo ha sido modificado (hash diferente)")
        return False
    
    print(f"  ✅ Hash del archivo coincide con el recibo")
    
    # Verificar firma con el servidor
    response = requests.post(
        f"{api_url}/verificar",
        json={
            "timestamp": recibo_cargado['timestamp'],
            "hash": recibo_cargado['hash'],
            "firma": recibo_cargado['firma']
        },
        timeout=5
    )
    
    if response.status_code == 200 and response.json()['valido']:
        print(f"  ✅ Firma digital válida - Documento auténtico")
    else:
        print(f"  ❌ Verificación de firma falló")
        return False
    
    print(f"\n  🎉 DOCUMENTO CERTIFICADO Y VERIFICADO EXITOSAMENTE")
    print(f"     - El documento existía en: {recibo_cargado['timestamp']}")
    print(f"     - El documento NO ha sido alterado")
    print(f"     - La firma es auténtica del Notario")
    
    return True


def main():
    """Función principal que ejecuta todos los tests."""
    print("\n" + "=" * 70)
    print("  🏛️  NOTARIO DIGITAL - Suite de Pruebas Automatizadas")
    print("=" * 70)
    
    resultados = []
    
    # Test 1: Criptografía local
    try:
        resultado = test_crypto_local()
        resultados.append(("Criptografía Local", resultado))
    except Exception as e:
        print(f"\n❌ ERROR en test de criptografía: {e}")
        resultados.append(("Criptografía Local", False))
    
    # Test 2: Servidor API
    try:
        resultado = test_servidor_api()
        resultados.append(("Servidor API", resultado))
    except Exception as e:
        print(f"\n❌ ERROR en test del servidor: {e}")
        resultados.append(("Servidor API", False))
    
    # Test 3: Integración completa
    if all(r[1] for r in resultados):
        try:
            resultado = test_integracion_completa()
            resultados.append(("Integración Completa", resultado))
        except Exception as e:
            print(f"\n❌ ERROR en test de integración: {e}")
            resultados.append(("Integración Completa", False))
    else:
        print("\n⚠️  Saltando test de integración debido a fallos previos")
        resultados.append(("Integración Completa", None))
    
    # Resumen
    imprimir_seccion("RESUMEN DE PRUEBAS")
    
    for nombre, resultado in resultados:
        if resultado is None:
            estado = "⊘ OMITIDO"
        elif resultado:
            estado = "✅ PASÓ"
        else:
            estado = "❌ FALLÓ"
        
        print(f"  {estado:<12} {nombre}")
    
    print("\n" + "=" * 70)
    
    total = len([r for r in resultados if r[1] is not None])
    pasados = len([r for r in resultados if r[1] is True])
    
    if pasados == total:
        print(f"  🎉 ¡TODOS LOS TESTS PASARON! ({pasados}/{total})")
        print("=" * 70)
        return 0
    else:
        print(f"  ⚠️  ALGUNOS TESTS FALLARON ({pasados}/{total} pasaron)")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
