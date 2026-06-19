# fetch_transcripts.py
#
# Requiere: youtube-transcript-api >= 0.6.0
# Instalar/actualizar con:
#   pip install --upgrade youtube-transcript-api
#
# Compatibilidad: este script usa la API de la versión 0.6.x en adelante
# (YouTubeTranscriptApi.get_transcript con lista de idiomas y
# FetchedTranscript.to_raw_data() para serializar el texto).

import json
import os
import re
import time
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Importar librería principal
# ---------------------------------------------------------------------------
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    raise SystemExit(
        "ERROR: youtube-transcript-api no está instalado.\n"
        "Ejecutá:  uv pip install youtube-transcript-api"
    )

# Importar excepciones específicas con fallback graceful.
# La v1.x reorganizó algunos nombres; usamos Exception como respaldo
# para que el script funcione independientemente de la versión.
try:
    from youtube_transcript_api._errors import TranscriptsDisabled
except ImportError:
    TranscriptsDisabled = Exception

try:
    from youtube_transcript_api._errors import NoTranscriptFound
except ImportError:
    NoTranscriptFound = Exception

try:
    from youtube_transcript_api._errors import VideoUnavailable
except ImportError:
    VideoUnavailable = Exception

try:
    from youtube_transcript_api._errors import TooManyRequests
except ImportError:
    try:
        from youtube_transcript_api._errors import RequestBlocked
        TooManyRequests = RequestBlocked
    except ImportError:
        TooManyRequests = Exception

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEO_IDS_FILE = REPO_ROOT / "research" / "video_ids.json"
OUTPUT_DIR = REPO_ROOT / "research" / "youtube-transcripts"


def extract_video_id(url_or_id: str) -> str:
    """
    Acepta una URL de YouTube en cualquier formato, o bien un ID limpio
    de 11 caracteres, y devuelve solo el video_id.

    Formatos soportados:
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtube.com/shorts/VIDEO_ID
      - VIDEO_ID  (directamente)
    """
    url_or_id = url_or_id.strip()

    # Si ya parece un ID limpio (solo caracteres válidos, longitud 11)
    if re.fullmatch(r"[A-Za-z0-9_\-]{11}", url_or_id):
        return url_or_id

    # Intentar extraer de URL
    patterns = [
        r"youtu\.be/([A-Za-z0-9_\-]{11})",
        r"youtube\.com/watch\?.*v=([A-Za-z0-9_\-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_\-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_\-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Si nada matchea, devolver tal cual (el error se captura más adelante)
    return url_or_id


def fetch_transcript(video_id: str) -> str:
    """
    Intenta obtener la transcripción en este orden de prioridad:
      1. Transcripción manual en inglés ("en")
      2. Transcripción auto-generada en inglés
      3. Cualquier transcripción disponible, traducida al inglés

    Devuelve el texto completo como string.
    Lanza excepción si ninguna opción funciona.
    """
    ytt = YouTubeTranscriptApi()

    # Paso 1 y 2: manual primero, luego auto-generada (ambas "en")
    # get_transcript prioriza manuales sobre auto-generadas si se pasa la
    # lista de idiomas en orden; internamente busca el primero disponible.
    try:
        transcript = ytt.fetch(video_id, languages=["en"])
        return transcript_to_text(transcript)
    except NoTranscriptFound:
        pass  # Ninguna transcripción "en" encontrada → intentar traducción

    # Paso 3: listar todas las disponibles y traducir al inglés
    try:
        transcript_list = ytt.list(video_id)
        # Intentar traducir al inglés la primera transcripción disponible
        transcript = transcript_list.find_transcript(
            [t.language_code for t in transcript_list]
        )
        translated = transcript.translate("en")
        return transcript_to_text(translated.fetch())
    except Exception:
        raise  # Re-lanza para que el caller registre el error


def transcript_to_text(transcript) -> str:
    """
    Convierte un objeto FetchedTranscript (o lista de snippets) a texto plano.
    Cada snippet tiene los campos 'text', 'start', 'duration'.
    """
    # FetchedTranscript es iterable y cada elemento tiene .text
    lines = []
    for snippet in transcript:
        text = snippet.get("text", "").strip() if isinstance(snippet, dict) else snippet.text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def main():
    # -----------------------------------------------------------------------
    # Cargar video IDs
    # -----------------------------------------------------------------------
    if not VIDEO_IDS_FILE.exists():
        raise SystemExit(f"ERROR: No se encontró el archivo de IDs: {VIDEO_IDS_FILE}")

    with open(VIDEO_IDS_FILE, encoding="utf-8") as f:
        raw_entries = json.load(f)

    if not isinstance(raw_entries, list) or len(raw_entries) == 0:
        raise SystemExit("ERROR: video_ids.json está vacío o no tiene formato de lista.")

    # Extraer IDs limpios (el archivo puede contener URLs o IDs directos)
    entries = [extract_video_id(entry) for entry in raw_entries]
    total = len(entries)

    # -----------------------------------------------------------------------
    # Crear carpeta de salida
    # -----------------------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Procesar cada video
    # -----------------------------------------------------------------------
    successes = 0
    failures = []  # lista de (video_id, motivo)

    for idx, video_id in enumerate(entries, start=1):
        print(f"[{idx}/{total}] Procesando: {video_id} ...", end=" ", flush=True)

        try:
            text = fetch_transcript(video_id)
            out_file = OUTPUT_DIR / f"{video_id}.txt"
            out_file.write_text(text, encoding="utf-8")
            print(f"✓ guardado ({len(text)} chars)")
            successes += 1

        except TranscriptsDisabled:
            reason = "transcripciones deshabilitadas"
            print(f"✗ {reason}")
            failures.append((video_id, reason))

        except VideoUnavailable:
            reason = "video no disponible"
            print(f"✗ {reason}")
            failures.append((video_id, reason))

        except TooManyRequests:
            reason = "demasiadas solicitudes (rate limit)"
            print(f"✗ {reason}")
            failures.append((video_id, reason))

        except NoTranscriptFound:
            reason = "sin transcripción disponible en ningún idioma"
            print(f"✗ {reason}")
            failures.append((video_id, reason))

        except Exception as e:
            reason = str(e)[:120]  # truncar mensajes muy largos
            print(f"✗ error: {reason}")
            failures.append((video_id, reason))

        # Delay aleatorio entre 1 y 2 segundos para evitar rate limiting
        if idx < total:
            time.sleep(random.uniform(1.0, 2.0))

    # -----------------------------------------------------------------------
    # Resumen final
    # -----------------------------------------------------------------------
    failed_count = len(failures)
    print()
    print(f"✓ Exitosos: {successes}/{total}")
    if failures:
        failed_str = ", ".join(f"{vid} ({mot})" for vid, mot in failures)
        print(f"✗ Fallidos: [{failed_str}]")
    else:
        print("✗ Fallidos: []")


if __name__ == "__main__":
    main()
