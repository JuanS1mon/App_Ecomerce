import fitz  # PyMuPDF

def reemplazar_texto_pdf(ruta_pdf, ruta_pdf_salida, texto_a_reemplazar, nuevo_texto):
    # Abrir el archivo PDF
    documento = fitz.open(ruta_pdf)
    
    # Iterar sobre cada página del PDF
    for pagina_num in range(documento.page_count):
        pagina = documento.load_page(pagina_num)
        areas = pagina.search_for(texto_a_reemplazar)
        
        for area in areas:
            # Obtener las propiedades de la fuente original
            font_size = 12  # Tamaño de fuente por defecto
            font_name = "helv"  # Nombre de fuente por defecto
            text_dict = pagina.get_text("dict")
            for block in text_dict.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if texto_a_reemplazar in span["text"]:
                            font_size = span["size"]
                            font_name = span["font"]
                            break
            
            # Redactar el área con el texto a reemplazar
            pagina.add_redact_annot(area, fill=(1, 1, 1))  # Color blanco
            pagina.apply_redactions()
            
            # Insertar el nuevo texto en la misma posición
            x0, y0, x1, y1 = area
            pagina.insert_text((x0, y0), nuevo_texto, fontsize=font_size, fontname="helv", color=(0, 0, 0))
    
    # Guardar el archivo PDF con el texto reemplazado
    documento.save(ruta_pdf_salida, garbage=4)
    documento.close()

# Ejemplo de uso
ruta_pdf = "sql_app/Services/certificado.pdf"  # Ruta del archivo PDF de entrada
ruta_pdf_salida = "sql_app/Services/editado_certificado.pdf"  # Ruta del archivo PDF de salida
texto_a_reemplazar = "48 hs."
nuevo_texto = "24 hs."

# Reemplazar el texto en el PDF
reemplazar_texto_pdf(ruta_pdf, ruta_pdf_salida, texto_a_reemplazar, nuevo_texto)