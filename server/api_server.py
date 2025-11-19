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
from shared.crypto_utils import NotarioCrypto, CURVAS_SOPORTADAS


# Modelos de datos
class NotarizarRequest(BaseModel):
    """Request para notarizar un hash."""
    hash: str = Field(..., description="Hash SHA-256 del archivo en formato hexadecimal")
    curva: Optional[str] = Field("SECP256R1", description="Curva elíptica a utilizar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "curva": "SECP256R1"
            }
        }


class NotarizarResponse(BaseModel):
    """Response con el recibo digital."""
    timestamp: str = Field(..., description="Timestamp ISO 8601 de la notarización")
    hash: str = Field(..., description="Hash del archivo notarizado")
    firma: str = Field(..., description="Firma digital en base64")
    curva: str = Field(..., description="Curva elíptica utilizada")
    mensaje: str = Field(..., description="Mensaje de confirmación")


class VerificarRequest(BaseModel):
    """Request para verificar un recibo."""
    timestamp: str = Field(..., description="Timestamp del recibo")
    hash: str = Field(..., description="Hash del archivo")
    firma: str = Field(..., description="Firma digital en base64")
    curva: Optional[str] = Field("SECP256R1", description="Curva elíptica utilizada")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-10T12:00:00Z",
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "firma": "MEUCIQDx...",
                "curva": "SECP256R1"
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
    curva: str = Field(..., description="Curva elíptica de la clave")


class CurvasResponse(BaseModel):
    """Response con las curvas disponibles."""
    curvas: dict = Field(..., description="Diccionario de curvas soportadas")


# Inicializar FastAPI
app = FastAPI(
    title="Notario Digital API",
    description="API para notarización y verificación de documentos digitales usando criptografía ECDSA con múltiples curvas",
    version="2.0.0"
)

# Configurar CORS para permitir conexiones desde el cliente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del sistema criptográfico (por defecto SECP256R1)
notario_instances = {}  # Cache de instancias por curva

# Ruta de la clave privada
KEYS_DIR = os.path.join(os.path.dirname(__file__), '..', 'keys')


def obtener_notario(curva: str = "SECP256R1") -> NotarioCrypto:
    """
    Obtiene o crea una instancia de NotarioCrypto para una curva específica.
    
    Args:
        curva (str): Nombre de la curva
        
    Returns:
        NotarioCrypto: Instancia configurada con la curva
    """
    if curva not in CURVAS_SOPORTADAS:
        raise ValueError(f"Curva no soportada: {curva}")
    
    if curva not in notario_instances:
        notario_instances[curva] = NotarioCrypto(curva=curva)
        inicializar_notario_curva(curva)
    
    return notario_instances[curva]


def inicializar_notario_curva(curva: str, password: Optional[str] = None):
    """
    Inicializa el notario para una curva específica cargando o generando claves.
    
    Args:
        curva (str): Nombre de la curva
        password (str, optional): Contraseña para cifrar/descifrar la clave privada
    """
    os.makedirs(KEYS_DIR, exist_ok=True)
    
    private_key_path = os.path.join(KEYS_DIR, f'notario_private_{curva.lower()}.pem')
    public_key_path = os.path.join(KEYS_DIR, f'notario_public_{curva.lower()}.pem')
    
    notario = notario_instances[curva]
    
    if os.path.exists(private_key_path):
        # Cargar clave existente
        print(f"📂 Cargando clave privada {curva} desde {private_key_path}")
        try:
            notario.cargar_clave_privada(private_key_path, password)
            print(f"✅ Clave privada {curva} cargada exitosamente")
        except Exception as e:
            print(f"❌ Error cargando clave privada {curva}: {e}")
            raise
    else:
        # Generar nuevo par de claves
        print(f"🔑 Generando nuevo par de claves {curva}...")
        notario.generar_par_claves()
        notario.guardar_clave_privada(private_key_path, password)
        notario.guardar_clave_publica(public_key_path)
        print(f"✅ Claves {curva} generadas y guardadas:")
        print(f"   - Privada: {private_key_path}")
        print(f"   - Pública: {public_key_path}")


@app.on_event("startup")
async def startup_event():
    """Evento de inicio del servidor."""
    print("=" * 60)
    print("🏛️  NOTARIO DIGITAL - Servidor API v2.0")
    print("=" * 60)
    
    # Leer contraseña de variable de entorno (opcional)
    password = os.environ.get('NOTARIO_KEY_PASSWORD')
    if password:
        print("🔒 Usando contraseña de variable de entorno")
    
    # Inicializar con curva por defecto
    print(f"Inicializando curva por defecto: SECP256R1")
    obtener_notario("SECP256R1")
    
    print("🚀 Servidor listo para recibir solicitudes")
    print(f"📋 Curvas disponibles: {', '.join(CURVAS_SOPORTADAS.keys())}")
    print("=" * 60)


