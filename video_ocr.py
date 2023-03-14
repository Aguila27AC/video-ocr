import re
import cv2
import pytesseract
from datetime import datetime, timedelta
import region_interes as ri
from googletrans import Translator

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def extraer_subtitulos(ruta_video, salto_fotograma, marcar_region_interes):

    if marcar_region_interes:
        inicio_x, inicio_y, fin_x, fin_y = ri.marcar_region_interes(ruta_video)
        print([inicio_x, inicio_y, fin_x, fin_y])
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
            texto = pytesseract.image_to_string(region_interes, lang='eng')

            texto = texto.replace("\n", " ").strip()

            # Mostrar el texto en la consola
            print(str(numero_fotograma) + ": " + texto)

            subtitulos.append([numero_fotograma, numero_fotograma, texto])

            numero_fotograma += 1

        # Aumentar contador
        contador_fotogramas += 1

    return subtitulos, fps

def simplificar_subtitulos(subtitulos):
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
    
    return subtitulos

def calcular_tiempo_subtitulos(subtitulos, fps, salto_fotograma):
    fps = fps / salto_fotograma

    for subtitulo in subtitulos:
        # Calcular el tiempo de inicio y finalización de cada fotograma
        subtitulo[0] = datetime.min + timedelta(seconds=subtitulo[0] / fps)
        subtitulo[1] = datetime.min + timedelta(seconds=((subtitulo[1]) + 1) / fps)

    return subtitulos

def traducir_subtitulos(subtitulos):    

    traductor = Translator()

    for subtitulo in subtitulos:
        texto_traducido = traductor.translate(text=subtitulo[2], src='en', dest='es').text
        subtitulo[2] = texto_traducido

    return subtitulos

def subtitulos_a_txt(subtitulos, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for subtitulo in subtitulos:
            archivo.write(f"{subtitulo[0]}-{subtitulo[1]}: {subtitulo[2]}\n")

def subtitulos_a_srt(subtitulos, nombre_archivo):
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

titulo = "death"

salto_fotograma = 30

subtitulos, fps = extraer_subtitulos(titulo + ".mp4", salto_fotograma, False)

subtitulos_a_txt(subtitulos, titulo + "_raw_subtitle_30.txt")

#subtitulos_a_srt(simplificar_subtitulos(calcular_tiempo_subtitulos(subtitulos, fps, salto_fotograma)), titulo + ".en.srt")

subtitulos_a_srt(traducir_subtitulos(simplificar_subtitulos(calcular_tiempo_subtitulos(subtitulos, fps, salto_fotograma))), titulo + ".es.srt")