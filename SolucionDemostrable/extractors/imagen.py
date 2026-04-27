import pytesseract
from PIL import Image
import io
import re
from extractors.pdf import parsear_texto

def extraer_imagen(contenido: bytes) -> dict:
    try:
        imagen = Image.open(io.BytesIO(contenido))

        # Preprocesamiento básico para mejorar OCR
        imagen = imagen.convert("L")  # escala de grises
        imagen = imagen.point(lambda x: 0 if x < 140 else 255)  # binarización

        # OCR con Tesseract en español
        texto = pytesseract.image_to_string(
            imagen,
            lang="spa",
            config="--psm 6"  # asume bloque de texto uniforme
        )

        if not texto.strip():
            return {
                "error": "No se pudo extraer texto de la imagen",
                "tipo_extraccion": "imagen_ocr"
            }

        resultado = parsear_texto(texto)
        resultado["tipo_extraccion"] = "imagen_ocr"
        resultado["texto_raw"] = texto[:300]  # primeros 300 chars para debug

        return resultado

    except Exception as e:
        return {
            "error": f"No se pudo procesar la imagen: {str(e)}",
            "tipo_extraccion": "imagen_ocr"
        }