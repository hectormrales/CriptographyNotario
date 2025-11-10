# 🏛️ Notario Digital

Sistema de notarización y verificación de documentos digitales usando criptografía ECDSA.

## 📋 Descripción

El Notario Digital es una aplicación de escritorio que permite certificar la existencia e integridad de documentos digitales en un momento específico del tiempo, utilizando firmas digitales basadas en criptografía de curva elíptica (ECDSA).

### El Problema que Resuelve

En el mundo digital, cualquiera puede modificar la fecha de creación de un archivo o alterar su contenido. Este sistema proporciona **certeza criptográfica** sobre:

- ✅ **Existencia temporal**: Prueba que un archivo existía en un momento exacto
- ✅ **Integridad**: Garantiza que el archivo no ha sido alterado desde su notarización
- ✅ **Autenticidad**: La firma digital es infalsificable matemáticamente

## 🔐 Tecnología

### Criptografía Utilizada

- **ECDSA (Elliptic Curve Digital Signature Algorithm)**: Curva SECP256R1
- **SHA-256**: Para generar huellas digitales de los archivos
- **Biblioteca**: `cryptography.io` - biblioteca oficial y recomendada

### Arquitectura

```
┌─────────────────┐         ┌─────────────────┐
│  Cliente GUI    │         │  Servidor API   │
│  (tkinter)      │◄───────►│  (FastAPI)      │
│                 │  HTTPS  │                 │
│  • Calcula hash │         │  • Firma ECDSA  │
│  • Notariza     │         │  • Timestamping │
│  • Verifica     │         │  • Verificación │
└─────────────────┘         └─────────────────┘
```

**Flujo de Notarización:**

1. Usuario selecciona archivo → Cliente calcula SHA-256
2. Cliente envía **solo el hash** (nunca el archivo completo - privacidad)
3. Servidor añade timestamp y firma con clave privada ECDSA
4. Servidor devuelve recibo digital infalsificable

**Flujo de Verificación:**

1. Usuario carga recibo + archivo original
2. Cliente calcula hash del archivo
3. Servidor verifica firma usando clave pública
4. Confirmación de autenticidad

## 📦 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

```powershell
cd c:\Users\Hector.Morales\Documents\CriptographyNotario
```

2. **Instalar dependencias**

```powershell
pip install -r requirements.txt
```

## 🚀 Uso

### 1. Iniciar el Servidor API

Primero, inicia el servidor del Notario Digital:

```powershell
python server\api_server.py
```

Deberías ver:

```
🏛️  NOTARIO DIGITAL - Servidor API
🔑 Generando nuevo par de claves ECDSA...
✅ Claves generadas y guardadas
🚀 Servidor listo para recibir solicitudes
```

El servidor estará disponible en: `http://127.0.0.1:8000`

> **Nota de Seguridad**: La primera vez que se ejecuta, el servidor genera automáticamente un par de claves ECDSA. La clave privada se guarda en `keys/notario_private.pem` y **nunca debe compartirse**.

### 2. Iniciar la Aplicación de Escritorio

En una **nueva terminal**, ejecuta la aplicación cliente:

```powershell
python client\notario_gui.py
```

Se abrirá la interfaz gráfica del Notario Digital.

### 3. Notarizar un Documento

1. En la pestaña **"📝 Notarizar Documento"**:
   - Click en "📂 Seleccionar Archivo"
   - Elige cualquier archivo (documento, imagen, código, etc.)
   - El sistema calculará automáticamente el hash SHA-256
   - Click en "🔏 Notarizar Documento"
   - Se generará un recibo digital en formato JSON

2. **Guardar el recibo**: El recibo se guarda automáticamente en `receipts/`

### 4. Verificar un Documento

1. En la pestaña **"✓ Verificar Recibo"**:
   - Click en "📂 Cargar Recibo (.json)"
   - Selecciona el recibo digital
   - Click en "📂 Seleccionar Archivo"
   - Elige el archivo original
   - Click en "✓ Verificar Autenticidad"

2. **Resultado**: El sistema confirmará si:
   - ✅ El archivo es auténtico (no modificado)
   - ❌ El archivo ha sido alterado o el recibo es inválido

## 📁 Estructura del Proyecto