@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz con información del servicio."""
    return {
        "servicio": "Notario Digital API",
        "version": "2.0.0",
        "descripcion": "Servicio de notarización digital usando criptografía ECDSA con múltiples curvas",
        "curvas_soportadas": list(CURVAS_SOPORTADAS.keys()),
        "endpoints": {
            "POST /notarizar": "Notariza un hash de archivo",
            "POST /verificar": "Verifica un recibo digital",
            "GET /clave-publica/{curva}": "Obtiene la clave pública del notario para una curva",
            "GET /curvas": "Lista todas las curvas disponibles"
        }
    }


@app.get("/curvas", response_model=CurvasResponse, tags=["Info"])
async def obtener_curvas():
    """
    Obtiene la lista de curvas elípticas soportadas.
    
    Returns:
        Diccionario con información de todas las curvas disponibles
    """
    return CurvasResponse(curvas=CURVAS_SOPORTADAS)


@app.get("/clave-publica/{curva}", response_model=ClavePublicaResponse, tags=["Notario"])
async def obtener_clave_publica(curva: str = "SECP256R1"):
    """
    Obtiene la clave pública del notario para una curva específica.
    
    Esta clave es necesaria para verificar las firmas digitales.
    
    Args:
        curva: Nombre de la curva elíptica
    """
    try:
        if curva not in CURVAS_SOPORTADAS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Curva no soportada: {curva}. Curvas disponibles: {list(CURVAS_SOPORTADAS.keys())}"
            )
        
        notario = obtener_notario(curva)
        clave_publica_pem = notario.exportar_clave_publica_str()
        return ClavePublicaResponse(clave_publica=clave_publica_pem, curva=curva)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo clave pública: {str(e)}"
        )


@app.post("/notarizar", response_model=NotarizarResponse, tags=["Notario"])
async def notarizar(request: NotarizarRequest):
    """
    Notariza un hash de archivo usando una curva específica.
    
    Recibe el hash SHA-256 de un archivo y devuelve un recibo digital firmado
    que incluye el timestamp y la firma ECDSA del notario.
    
    Args:
        request: Solicitud con el hash del archivo y la curva
        
    Returns:
        Recibo digital con timestamp, firma y curva utilizada
    """
    try:
        # Validar curva
        curva = request.curva or "SECP256R1"
        if curva not in CURVAS_SOPORTADAS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Curva no soportada: {curva}. Curvas disponibles: {list(CURVAS_SOPORTADAS.keys())}"
            )
        
        # Validar formato del hash (debe ser hexadecimal de 64 caracteres para SHA-256)
        if len(request.hash) != 64 or not all(c in '0123456789abcdefABCDEF' for c in request.hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hash inválido. Debe ser SHA-256 en formato hexadecimal (64 caracteres)"
            )
        
        # Obtener notario para la curva
        notario = obtener_notario(curva)
        
        # Obtener timestamp actual
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Firmar el hash con timestamp
        recibo = notario.firmar_hash(request.hash.lower(), timestamp)
        
        print(f"📝 Hash notarizado con {curva}: {request.hash[:16]}... en {timestamp}")
        
        return NotarizarResponse(
            timestamp=recibo["timestamp"],
            hash=recibo["hash"],
            firma=recibo["firma"],
            curva=recibo["curva"],
            mensaje=f"Documento notarizado exitosamente usando {curva}"
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
    usando la clave pública del notario para la curva especificada.
    
    Args:
        request: Recibo a verificar
        
    Returns:
        Resultado de la verificación
    """
    try:
        # Determinar curva (del request o por defecto)
        curva = request.curva or "SECP256R1"
        
        if curva not in CURVAS_SOPORTADAS:
            return VerificarResponse(
                valido=False,
                mensaje=f"Curva no soportada: {curva}",
                detalles={"curva": curva}
            )
        
        # Obtener notario para la curva
        notario = obtener_notario(curva)
        
        # Preparar recibo para verificación
        recibo = {
            "timestamp": request.timestamp,
            "hash": request.hash.lower(),
            "firma": request.firma,
            "curva": curva
        }
        
        # Verificar la firma
        es_valido = notario.verificar_firma(recibo)
        
        if es_valido:
            print(f"✅ Recibo verificado ({curva}): {request.hash[:16]}... - {request.timestamp}")
            return VerificarResponse(
                valido=True,
                mensaje=f"El recibo es auténtico y válido (curva: {curva})",
                detalles={
                    "timestamp": request.timestamp,
                    "hash": request.hash,
                    "curva": curva
                }
            )
        else:
            print(f"❌ Recibo inválido ({curva}): {request.hash[:16]}...")
            return VerificarResponse(
                valido=False,
                mensaje=f"El recibo NO es válido. La firma no corresponde o ha sido alterado (curva: {curva})",
                detalles={
                    "timestamp": request.timestamp,
                    "hash": request.hash,
                    "curva": curva
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
    claves_disponibles = {}
    for curva in notario_instances.keys():
        claves_disponibles[curva] = notario_instances[curva].public_key is not None
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "curvas_inicializadas": list(notario_instances.keys()),
        "claves_disponibles": claves_disponibles
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
