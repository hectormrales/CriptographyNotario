"""
Servidor API del Notario Digital.
Proporciona endpoints para notarizar y verificar documentos digitales.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
import sys
from datetime import datetime
import uvicorn

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto


# Modelos de datos
class NotarizarRequest(BaseModel):
    """Request para notarizar un hash."""
    hash: str = Field(..., description="Hash SHA-256 del archivo en formato hexadecimal")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
        }


class NotarizarResponse(BaseModel):
    """Response con el recibo digital."""
    timestamp: str = Field(..., description="Timestamp ISO 8601 de la notarización")
    hash: str = Field(..., description="Hash del archivo notarizado")
    firma: str = Field(..., description="Firma digital en base64")
    mensaje: str = Field(..., description="Mensaje de confirmación")


class VerificarRequest(BaseModel):
    """Request para verificar un recibo."""
    timestamp: str = Field(..., description="Timestamp del recibo")
    hash: str = Field(..., description="Hash del archivo")
    firma: str = Field(..., description="Firma digital en base64")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-10T12:00:00Z",
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "firma": "MEUCIQDx..."
            }
        }


class VerificarResponse(BaseModel):
    """Response de verificación."""
    valido: bool = Field(..., description="Indica si la firma es válida")
    mensaje: str = Field(..., description="Mensaje descriptivo del resultado")
    detalles: Optional[dict] = Field(None, description="Detalles adicionales de la verificación")


class ClavePublicaResponse(BaseModel):
    """Response con la clave pública del notario."""
    clave_publica: str = Field(..., description="Clave pública en formato PEM")


# Inicializar FastAPI
app = FastAPI(
    title="Notario Digital API",
    description="API para notarización y verificación de documentos digitales usando criptografía ECDSA",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde el cliente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del sistema criptográfico
notario = NotarioCrypto()

# Ruta de la clave privada
KEYS_DIR = os.path.join(os.path.dirname(__file__), '..', 'keys')
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, 'notario_private.pem')
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, 'notario_public.pem')


def inicializar_notario(password: Optional[str] = None):
    """
    Inicializa el notario cargando o generando claves.
    
    Args:
        password (str, optional): Contraseña para cifrar/descifrar la clave privada
    """
    os.makedirs(KEYS_DIR, exist_ok=True)
    
    if os.path.exists(PRIVATE_KEY_PATH):
        # Cargar clave existente
        print(f"📂 Cargando clave privada existente desde {PRIVATE_KEY_PATH}")
        try:
            notario.cargar_clave_privada(PRIVATE_KEY_PATH, password)
            print("✅ Clave privada cargada exitosamente")
        except Exception as e:
            print(f"❌ Error cargando clave privada: {e}")
            raise
    else:
        # Generar nuevo par de claves
        print("🔑 Generando nuevo par de claves ECDSA...")
        notario.generar_par_claves()
        notario.guardar_clave_privada(PRIVATE_KEY_PATH, password)
        notario.guardar_clave_publica(PUBLIC_KEY_PATH)
        print(f"✅ Claves generadas y guardadas:")
        print(f"   - Privada: {PRIVATE_KEY_PATH}")
        print(f"   - Pública: {PUBLIC_KEY_PATH}")


@app.on_event("startup")
async def startup_event():
    """Evento de inicio del servidor."""
    print("=" * 60)
    print("🏛️  NOTARIO DIGITAL - Servidor API")
    print("=" * 60)
    
    # Leer contraseña de variable de entorno (opcional)
    password = os.environ.get('NOTARIO_KEY_PASSWORD')
    if password:
        print("🔒 Usando contraseña de variable de entorno")
    
    inicializar_notario(password)
    print("🚀 Servidor listo para recibir solicitudes")
    print("=" * 60)


@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz con información del servicio."""
    return {
        "servicio": "Notario Digital API",
        "version": "1.0.0",
        "descripcion": "Servicio de notarización digital usando criptografía ECDSA",
        "endpoints": {
            "POST /notarizar": "Notariza un hash de archivo",
            "POST /verificar": "Verifica un recibo digital",
            "GET /clave-publica": "Obtiene la clave pública del notario"
        }
    }


@app.get("/clave-publica", response_model=ClavePublicaResponse, tags=["Notario"])
async def obtener_clave_publica():
    """
    Obtiene la clave pública del notario.
    
    Esta clave es necesaria para verificar las firmas digitales.
    """
    try:
        clave_publica_pem = notario.exportar_clave_publica_str()
        return ClavePublicaResponse(clave_publica=clave_publica_pem)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo clave pública: {str(e)}"
        )


@app.post("/notarizar", response_model=NotarizarResponse, tags=["Notario"])
async def notarizar(request: NotarizarRequest):
    """
    Notariza un hash de archivo.
    
    Recibe el hash SHA-256 de un archivo y devuelve un recibo digital firmado
    que incluye el timestamp y la firma ECDSA del notario.
    
    Args:
        request: Solicitud con el hash del archivo
        
    Returns:
        Recibo digital con timestamp y firma
    """
    try:
        # Validar formato del hash (debe ser hexadecimal de 64 caracteres para SHA-256)
        if len(request.hash) != 64 or not all(c in '0123456789abcdefABCDEF' for c in request.hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hash inválido. Debe ser SHA-256 en formato hexadecimal (64 caracteres)"
            )
        
        # Obtener timestamp actual
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Firmar el hash con timestamp
        recibo = notario.firmar_hash(request.hash.lower(), timestamp)
        
        print(f"📝 Hash notarizado: {request.hash[:16]}... en {timestamp}")
        
        return NotarizarResponse(
            timestamp=recibo["timestamp"],
            hash=recibo["hash"],
            firma=recibo["firma"],
            mensaje="Documento notarizado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en notarización: {str(e)}"
        )


@app.post("/verificar", response_model=VerificarResponse, tags=["Notario"])
async def verificar(request: VerificarRequest):
    """
    Verifica la autenticidad de un recibo digital.
    
    Comprueba que la firma del recibo corresponda al hash y timestamp
    usando la clave pública del notario.
    
    Args:
        request: Recibo a verificar
        
    Returns:
        Resultado de la verificación
    """
    try:
        # Preparar recibo para verificación
        recibo = {
            "timestamp": request.timestamp,
            "hash": request.hash.lower(),
            "firma": request.firma
        }
        
        # Verificar la firma
        es_valido = notario.verificar_firma(recibo)
        
        if es_valido:
            print(f"✅ Recibo verificado: {request.hash[:16]}... - {request.timestamp}")
            return VerificarResponse(
                valido=True,
                mensaje="El recibo es auténtico y válido",
                detalles={
                    "timestamp": request.timestamp,
                    "hash": request.hash
                }
            )
        else:
            print(f"❌ Recibo inválido: {request.hash[:16]}...")
            return VerificarResponse(
                valido=False,
                mensaje="El recibo NO es válido. La firma no corresponde o ha sido alterado",
                detalles={
                    "timestamp": request.timestamp,
                    "hash": request.hash
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en verificación: {str(e)}"
        )


@app.get("/health", tags=["Info"])
async def health_check():
    """Verifica el estado del servidor."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "clave_publica_disponible": notario.public_key is not None
    }


if __name__ == "__main__":
    # Configuración del servidor
    print("\n🚀 Iniciando servidor Notario Digital...\n")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
