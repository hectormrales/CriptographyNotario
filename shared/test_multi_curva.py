"""
Script de prueba para verificar el soporte multi-curva del Notario Digital.
Ejecuta este script para verificar que todas las curvas funcionan correctamente.
"""

import sys
import os

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto, CURVAS_SOPORTADAS, guardar_recibo, cargar_recibo

def test_curva(codigo_curva):
    """Prueba una curva específica."""
    print(f"\n{'='*60}")
    print(f"Probando curva: {codigo_curva}")
    print(f"Nombre: {CURVAS_SOPORTADAS[codigo_curva]['nombre']}")
    print(f"{'='*60}")
    
    try:
        # 1. Generar claves
        print("1. Generando par de claves...")
        crypto = NotarioCrypto(curva=codigo_curva)
        crypto.generar_par_claves()
        print("   ✅ Claves generadas")
        
        # 2. Crear un hash de prueba
        hash_prueba = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        print(f"2. Hash de prueba: {hash_prueba[:32]}...")
        
        # 3. Firmar
        print("3. Firmando hash...")
        recibo = crypto.firmar_hash(hash_prueba)
        print(f"   ✅ Firma generada: {recibo['firma'][:40]}...")
        print(f"   Timestamp: {recibo['timestamp']}")
        print(f"   Curva: {recibo['curva']}")
        
        # 4. Verificar
        print("4. Verificando firma...")
        es_valido = crypto.verificar_firma(recibo)
        if es_valido:
            print("   ✅ Firma VÁLIDA")
        else:
            print("   ❌ Firma INVÁLIDA")
            return False
        
        # 5. Verificar con firma alterada
        print("5. Probando detección de firma alterada...")
        recibo_falso = recibo.copy()
        recibo_falso['firma'] = recibo_falso['firma'][:-10] + "xxxxxxxxxx"
        es_valido_falso = crypto.verificar_firma(recibo_falso)
        if not es_valido_falso:
            print("   ✅ Firma alterada detectada correctamente")
        else:
            print("   ❌ ERROR: No detectó firma alterada")
            return False
        
        # 6. Exportar clave pública
        print("6. Exportando clave pública...")
        pub_key_pem = crypto.exportar_clave_publica_str()
        print(f"   ✅ Clave pública exportada ({len(pub_key_pem)} bytes)")
        
        # 7. Crear nueva instancia y cargar clave pública
        print("7. Probando importación de clave pública...")
        crypto2 = NotarioCrypto(curva=codigo_curva)
        crypto2.importar_clave_publica_str(pub_key_pem)
        
        # 8. Verificar con la clave importada
        print("8. Verificando con clave pública importada...")
        es_valido_importado = crypto2.verificar_firma(recibo)
        if es_valido_importado:
            print("   ✅ Verificación con clave importada: VÁLIDA")
        else:
            print("   ❌ ERROR: Verificación con clave importada falló")
            return False
        
        print(f"\n✅ CURVA {codigo_curva} - TODAS LAS PRUEBAS PASARON")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en curva {codigo_curva}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_guardado_y_carga_recibo():
    """Prueba el guardado y carga de recibos."""
    print(f"\n{'='*60}")
    print("Probando guardado y carga de recibos")
    print(f"{'='*60}")
    
    try:
        # Crear recibo de prueba
        crypto = NotarioCrypto(curva="SECP256K1")
        crypto.generar_par_claves()
        
        hash_prueba = "abc123def456789012345678901234567890123456789012345678901234"
        recibo = crypto.firmar_hash(hash_prueba)
        recibo['archivo_original'] = "test.txt"
        
        # Guardar
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'test_receipts')
        os.makedirs(test_dir, exist_ok=True)
        
        recibo_path = os.path.join(test_dir, 'test_recibo.json')
        print(f"1. Guardando recibo en: {recibo_path}")
        guardar_recibo(recibo, recibo_path)
        print("   ✅ Recibo guardado")
        
        # Cargar
        print("2. Cargando recibo...")
        recibo_cargado = cargar_recibo(recibo_path)
        print("   ✅ Recibo cargado")
        
        # Verificar campos
        print("3. Verificando campos...")
        campos_esperados = ['timestamp', 'hash', 'firma', 'curva', 'archivo_original']
        for campo in campos_esperados:
            if campo not in recibo_cargado:
                print(f"   ❌ Campo faltante: {campo}")
                return False
            if recibo_cargado[campo] != recibo[campo]:
                print(f"   ❌ Campo {campo} no coincide")
                return False
        print("   ✅ Todos los campos correctos")
        
        # Verificar firma del recibo cargado
        print("4. Verificando firma del recibo cargado...")
        es_valido = crypto.verificar_firma(recibo_cargado)
        if es_valido:
            print("   ✅ Firma del recibo cargado: VÁLIDA")
        else:
            print("   ❌ Firma del recibo cargado: INVÁLIDA")
            return False
        
        # Limpiar
        os.remove(recibo_path)
        os.rmdir(test_dir)
        
        print("\n✅ GUARDADO Y CARGA - TODAS LAS PRUEBAS PASARON")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en guardado/carga: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*60)
    print("SUITE DE PRUEBAS - NOTARIO DIGITAL MULTI-CURVA")
    print("="*60)
    
    resultados = {}
    
    # Probar cada curva
    for codigo_curva in CURVAS_SOPORTADAS.keys():
        resultado = test_curva(codigo_curva)
        resultados[codigo_curva] = resultado
    
    # Probar guardado y carga
    resultados['Guardado/Carga'] = test_guardado_y_carga_recibo()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    total = len(resultados)
    exitosas = sum(1 for r in resultados.values() if r)
    
    for nombre, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:20s} : {estado}")
    
    print("="*60)
    print(f"Total: {exitosas}/{total} pruebas exitosas")
    
    if exitosas == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        return 0
    else:
        print("\n⚠️  ALGUNAS PRUEBAS FALLARON. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
