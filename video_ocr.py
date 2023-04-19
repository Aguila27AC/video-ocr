import argparse
import os
import re
import cv2
import pytesseract
import easyocr
from datetime import datetime, timedelta
import region_interes as ri
from googletrans import Translator

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def extraer_subtitulos_easyocr(ruta_video, salto_fotograma, marcar_region_interes):

    print(f"[ ] Extrayendo subtitulos...", end="\r")

    if marcar_region_interes:
        inicio_x, inicio_y, fin_x, fin_y = ri.marcar_region_interes(ruta_video)
        print("Coordenadas: " + str([inicio_x, inicio_y, fin_x, fin_y]) + "\n")
    else:
        inicio_x, inicio_y, fin_x, fin_y = [300, 905, 1620, 1045]

    if inicio_x > fin_x:
        inicio_x, fin_x = fin_x, inicio_x

    if inicio_y > fin_y:
        inicio_y, fin_y = fin_y, inicio_y

    reader = easyocr.Reader(model_storage_directory="english_g2", lang_list=["en"], gpu=True)

    # Abrir el video
    video = cv2.VideoCapture(ruta_video)

    # Obtener la tasa de fotogramas por segundo
    fps = video.get(cv2.CAP_PROP_FPS)

    # Obtiene el número total de fotogramas
    total_fotogramas = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    total_fotogramas = int(total_fotogramas/salto_fotograma)

    #Crear lista_fotograma_texto
    subtitulos = []

    numero_fotograma = 1
    contador_fotogramas = 1

    while True:
        # Leer el siguiente fotograma del video
        ret, fotograma = video.read()

        # Salir del ciclo si se llega al final del video
        if not ret:
            break

        if contador_fotogramas%salto_fotograma == 0:
            # Recortar la región de interés del fotograma
            region_interes = fotograma[inicio_y:fin_y, inicio_x:fin_x]

            # Convertir la región de interés a escala de grises
            region_interes_gris = cv2.cvtColor(region_interes, cv2.COLOR_BGR2GRAY)

            # Aplicar OCR al fotograma
            texto = " ".join(reader.readtext(region_interes_gris, detail=0, paragraph=True))

            texto = texto.replace("\n", " ").strip()

            subtitulos.append([numero_fotograma, numero_fotograma, texto])

            # Mostrar el texto en la consola
            print(f"[ ] Extrayendo subtitulos... Fotogramas leidos: {numero_fotograma}/{total_fotogramas}", end="\r")

            numero_fotograma += 1

        # Aumentar contador
        contador_fotogramas += 1
    
    print(f"[x] Extrayendo subtitulos: Completado")

    return subtitulos, fps

def extraer_subtitulos_tesseract(ruta_video, salto_fotograma, marcar_region_interes):

    print(f"[ ] Extrayendo subtitulos...", end="\r")

    if marcar_region_interes:
        inicio_x, inicio_y, fin_x, fin_y = ri.marcar_region_interes(ruta_video)
        #print([inicio_x, inicio_y, fin_x, fin_y])
    else:
        inicio_x, inicio_y, fin_x, fin_y = [346, 906, 1460, 1053]

    if inicio_x > fin_x:
        inicio_x, fin_x = fin_x, inicio_x

    if inicio_y > fin_y:
        inicio_y, fin_y = fin_y, inicio_y

    # Abrir el video
    video = cv2.VideoCapture(ruta_video)

    # Obtener la tasa de fotogramas por segundo
    fps = video.get(cv2.CAP_PROP_FPS)

    # Obtiene el número total de fotogramas
    total_fotogramas = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    total_fotogramas = int(total_fotogramas/salto_fotograma)

    #Crear lista_fotograma_texto
    subtitulos = []

    numero_fotograma = 1
    contador_fotogramas = 1

    while True:
        # Leer el siguiente fotograma del video
        ret, fotograma = video.read()

        # Salir del ciclo si se llega al final del video
        if not ret:
            break

        if contador_fotogramas%salto_fotograma == 0:
            # Recortar la región de interés del fotograma
            region_interes = fotograma[inicio_y:fin_y, inicio_x:fin_x]

            # Convertir la región de interés a escala de grises
            #region_interes_gris = cv2.cvtColor(region_interes, cv2.COLOR_BGR2GRAY)

            # Aplicar OCR al fotograma
            texto = pytesseract.image_to_string(region_interes, lang='eng', config='-c tessedit_char_blacklist=~|_')

            texto = texto.replace("\n", " ").strip()

            subtitulos.append([numero_fotograma, numero_fotograma, texto])

            # Mostrar el texto en la consola
            print(f"[ ] Extrayendo subtitulos... Fotogramas leidos: {numero_fotograma}/{total_fotogramas}", end="\r")

            numero_fotograma += 1

        # Aumentar contador
        contador_fotogramas += 1
    
    print(f"[x] Extrayendo subtitulos: Completado")

    return subtitulos, fps

