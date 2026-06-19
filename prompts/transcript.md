Necesito que construyas un script Python, NO que lo ejecutes. Tu única
tarea es escribir el archivo y dejarlo listo para que yo lo ejecute
manualmente.

Hacé lo siguiente:

1. Crea la carpeta /scripts/ en la raíz del proyecto si no existe.

2. Dentro de /scripts/, crea el archivo fetch_transcripts.py con el
   siguiente comportamiento:

   a) Lee los Video IDs desde /research/video_ids.json (son IDs limpios
      de 11 caracteres, ya extraídos de URLs).

   b) Usa la librería `youtube-transcript-api`. Incluí en el script un
      comentario al inicio indicando la versión mínima requerida
      (pip install --upgrade youtube-transcript-api) y usá la sintaxis
      correspondiente a la versión más reciente de esa librería.

   c) Para cada video, intenta obtener la transcripción en este orden
      de prioridad:
      - Transcripción manual en inglés ("en")
      - Transcripción auto-generada en inglés ("en", generada por YouTube)
      - Cualquier transcripción disponible traducida automáticamente al inglés
      Si ninguna opción funciona, el script debe capturar el error,
      registrar el video_id y el motivo del fallo, y continuar con
      el siguiente video sin detenerse.

   d) Agrega un delay de 1-2 segundos entre cada request para evitar
      rate limiting de YouTube.

   e) Guarda cada transcripción exitosa como archivo .txt dentro de
      /research/youtube-transcripts/ (el script debe crear esta carpeta
      si no existe), usando el handle correspondiente como nombre de
      archivo (ej: jakewardio.txt).

   f) Al final de la ejecución, el script debe imprimir por consola un
      resumen con este formato exacto:
      ✓ Exitosos: X/10
      ✗ Fallidos: [handle1 (motivo), handle2 (motivo), ...]

3. NO ejecutes el script. NO corras ningún comando python. Tu tarea
   termina al guardar el archivo /scripts/fetch_transcripts.py.

4. Una vez creado el archivo, mostrame:
   - La ruta exacta donde quedó guardado
   - El comando exacto que debo correr yo para ejecutarlo
     (incluyendo instalación de dependencias si falta alguna)
   - Qué resultado debería ver en consola si todo funciona bien

No hagas nada más allá de estos 4 puntos.