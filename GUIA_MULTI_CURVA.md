# 🔐 Guía de Uso: Soporte Multi-Curva

## Introducción

El Notario Digital v2.0 ahora soporta múltiples curvas elípticas, permitiéndote elegir el estándar criptográfico que mejor se adapte a tus necesidades.

## 🎯 ¿Qué Curva Debo Usar?

### SECP256R1 (NIST P-256) - **Recomendada para mayoría de casos**

✅ **Cuándo usarla:**
- Documentos legales y contratos
- Certificados y títulos
- Cualquier uso general
- Máxima compatibilidad con sistemas existentes

📊 **Ventajas:**
- Estándar global ampliamente adoptado
- Usado en TLS/SSL
- Excelente soporte en hardware y software
- Balance perfecto entre seguridad y rendimiento

### SECP256K1 - **Para aplicaciones blockchain**

✅ **Cuándo usarla:**
- Integración con Bitcoin o Ethereum
- Aplicaciones de criptomonedas
- Smart contracts
- NFTs y tokens

📊 **Ventajas:**
- Compatible con ecosistema blockchain
- Misma curva que Bitcoin
- Óptima para aplicaciones cripto
- Comunidad grande y activa

⚠️ **Nota:** Menos adoptada fuera del mundo blockchain

### SECP384R1 (NIST P-384) - **Alta seguridad**

✅ **Cuándo usarla:**
- Información sensible o clasificada
- Documentos de alto valor
- Requisitos de seguridad estrictos
- Aplicaciones gubernamentales

📊 **Ventajas:**
- 384 bits de seguridad
- Recomendada para información clasificada
- Mayor margen de seguridad a largo plazo

⚠️ **Nota:** Firmas más grandes, procesamiento ligeramente más lento

### SECP521R1 (NIST P-521) - **Máxima seguridad**

✅ **Cuándo usarla:**
- Documentos extremadamente sensibles
- Almacenamiento a muy largo plazo
- Máximos requisitos de seguridad

📊 **Ventajas:**
- 521 bits de seguridad
- Máximo nivel disponible
- Futuro-proof

⚠️ **Nota:** Firmas más grandes, procesamiento más lento

## 📚 Guía Paso a Paso

### 1. Generar Claves para una Curva

1. Abre el **Notario Digital**
2. Ve a la pestaña **"🔑 Gestión de Llaves"**
3. En el menú desplegable, selecciona la curva deseada
4. Lee la descripción para confirmar que es la adecuada
5. (Opcional) Marca "Proteger clave privada con contraseña"
6. Click en **"🔑 Generar Nuevo Par de Claves"**
7. Confirma la operación

**Resultado:** Se crearán dos archivos en `keys/`:
- `notario_private_secp256k1.pem` (clave privada - ¡PROTÉGELA!)
- `notario_public_secp256k1.pem` (clave pública - compartible)

### 2. Notarizar un Documento con una Curva Específica

1. **Selecciona la curva** en "Gestión de Llaves"
2. Ve a la pestaña **"📝 Notarizar Documento"**
3. Click en "📂 Seleccionar Archivo"
4. Selecciona tu documento
5. El sistema calculará el hash automáticamente
6. Click en **"🔏 Notarizar Documento"**
   - El sistema usará la curva que seleccionaste en paso 1
7. Guarda el recibo JSON generado

**El recibo incluirá:**
```json
{
  "timestamp": "2025-11-19T10:30:00Z",
  "hash": "abc123...",
  "firma": "MEUCIQ...",
  "curva": "SECP256K1",  ← Curva utilizada
  "archivo_original": "documento.pdf"
}
```

### 3. Verificar un Recibo

1. Ve a **"✓ Verificar Recibo"**
2. Click en "📂 Cargar Recibo (.json)"
3. Selecciona el archivo JSON del recibo
4. Click en "📂 Seleccionar Archivo" para el documento
5. Click en **"✓ Verificar Autenticidad"**

**El sistema:**
- Detecta automáticamente qué curva se usó (del recibo)
- Carga la clave pública correspondiente
- Verifica la firma
- Muestra si es válido o no

### 4. Ver Todas tus Claves

1. Ve a **"🔑 Gestión de Llaves"**
2. Desplázate hacia abajo
3. En "3. Claves Existentes" verás todas las claves organizadas por curva
4. Click en "🔄 Actualizar Lista de Claves" para refrescar

## 🔄 Ejemplo Completo: Bitcoin + Notarización

Escenario: Quieres notarizar el whitepaper de tu proyecto de blockchain.

```
1. Gestión de Llaves
   └─ Seleccionar: "SECP256K1 - Bitcoin/Ethereum"
   └─ Generar claves

2. Notarizar Documento
   └─ Archivo: "mi_proyecto_whitepaper.pdf"
   └─ Notarizar (usará SECP256K1)
   └─ Guardar: "recibo_whitepaper_SECP256K1_2025-11-19.json"

3. Publicar
   └─ Sube el recibo a IPFS o tu blockchain
   └─ Ahora tienes prueba timestamp con la curva de Bitcoin!
```

## 🔒 Mejores Prácticas

### Seguridad de Claves

✅ **HAZ:**
- Haz backup de tus claves en un lugar seguro
- Usa contraseña para claves privadas sensibles
- Una curva diferente por tipo de aplicación
- Mantén las claves privadas en un dispositivo seguro

❌ **NO HAGAS:**
- Compartir claves privadas NUNCA
- Usar la misma curva para casos incompatibles
- Subir claves privadas a repositorios públicos
- Reutilizar contraseñas débiles

### Organización

Estructura recomendada:

```
keys/
├── notario_private_secp256r1.pem  ← Documentos generales
├── notario_public_secp256r1.pem
├── notario_private_secp256k1.pem  ← Blockchain/NFT
├── notario_public_secp256k1.pem
├── notario_private_secp384r1.pem  ← Alta seguridad
└── notario_public_secp384r1.pem
```

## 🆘 Troubleshooting

### "Curva no soportada"
**Causa:** El servidor no tiene las claves para esa curva
**Solución:** Genera las claves en "Gestión de Llaves"

### "Error verificando recibo"
**Causa:** Falta la clave pública de la curva usada
**Solución:** 
1. Verifica qué curva está en el recibo
2. Obtén la clave pública correspondiente del notario
3. Colócala en `keys/notario_public_{curva}.pem`

### "Las firmas no coinciden"
**Causa:** El archivo fue modificado o curva incorrecta
**Solución:** 
1. Verifica que el archivo sea exactamente el original
2. Verifica que la curva del recibo coincida con las claves

## 📖 Referencias Técnicas

- [RFC 5480 - ECC SubjectPublicKeyInfo](https://tools.ietf.org/html/rfc5480)
- [SEC 2: Recommended Elliptic Curve Domain Parameters](https://www.secg.org/sec2-v2.pdf)
- [Bitcoin Curve SECP256K1](https://en.bitcoin.it/wiki/Secp256k1)
- [NIST FIPS 186-4 - Digital Signature Standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)

## 💡 Casos de Uso Avanzados

### Multi-Firma (Misma Curva)
Notariza el mismo documento con diferentes servidores usando la misma curva para redundancia.

### Cadena de Custodia
Usa diferentes curvas para diferentes etapas del documento:
1. Creación: SECP256R1
2. Revisión: SECP384R1  
3. Publicación blockchain: SECP256K1

### Archivo a Largo Plazo
Para documentos que debes conservar 50+ años, usa SECP521R1 para máxima seguridad a futuro.

---

¿Preguntas? Revisa la pestaña "ℹ️ Información" en la aplicación o consulta el README.md principal.
