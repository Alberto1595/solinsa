from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime

from extractors.xml import extraer_xml
from extractors.pdf import extraer_pdf
from extractors.imagen import extraer_imagen
from validator import validar_pago

app = FastAPI(
    title="Solinsa — Procesador de Comprobantes",
    description="API para extracción y validación automática de comprobantes de pago",
    version="1.0.0"
)

BITACORA_PATH = "bitacora.json"

EXTENSIONES_PDF    = [".pdf"]
EXTENSIONES_XML    = [".xml"]
EXTENSIONES_IMAGEN = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]


def detectar_tipo(nombre_archivo: str) -> str:
    ext = os.path.splitext(nombre_archivo.lower())[1]
    if ext in EXTENSIONES_PDF:
        return "pdf"
    elif ext in EXTENSIONES_XML:
        return "xml"
    elif ext in EXTENSIONES_IMAGEN:
        return "imagen"
    else:
        return "desconocido"


def registrar_bitacora(entrada: dict):
    bitacora = []

    if os.path.exists(BITACORA_PATH):
        with open(BITACORA_PATH, "r", encoding="utf-8") as f:
            try:
                bitacora = json.load(f)
            except:
                bitacora = []

    bitacora.append(entrada)

    with open(BITACORA_PATH, "w", encoding="utf-8") as f:
        json.dump(bitacora, f, ensure_ascii=False, indent=2, default=str)


@app.post("/procesar-comprobante")
async def procesar_comprobante(archivo: UploadFile = File(...)):
    contenido = await archivo.read()
    nombre = archivo.filename
    tipo = detectar_tipo(nombre)

    # Extracción según tipo
    if tipo == "xml":
        datos = extraer_xml(contenido)
    elif tipo == "pdf":
        datos = extraer_pdf(contenido)
    elif tipo == "imagen":
        datos = extraer_imagen(contenido)
    else:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de archivo no soportado: {nombre}"
        )

    # Verificar si hubo error en extracción
    if "error" in datos:
        entrada_bitacora = {
            "timestamp": datetime.now().isoformat(),
            "archivo": nombre,
            "tipo": tipo,
            "resultado": "error_extraccion",
            "detalle": datos["error"]
        }
        registrar_bitacora(entrada_bitacora)
        return JSONResponse(status_code=422, content={
            "estado": "error_extraccion",
            "archivo": nombre,
            "detalle": datos["error"]
        })

    # Validación contra Excel
    resultado = validar_pago(datos)

    # Registrar en bitácora
    entrada_bitacora = {
        "timestamp": datetime.now().isoformat(),
        "archivo": nombre,
        "tipo": tipo,
        "resultado": resultado["resultado"],
        "accion": resultado["accion"],
        "mensaje": resultado["mensaje"],
        "datos_extraidos": datos
    }
    registrar_bitacora(entrada_bitacora)

    return JSONResponse(content={
        "estado": resultado["resultado"],
        "accion": resultado["accion"],
        "mensaje": resultado["mensaje"],
        "archivo": nombre,
        "datos_extraidos": datos,
        "factura": resultado["factura"]
    })


@app.get("/bitacora")
async def ver_bitacora():
    if not os.path.exists(BITACORA_PATH):
        return JSONResponse(content={"registros": []})

    with open(BITACORA_PATH, "r", encoding="utf-8") as f:
        try:
            bitacora = json.load(f)
        except:
            bitacora = []

    return JSONResponse(content={"total": len(bitacora), "registros": bitacora})


@app.get("/facturas")
async def ver_facturas():
    from validator import cargar_facturas
    facturas = cargar_facturas()
    return JSONResponse(content={"total": len(facturas), "facturas": facturas})


@app.get("/")
async def health_check():
    return {"estado": "activo", "version": "1.0.0"}