def simplificar_subtitulos(subtitulos):
    print(f"[ ] Simplificando subtitulos...", end="\r")

    i = len(subtitulos) - 1
    while i > -1:
        fotograma_inicio, fotograma_final, texto = subtitulos[i]
        fotograma_inicio_ant, fotograma_final_ant, texto_ant = subtitulos[i-1]

        if not texto:
            subtitulos.remove(subtitulos[i])
        elif texto == texto_ant:
            subtitulos.remove(subtitulos[i])
            subtitulos[i-1][1] = fotograma_final
        elif texto_ant and texto.startswith(texto_ant):
            subtitulos.remove(subtitulos[i])
            subtitulos[i-1][1] = fotograma_final
            subtitulos[i-1][2] = texto
        elif texto_ant and len(texto)>2 and texto.startswith(texto_ant[:-1]):
            subtitulos.remove(subtitulos[i])
            subtitulos[i-1][1] = fotograma_final
            subtitulos[i-1][2] = texto

        i -= 1
    
    print(f"[x] Simplificando subtitulos: Completado")
    
    return subtitulos

def calcular_tiempo_subtitulos(subtitulos, fps, salto_fotograma):
    print(f"[ ] Calculando tiempo subtitulos...", end="\r")

    fps = fps / salto_fotograma

    for subtitulo in subtitulos:
        # Calcular el tiempo de inicio y finalización de cada fotograma
        subtitulo[0] = datetime.min + timedelta(seconds=subtitulo[0] / fps)
        subtitulo[1] = datetime.min + timedelta(seconds=((subtitulo[1]) + 1) / fps)

    print(f"[x] Calculando tiempo subtitulos: Completado")

    return subtitulos

def traducir_subtitulos(subtitulos):
    print(f"[ ] Traduciendo subtitulos...", end='\r')

    traductor = Translator()

    for subtitulo in subtitulos:
        texto_traducido = traductor.translate(text=subtitulo[2], src='en', dest='es').text
        subtitulo[2] = texto_traducido

    print(f"[x] Traduciendo subtitulos: Completado")

    return subtitulos

def subtitulos_a_txt(subtitulos, nombre_archivo):
    print(f"[ ] Guardando a txt...", end='\r')

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for subtitulo in subtitulos:
            archivo.write(f"{subtitulo[0]}-{subtitulo[1]}: {subtitulo[2]}\n")

    print(f"[x] Guardando a txt: Completado")

def subtitulos_a_srt(subtitulos, nombre_archivo):
    print(f"[ ] Guardando a srt...", end='\r')

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        i = 1
        for subtitulo in subtitulos:
            # Escribir el número de subtítulo
            archivo.write(f"{i}\n")

            # Escribir el tiempo de inicio y finalización
            archivo.write(f"{subtitulo[0].strftime('%H:%M:%S,%f')[:-3]} --> {subtitulo[1].strftime('%H:%M:%S,%f')[:-3]}\n")

            # Escribir el texto del subtítulo
            archivo.write(f"{subtitulo[2]}\n\n")

            i += 1

    print(f"[x] Guardando a srt: Completado")

def subtitulos_desde_txt(nombre_archivo):
    # Abre el archivo txt y lee cada línea
    with open("death_s_raw_subtitle_30.txt", "r", encoding="utf-8") as file:
        # Lee todas las líneas del archivo
        lines = file.readlines()

    # Crea una lista para almacenar los números y los textos
    subtitulos = []

    # Itera sobre cada línea
    for line in lines:
        # Busca el número y el texto usando expresiones regulares
        match = re.search(r"^(\d+)-\d+: (.+)", line)
        if match:
            # Si se encontró una coincidencia, agrega el número y el texto a la lista
            number = match.group(1)
            text = match.group(2)
            subtitulos.append([number, number, text])

    return subtitulos

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ruta_video", help="Ruta del archivo de video")
    parser.add_argument("salto_fotograma", type=int, help="Salto fotograma")
    parser.add_argument("--region", help="Marcar region interes", action="store_true")
    parser.add_argument("--traducir", help="Traducir subtitulos", action="store_true")

    args = parser.parse_args()

    ruta_video = args.ruta_video
    salto_fotograma = args.salto_fotograma
    marcar_region_interes = args.region
    traducir = args.traducir

    if not ruta_video or not salto_fotograma:
        print("Faltan parámetros necesarios")
    else:
        subtitulos, fps = extraer_subtitulos_easyocr(ruta_video, salto_fotograma, marcar_region_interes)

        ruta_video_sin_extension = os.path.splitext(os.path.basename(ruta_video))[0]

        subtitulos_a_txt(subtitulos, ruta_video_sin_extension + "_raw_subtitle_" + str(salto_fotograma) + ".txt")

        subtitulos = simplificar_subtitulos(subtitulos)

        subtitulos_a_txt(subtitulos, ruta_video_sin_extension + "_raw_s_subtitle_" + str(salto_fotograma) + ".txt")

        calcular_tiempo_subtitulos(subtitulos, fps, salto_fotograma)

        subtitulos_a_srt(subtitulos, ruta_video_sin_extension + "_" + str(salto_fotograma) + ".en.srt")

        if traducir:
            subtitulos_a_srt(traducir_subtitulos(subtitulos), ruta_video_sin_extension + "_" + str(salto_fotograma) + ".es.srt")
