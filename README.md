# Automatización de Comprobantes de Pago — Solinsa

Solución desarrollada como parte del proceso de selección para el puesto de **Analista de TI & Automatización Empresarial** en Solinsa.

---

## Problema

El equipo de cobranza de Comercializadora Nexo recibe entre 80 y 120 comprobantes de pago mensuales por correo electrónico, en formatos heterogéneos (PDF, imagen, XML), y los procesa manualmente — consumiendo aproximadamente **30 horas mensuales** con riesgo constante de errores de captura.

---

## Solución

Sistema de automatización end-to-end que detecta correos con comprobantes, extrae los datos clave, los valida contra el registro de facturas pendientes y notifica al equipo únicamente cuando hay una discrepancia que requiere intervención humana.

```
Outlook (buzón compartido)
        ↓
Power Automate — trigger + orquestación
        ↓
FastAPI en Ubuntu local — extracción + validación
        ↓
Excel en SharePoint — actualización automática
        ↓
Microsoft Teams — notificación solo si hay discrepancia
```

---

## Entregables

| Archivo | Descripción |
|---|---|
| `DiagramaDeFlujo.pdf` | Flujo completo del proceso automatizado |
| `explicacion_tecnica_solinsa_v2.pdf` | Arquitectura, decisiones técnicas, deuda técnica y propuesta de evolución |
| `estimado_impacto_solinsa.pdf` | Comparativa de tiempo: 30 hrs → ~1.7 hrs mensuales (~94% reducción) |
| `casos_edge_solinsa.pdf` | 11 casos edge identificados incluyendo detección de comprobantes falsos |
| `SolucionDemostrable/` | Código funcional demostrable con ejemplos de prueba |

---

## Estructura del código

```
SolucionDemostrable/
├── main.py                  # FastAPI — endpoint principal y bitácora
├── validator.py             # Validación contra Excel y actualización de estado
├── generar_datos.py         # Genera el Excel de facturas de prueba
├── requirements.txt         # Dependencias del proyecto
├── facturas.xlsx            # Excel de facturas pendientes (generado)
├── extractors/
│   ├── xml.py               # Parseo CFDI (lxml) — SAT México
│   ├── pdf.py               # Extracción de texto (pdfplumber + regex)
│   └── imagen.py            # OCR (Tesseract + Pillow)
└── ejemplos_prueba/
    ├── factura.xml          # Comprobante XML — coincidencia exacta (TRF-001)
    └── factura_parcial.xml  # Comprobante XML — pago parcial (TRF-002)
```

---

## Instalación y ejecución

### Requisitos previos

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-spa python3-venv
```

### Instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Generar Excel de facturas de prueba
python generar_datos.py
```

### Ejecutar el servidor

```bash
uvicorn main:app --reload --port 8000
```

La documentación interactiva queda disponible en: `http://localhost:8000/docs`

---

## Pruebas con curl

### Comprobante con coincidencia exacta

```bash
curl -X POST http://localhost:8000/procesar-comprobante \
  -F "archivo=@ejemplos_prueba/factura.xml"
```

Respuesta esperada:
```json
{
  "estado": "coincidencia_exacta",
  "accion": "actualizado",
  "mensaje": "Pago correcto. Factura TRF-001 marcada como pagada."
}
```

### Comprobante con pago parcial

```bash
curl -X POST http://localhost:8000/procesar-comprobante \
  -F "archivo=@ejemplos_prueba/factura_parcial.xml"
```

Respuesta esperada:
```json
{
  "estado": "pago_parcial",
  "accion": "escalado",
  "mensaje": "Pago incompleto. Se esperaban $8750.50, se recibieron $8000.00. Diferencia: $750.50"
}
```

### Consultar bitácora

```bash
curl http://localhost:8000/bitacora
```

### Consultar estado de facturas

```bash
curl http://localhost:8000/facturas
```

---

## Decisiones técnicas destacadas

- **Ubuntu Server local** — los comprobantes con datos financieros no salen de la red de la empresa
- **Extracción híbrida** — cada tipo de archivo usa la librería óptima (lxml para XML, pdfplumber para PDF, Tesseract para imágenes)
- **Power Automate como orquestador** — sin costo adicional, incluido en la licencia M365 Business Standard
- **Bitácora persistente** — cada operación queda registrada con timestamp para auditoría

## Propuesta de evolución

| Versión | Almacenamiento | Interfaz de consulta |
|---|---|---|
| V1 — Actual | Excel en SharePoint | Excel |
| V2 — Puente | PostgreSQL + Excel sincronizado | Excel (solo lectura) |
| V3 — Objetivo | PostgreSQL | Power BI o portal web |

---

## Stack tecnológico

`Python 3.12` · `FastAPI` · `lxml` · `pdfplumber` · `Tesseract OCR` · `openpyxl` · `Power Automate` · `Ubuntu Server` · `Microsoft 365`

---

*Desarrollado por Alberto Villarreal — Proceso de selección Solinsa 2026*
