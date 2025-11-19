# Changelog - Notario Digital

## Versión 2.0.0 - Soporte Multi-Curva (19 de Noviembre 2025)

### ✨ Nuevas Características

#### 🔐 Soporte para Múltiples Curvas Elípticas

El sistema ahora soporta múltiples curvas criptográficas estándar:

- **SECP256R1 (NIST P-256)**: Curva estándar usada globalmente para TLS/SSL
  - 256 bits de seguridad
  - Ampliamente adoptada y probada en la industria

- **SECP256K1**: La curva utilizada en Bitcoin y criptomonedas
  - 256 bits de seguridad
  - Óptima para aplicaciones blockchain
  - Compatible con ecosistema cripto

- **SECP384R1 (NIST P-384)**: Mayor seguridad
  - 384 bits de seguridad
  - Recomendada para información clasificada

- **SECP521R1 (NIST P-521)**: Máxima seguridad
  - 521 bits de seguridad
  - Nivel de protección más alto disponible

#### 🔑 Nueva Pestaña: Gestión de Llaves

Interfaz gráfica completa para administrar pares de claves:

- **Selector de Curva**: ComboBox con todas las curvas disponibles y descripciones
- **Generación de Claves**: Genera pares de claves para cualquier curva
- **Protección por Contraseña**: Opción para cifrar claves privadas
- **Visualización de Claves**: Lista todas las claves existentes organizadas por curva
- **Información Contextual**: Muestra descripción detallada de cada curva

#### 🚀 Mejoras en el API

- Nuevo endpoint `/curvas`: Lista todas las curvas disponibles
- Endpoint `/clave-publica/{curva}`: Obtiene clave pública por curva
- Parámetro `curva` en `/notarizar`: Especifica qué curva usar
- Parámetro `curva` en `/verificar`: Verifica con la curva correcta
- Cache de instancias de NotarioCrypto por curva
- Generación automática de claves bajo demanda

### 🔧 Cambios Técnicos

#### Backend (`crypto_utils.py`)
- Clase `NotarioCrypto` acepta parámetro `curva` en constructor
- Diccionario `CURVAS_SOPORTADAS` con metadata de cada curva
- Funciones auxiliares: `obtener_curvas_disponibles()`, `obtener_nombre_curva()`
- Los recibos ahora incluyen campo `curva`

#### API Server (`api_server.py`)
- Sistema de cache para instancias NotarioCrypto por curva
- Función `obtener_notario(curva)` para gestión de instancias
- Función `inicializar_notario_curva()` para inicialización lazy
- Archivos de claves por curva: `notario_private_{curva}.pem`
- Actualización de modelos Pydantic con campo `curva`

#### Cliente GUI (`notario_gui.py`)
- Nueva pestaña "🔑 Gestión de Llaves"
- Variable `curva_seleccionada` para tracking
- Funciones: `generar_claves()`, `listar_claves()`, `on_curva_seleccionada()`
- Actualización de recibos con información de curva
- Mejora en mensajes de verificación mostrando curva usada

#### Script de Generación (`generar_claves.py`)
- Menú interactivo para seleccionar curva
- Nombres de archivo incluyen curva: `notario_private_{curva}.pem`
- Descripción detallada de cada opción de curva

### 📝 Formato de Recibos

Los recibos ahora incluyen el campo `curva`:

```json
{
  "timestamp": "2025-11-19T10:30:00Z",
  "hash": "abc123...",
  "firma": "MEUCIQDx...",
  "curva": "SECP256K1",
  "archivo_original": "documento.pdf"
}
```

### 🔄 Retrocompatibilidad

- Recibos antiguos sin campo `curva` usan SECP256R1 por defecto
- API mantiene compatibilidad con requests sin parámetro `curva`
- Claves antiguas siguen funcionando normalmente

### 📚 Documentación Actualizada

- README actualizado con información de curvas
- Pestaña "Información" en GUI con guía completa
- Ejemplos de uso para cada curva
- Guía de selección de curva según caso de uso

---

## Versión 1.0.0 - Versión Inicial

### Características Base

- Notarización de documentos con ECDSA (SECP256R1)
- Hash SHA-256 de archivos
- Firma digital con timestamp
- Verificación de recibos
- Interfaz gráfica con tkinter
- API REST con FastAPI
- Cliente y servidor independientes
