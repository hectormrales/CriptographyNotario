# 🚀 Guía Rápida de Inicio - Notario Digital

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Instalar Dependencias

```powershell
cd c:\Users\Hector.Morales\Documents\CriptographyNotario
pip install -r requirements.txt
```

### 2️⃣ Iniciar el Servidor

**Opción A - Script automático:**
```powershell
.\iniciar_servidor.bat
```

**Opción B - Manual:**
```powershell
python server\api_server.py
```

**Opción C - Con entorno virtual:**
```powershell
.venv\Scripts\python.exe server\api_server.py
```

Verás:
```
🏛️  NOTARIO DIGITAL - Servidor API
🔑 Generando nuevo par de claves ECDSA...
✅ Claves generadas y guardadas
🚀 Servidor listo para recibir solicitudes
Uvicorn running on http://127.0.0.1:8000
```

### 3️⃣ Iniciar la Aplicación Cliente

**En una NUEVA terminal:**

**Opción A - Script automático:**
```powershell
.\iniciar_cliente.bat
```

**Opción B - Manual:**
```powershell
python client\notario_gui.py
```

**Opción C - Con entorno virtual:**
```powershell
.venv\Scripts\python.exe client\notario_gui.py
```

---

## 📝 Uso de la Aplicación

### Notarizar un Documento

1. Abre la pestaña **"📝 Notarizar Documento"**
2. Click en **"📂 Seleccionar Archivo"**
3. Elige cualquier archivo (PDF, TXT, DOCX, imagen, etc.)
4. El hash SHA-256 se calculará automáticamente
5. Click en **"🔏 Notarizar Documento"**
6. El recibo se guarda en la carpeta `receipts/`

### Verificar un Documento

1. Abre la pestaña **"✓ Verificar Recibo"**
2. Click en **"📂 Cargar Recibo (.json)"**
3. Selecciona el archivo de recibo
4. Click en **"📂 Seleccionar Archivo"**
5. Elige el archivo original
6. Click en **"✓ Verificar Autenticidad"**
7. El sistema te dirá si el documento es auténtico

---

## 🧪 Prueba Rápida

### Prueba Manual

1. **Crear archivo de prueba:**
   ```powershell
   echo "Documento de prueba" > documento.txt
   ```

2. **Notarizar el archivo:**
   - Usa la aplicación GUI para notarizar `documento.txt`
   - Se creará un recibo en `receipts/`

3. **Verificar (debe ser VÁLIDO):**
   - Carga el recibo
   - Selecciona el archivo original `documento.txt`
   - Resultado: ✅ VÁLIDO

4. **Modificar el archivo:**
   ```powershell
   echo "Modificado" >> documento.txt
   ```

5. **Verificar de nuevo (debe FALLAR):**
   - Usa el mismo recibo
   - Selecciona el archivo modificado
   - Resultado: ❌ INVÁLIDO (hash diferente)

### Prueba Automatizada

```powershell
python shared\test_suite.py
```

Esto ejecutará una suite completa de pruebas.

---

## 🔧 Solución de Problemas

### El servidor no inicia

**Error: `ModuleNotFoundError: No module named 'fastapi'`**

**Solución:**
```powershell
pip install -r requirements.txt
```

o con entorno virtual:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### El cliente no puede conectarse al servidor

**Error: "No se puede conectar al servidor"**

**Solución:**
1. Verifica que el servidor esté ejecutándose
2. Abre http://127.0.0.1:8000 en tu navegador
3. Deberías ver información del servicio

### Puerto 8000 ocupado

**Error: `Address already in use`**

**Solución:**
```powershell
# Encontrar el proceso
netstat -ano | findstr :8000

# Matar el proceso (reemplaza PID)
taskkill /PID <numero_pid> /F
```

O cambia el puerto en `server/api_server.py` (línea final):
```python
uvicorn.run(app, host="127.0.0.1", port=8001)  # Cambiar a 8001
```

---

## 🔑 Conceptos Clave

### Hash SHA-256
- Huella digital única de 64 caracteres hexadecimales
- Cualquier cambio en el archivo → hash completamente diferente
- Imposible revertir (no se puede obtener el archivo desde el hash)

### Firma Digital ECDSA
- Solo el notario puede crear firmas válidas (tiene la clave privada)
- Cualquiera puede verificar (usa la clave pública)
- Matemáticamente imposible de falsificar