```
CriptographyNotario/
│
├── client/                     # Aplicación de escritorio
│   └── notario_gui.py         # Interfaz gráfica con tkinter
│
├── server/                     # Servidor API
│   └── api_server.py          # API REST con FastAPI
│
├── shared/                     # Módulos compartidos
│   └── crypto_utils.py        # Utilidades criptográficas
│
├── keys/                       # Claves del notario (generadas)
│   ├── notario_private.pem    # Clave privada (NO compartir)
│   └── notario_public.pem     # Clave pública
│
├── receipts/                   # Recibos digitales generados
│
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

## 🛡️ Seguridad

### Requisitos No Funcionales Implementados

✅ **RNF-1: Protección de Clave Privada**
- La clave privada del notario se almacena en formato PEM cifrado
- Nunca se incluye en el código fuente (no hardcoded)
- Solo el servidor tiene acceso a ella
- Opcionalmente puede protegerse con contraseña

✅ **RNF-2: Privacidad del Usuario**
- El servidor **NUNCA** recibe el archivo original
- Solo se transmite el hash SHA-256 (64 caracteres)
- El contenido del archivo permanece completamente privado

✅ **RNF-3: Integridad Criptográfica**
- ECDSA con curva SECP256R1 (nivel de seguridad equivalente a RSA-3072)
- SHA-256 para hashing (resistente a colisiones)
- Firmas matemáticamente infalsificables

### Protección con Contraseña (Opcional)

Para proteger la clave privada con contraseña:

```powershell
$env:NOTARIO_KEY_PASSWORD="tu_contraseña_segura"
python server\api_server.py
```

## 📚 Requisitos Funcionales

### RF-1: Generación de Claves ✅

El sistema genera automáticamente un par de claves ECDSA:
- Curva elíptica: SECP256R1
- Formato: PEM (Privacy Enhanced Mail)
- Clave privada para firmar
- Clave pública para verificar

### RF-2: Firma de Hash + Timestamp ✅

El notario firma el hash SHA-256 del archivo junto con un timestamp:
- Timestamp en formato ISO 8601 (UTC)
- Firma ECDSA del mensaje `hash|timestamp`
- Codificación Base64 para transporte

### RF-3: Verificación de Firmas ✅

Cualquiera puede verificar un recibo:
- Usa la clave pública del notario
- Confirma que la firma es auténtica
- Detecta cualquier alteración

## 🎯 Casos de Uso

- 🎨 **Arte Digital**: Probar autoría y fecha de creación
- 💼 **Contratos**: Certificar acuerdos digitales
- 💻 **Código Fuente**: Proteger propiedad intelectual
- 📄 **Documentos Legales**: Evidencia temporal
- 🎓 **Trabajos Académicos**: Prevenir plagio temporal
- 🖼️ **NFTs**: Certificación de existencia

## 🧪 Pruebas Rápidas

### Probar Notarización

1. Crea un archivo de prueba:
   ```powershell
   echo "Documento de prueba" > test.txt
   ```

2. Notarízalo usando la aplicación GUI

3. El recibo se guardará en `receipts/`

### Probar Verificación

1. Verifica el archivo original → ✅ Debe ser válido

2. Modifica el archivo:
   ```powershell
   echo "Modificado" >> test.txt
   ```

3. Intenta verificar de nuevo → ❌ Debe fallar (hash diferente)

## 📖 Conceptos Técnicos

### ¿Qué es un Hash SHA-256?

Una función criptográfica que convierte cualquier archivo en una "huella digital" única de 256 bits (64 caracteres hexadecimales).

**Propiedades:**
- Determinista: mismo archivo = mismo hash
- Único: archivos diferentes = hashes diferentes
- Irreversible: imposible recuperar el archivo desde el hash
- Efecto avalancha: un cambio mínimo produce hash completamente diferente

### ¿Qué es ECDSA?

Elliptic Curve Digital Signature Algorithm - algoritmo de firma digital basado en matemática de curvas elípticas.

**Ventajas:**
- Más eficiente que RSA
- Claves más pequeñas con igual seguridad
- Ampliamente usado (Bitcoin, TLS, etc.)

### ¿Por qué es Infalsificable?

1. **Problema matemático difícil**: Romper ECDSA requiere resolver el problema del logaritmo discreto en curvas elípticas
2. **Computacionalmente imposible**: Requeriría más poder de cómputo que todos los ordenadores del mundo juntos durante millones de años
3. **Clave privada secreta**: Solo el notario puede generar firmas válidas

## 🔧 Desarrollo

### Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación
- **cryptography.io**: Biblioteca criptográfica (ECDSA, SHA-256)
- **FastAPI**: Framework web moderno y rápido
- **tkinter**: GUI multiplataforma (incluida con Python)
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Requests**: Cliente HTTP

### API Endpoints

#### `GET /`
Información del servicio

#### `GET /clave-publica`
Obtiene la clave pública del notario

#### `POST /notarizar`
Notariza un hash

**Request:**
```json
{
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

**Response:**
```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "hash": "e3b0c44...",
  "firma": "MEUCIQDx...",
  "mensaje": "Documento notarizado exitosamente"
}
```

#### `POST /verificar`
Verifica un recibo

**Request:**
```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "hash": "e3b0c44...",
  "firma": "MEUCIQDx..."
}
```

**Response:**
```json
{
  "valido": true,
  "mensaje": "El recibo es auténtico y válido",
  "detalles": { ... }
}
```

## 📝 Formato del Recibo Digital

Los recibos se guardan en formato JSON:

```json
{
  "timestamp": "2025-11-10T14:30:00.123456Z",
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "firma": "MEUCIQDxKvqL5h3w...",
  "archivo_original": "documento.pdf"
}
```

## ⚠️ Limitaciones y Consideraciones

1. **Timestamping**: El timestamp es generado por el servidor. En producción, se debería usar un servicio de timestamping externo certificado (RFC 3161).

2. **Almacenamiento**: Los recibos deben guardarse de forma segura. Considerar blockchain o almacenamiento distribuido para producción.

3. **Red Local**: Esta versión funciona en `localhost`. Para producción, implementar HTTPS y autenticación.

4. **Clave Privada**: Proteger adecuadamente. Considerar HSM (Hardware Security Module) para entornos críticos.

## 🚀 Futuras Mejoras

- [ ] Interfaz web (React/Vue)
- [ ] Timestamping RFC 3161 certificado
- [ ] Blockchain para registro inmutable
- [ ] Soporte multi-firma
- [ ] API de integración para terceros
- [ ] Almacenamiento distribuido (IPFS)
- [ ] Aplicación móvil

## 👨‍💻 Autor

Héctor Morales

## 📄 Licencia

Este proyecto es un prototipo educativo desarrollado para demostrar conceptos de criptografía aplicada.

---

**¿Preguntas? ¿Problemas?**

Si el servidor no inicia, verifica:
1. ✅ Python 3.8+ instalado
2. ✅ Dependencias instaladas (`pip install -r requirements.txt`)
3. ✅ Puerto 8000 disponible
4. ✅ Permisos de escritura en carpeta `keys/`

---

**Desarrollado con ❤️ usando Python y criptografía moderna**
