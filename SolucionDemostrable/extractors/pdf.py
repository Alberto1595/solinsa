import pdfplumber
import re
import io

def extraer_pdf(contenido: bytes) -> dict:
    try:
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""

        if not texto.strip():
            return {
                "error": "PDF sin texto extraíble, posiblemente es imagen escaneada",
                "tipo_extraccion": "pdf"
            }

        return parsear_texto(texto)

    except Exception as e:
        return {
            "error": f"No se pudo leer el PDF: {str(e)}",
            "tipo_extraccion": "pdf"
        }


def parsear_texto(texto: str) -> dict:
    texto_lower = texto.lower()

    # Monto
    monto = None
    patrones_monto = [
        r"total\s*[:\$]?\s*([\d,]+\.?\d*)",
        r"importe\s*[:\$]?\s*([\d,]+\.?\d*)",
        r"monto\s*[:\$]?\s*([\d,]+\.?\d*)",
        r"\$\s*([\d,]+\.?\d+)",
    ]
    for patron in patrones_monto:
        match = re.search(patron, texto_lower)
        if match:
            monto_str = match.group(1).replace(",", "")
            try:
                monto = float(monto_str)
                break
            except:
                continue

    # Fecha
    fecha = None
    patrones_fecha = [
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}-\d{2}-\d{4})",
    ]
    for patron in patrones_fecha:
        match = re.search(patron, texto)
        if match:
            fecha = match.group(1)
            break

    # Referencia
    referencia = None
    patrones_ref = [
        r"referencia\s*[:\#]?\s*([A-Z0-9\-]+)",
        r"concepto\s*[:\#]?\s*([A-Z0-9\-]+)",
        r"clave\s*[:\#]?\s*([A-Z0-9\-]+)",
        r"folio\s*[:\#]?\s*([A-Z0-9\-]+)",
    ]
    for patron in patrones_ref:
        match = re.search(patron, texto_lower)
        if match:
            referencia = match.group(1).upper()
            break

    # Pagador
    pagador = None
    patrones_pagador = [
        r"ordenante[:\s]+(.+)",
        r"nombre[:\s]+(.+)",
        r"empresa[:\s]+(.+)",
        r"raz[oó]n social[:\s]+(.+)",
    ]
    for patron in patrones_pagador:
        match = re.search(patron, texto_lower)
        if match:
            pagador = match.group(1).strip().title()[:60]
            break

    return {
        "pagador": pagador or "No identificado",
        "monto": monto or 0.0,
        "fecha": fecha or "No identificada",
        "referencia": referencia or "No identificada",
        "tipo_extraccion": "pdf"
    }