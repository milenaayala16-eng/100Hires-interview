Actúa como un ingeniero de datos. Tengo una lista de 10 URLs de perfiles
de LinkedIn y necesito extraer sus 3 posts más recientes (texto + fecha
de publicación) para un proyecto de investigación.

RESTRICCIÓN CRÍTICA: NO uses Playwright, Puppeteer ni la herramienta de
navegación nativa. Vamos a usar la API de Apify, que corre el scraping
en su infraestructura y evita el riesgo de bloqueo de mi cuenta personal.

Hacé lo siguiente:

1. Crea la carpeta /research/linkedin-posts/ si no existe.

2. Escribe un script Python llamado fetch_linkedin.py que:
   - Lea el token de Apify desde una variable de entorno APIFY_API_TOKEN
   - Use el actor de Apify "apimaestro/linkedin-profile-posts" (o el
     actor equivalente más actualizado que encuentres en el Apify Store
     para "linkedin posts scraper") vía su API REST
     (https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items)
   - Itere sobre esta lista de perfiles de linkedin seleccionadas:
     del archivo research/sources.md
   - Para cada perfil, solicite los 3 posts más recientes
   - Extraiga de cada post: texto completo y fecha de publicación

3. El script debe guardar cada perfil como un archivo .txt separado en
   /research/linkedin-posts/ con formato nombre-apellido.txt, así:

   POST 1 — [fecha]
   [texto del post]

   POST 2 — [fecha]
   [texto del post]

   POST 3 — [fecha]
   [texto del post]

4. Agregá manejo de errores: si un perfil falla (privado, URL inválida,
   sin posts), que el script lo loguee en consola y continúe con el
   siguiente sin detenerse.

5. Antes de ejecutar el script completo, corré una prueba con 1 sola URL
   para confirmar que el actor de Apify devuelve los campos correctos
   (texto y fecha). Mostrame el JSON crudo de esa prueba antes de
   procesar las 10 URLs completas, así verifico el formato.

6. Una vez confirmado el formato, ejecutá el script con las 10 URLs.

7. El script debe minimar el uso de la api de Apify. Considera que las URLs son de perfiles de linkedin seleccionadas, lo que significa que los 3 posts mas recientes de cada perfil pueden ser muy recientes y no es necesario usar la api de Apify para obtenerlos. Analiza la mejor manera de obtener los 3 posts mas recientes de cada perfil con el menor uso de la api de Apify. 