# Clave pública del Notario Digital

Esta carpeta contiene las claves criptográficas del Notario Digital.

## Archivos

- `notario_private.pem` - **Clave privada** (generada automáticamente, NUNCA compartir)
- `notario_public.pem` - **Clave pública** (puede compartirse para verificar firmas)

## Seguridad

⚠️ **IMPORTANTE**: 

- La clave privada es **EXTREMADAMENTE SENSIBLE**
- Nunca la compartas, subas a control de versiones ni la envíes por email
- Si la clave privada se compromete, todas las firmas pierden validez
- Guarda backups seguros de la clave privada (cifrados)

## Regeneración

Si necesitas generar nuevas claves:

1. Detén el servidor
2. Elimina los archivos `.pem` de esta carpeta
3. Inicia el servidor nuevamente
4. Se generarán automáticamente nuevas claves

⚠️ Nota: Los recibos antiguos ya NO serán verificables con las nuevas claves.