### Recibo Digital
Un archivo JSON con:
- **timestamp**: Momento exacto de la notarización
- **hash**: Huella digital SHA-256 del archivo
- **firma**: Firma ECDSA del notario

---

## 📂 Archivos Importantes

```
CriptographyNotario/
├── keys/
│   ├── notario_private.pem  ⚠️ NUNCA COMPARTIR
│   └── notario_public.pem   ✓ Puede compartirse
│
├── receipts/
│   └── recibo_*.json        ✓ Recibos digitales
│
├── server/
│   └── api_server.py        🖥️ Servidor API
│
├── client/
│   └── notario_gui.py       🖼️ Aplicación GUI
│
└── shared/
    ├── crypto_utils.py      🔐 Funciones criptográficas
    └── test_suite.py        🧪 Pruebas automatizadas
```

---

## 🌐 API Endpoints

### GET /
Información del servicio

### GET /health
Estado del servidor

### GET /clave-publica
Obtiene la clave pública del notario

### POST /notarizar
Notariza un hash

**Request:**
```json
{
  "hash": "65c63a813709be2e928f1c8d54a1015e17c2bbcb2ae83d41007a1a34d3a9059a"
}
```

**Response:**
```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "hash": "65c63a8...",
  "firma": "MEUCIQDx...",
  "mensaje": "Documento notarizado exitosamente"
}
```

### POST /verificar
Verifica un recibo

**Request:**
```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "hash": "65c63a8...",
  "firma": "MEUCIQDx..."
}
```

**Response:**
```json
{
  "valido": true,
  "mensaje": "El recibo es auténtico y válido"
}
```

---

## 💡 Tips

### Backup de Claves
```powershell
# Hacer backup de la clave privada
copy keys\notario_private.pem C:\BackupSeguro\
```

### Ver Recibos
Los recibos son archivos JSON que puedes abrir con cualquier editor de texto:
```powershell
notepad receipts\recibo_documento.txt_2025-11-10T14-30-00Z.json
```

### Probar desde línea de comandos

**Calcular hash:**
```powershell
python -c "from shared.crypto_utils import NotarioCrypto; c = NotarioCrypto(); print(c.calcular_hash_archivo('archivo.txt'))"
```

**Notarizar vía API:**
```powershell
curl -X POST http://127.0.0.1:8000/notarizar -H "Content-Type: application/json" -d '{\"hash\":\"65c63a813709be2e928f1c8d54a1015e17c2bbcb2ae83d41007a1a34d3a9059a\"}'
```

---

## ⚠️ Seguridad

### ✅ Buenas Prácticas
- Guarda backups cifrados de `notario_private.pem`
- Nunca compartas la clave privada
- Guarda los recibos en lugares seguros
- Considera usar contraseña para la clave privada

### ❌ NO Hacer
- NO subir `notario_private.pem` a GitHub
- NO enviar la clave privada por email
- NO perder los recibos (son irrecuperables)
- NO compartir la misma clave para producción y pruebas

---

## 🎯 Casos de Uso Reales

✓ **Contratos Digitales**: Firma de acuerdos con fecha certificada
✓ **Código Fuente**: Protección de propiedad intelectual
✓ **Trabajos Académicos**: Prevención de plagio con fecha
✓ **Arte Digital**: Certificación de autoría
✓ **Documentos Legales**: Evidencia temporal
✓ **Reportes**: Certificación de integridad

---

## 📚 Recursos

- [Documentación cryptography.io](https://cryptography.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ECDSA Wikipedia](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [SHA-256 Explanation](https://en.wikipedia.org/wiki/SHA-2)

---

## ❓ FAQ

**P: ¿Puedo notarizar el mismo archivo dos veces?**
R: Sí, cada notarización tendrá un timestamp diferente.

**P: ¿El servidor guarda mis archivos?**
R: NO. El servidor solo recibe el hash (64 caracteres), nunca el archivo completo.

**P: ¿Qué pasa si pierdo el recibo?**
R: No se puede recuperar. Guarda siempre copias de seguridad.

**P: ¿Puedo verificar sin el servidor?**
R: Sí, si tienes la clave pública puedes verificar localmente usando `crypto_utils.py`.

**P: ¿Es seguro para producción?**
R: Este es un prototipo educativo. Para producción necesitarías:
- HTTPS
- Timestamping RFC 3161 certificado
- HSM para claves
- Almacenamiento distribuido/blockchain

---

**¡Disfruta tu Notario Digital! 🏛️**
