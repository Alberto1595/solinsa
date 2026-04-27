import lxml.etree as ET

CFDI_NS = "http://www.sat.gob.mx/cfd/4"
CFDI_NS3 = "http://www.sat.gob.mx/cfd/3"

def extraer_xml(contenido: bytes) -> dict:
    try:
        root = ET.fromstring(contenido)
        
        # Detectar namespace version 3 o 4
        ns = CFDI_NS if CFDI_NS in root.nsmap.values() else CFDI_NS3
        
        # Extraer atributos del comprobante
        monto = root.get("Total") or root.get("total")
        fecha = root.get("Fecha") or root.get("fecha")
        folio = root.get("Folio") or root.get("folio") or root.get("NoCertificado", "SIN_FOLIO")
        serie = root.get("Serie") or ""
        referencia = f"{serie}-{folio}".strip("-")

        # Extraer receptor (quien paga)
        receptor = root.find(f"{{{ns}}}Receptor")
        if receptor is None:
            receptor = root.find("Receptor")
        
        pagador = receptor.get("Nombre") if receptor is not None else "Desconocido"
        rfc = receptor.get("Rfc") if receptor is not None else "Desconocido"

        return {
            "pagador": pagador,
            "rfc": rfc,
            "monto": float(monto) if monto else 0.0,
            "fecha": fecha,
            "referencia": referencia,
            "tipo_extraccion": "xml"
        }

    except Exception as e:
        return {
            "error": f"No se pudo parsear el XML: {str(e)}",
            "tipo_extraccion": "xml"
        }