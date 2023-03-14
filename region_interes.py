import cv2

# Función para actualizar las coordenadas en respuesta a un evento de clic del mouse
def actualizar_coordenadas(event, x, y, flags, param):
    # Actualizar las coordenadas de inicio si se hace clic con el botón izquierdo
    if event == cv2.EVENT_LBUTTONUP:
        param[0] = x
        param[1] = y
    
    # Actualizar las coordenadas de fin si se hace clic con el botón derecho
    elif event == cv2.EVENT_RBUTTONUP:
        param[2] = x
        param[3] = y

# Funcion para marcar la region de interes
def marcar_region_interes(ruta_video):
    # Crear un objeto de captura de video
    video = cv2.VideoCapture(ruta_video)

    # Definir las coordenadas de inicio y fin como pixeles
    coordenadas = [10, 20, 10, 20]

    # Crear la ventana del fotograma y registrar la función de actualización de coordenadas
    cv2.namedWindow('Fotograma')
    cv2.setMouseCallback('Fotograma', actualizar_coordenadas, coordenadas)

    while True:
        # Leer el siguiente fotograma del video
        ret, fotograma = video.read()

        # Salir del ciclo si se llega al final del video
        if not ret:
            break

        # Obtener las coordenadas actualizadas
        inicio_x, inicio_y, fin_x, fin_y = coordenadas

        # Dibujar el rectángulo en el fotograma
        cv2.rectangle(fotograma, (inicio_x, inicio_y), (fin_x, fin_y), (0, 255, 0), 2)

        # Mostrar el fotograma en la ventana
        cv2.imshow('Fotograma', fotograma)

        # Esperar hasta que se presione la tecla 'q'
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break

    # Liberar el objeto de captura de video y cerrar todas las ventanas
    video.release()
    cv2.destroyAllWindows()

    # Devolver las coordenadas de la región de interés
    return inicio_x, inicio_y, fin_x, fin_y