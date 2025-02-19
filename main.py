import essentia.standard as es
from fastapi import FastAPI, HTTPException
import os
import yt_dlp
from tempfile import mkdtemp

app = FastAPI()

# Configuración temporal para almacenar archivos descargados
TEMP_DIR = mkdtemp()

def download_audio(youtube_url):
    try:
        print("🔹 Descargando audio desde YouTube...")
        
        # Opciones de yt-dlp para descargar solo audio en formato MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,  # Evita la salida innecesaria en la consola
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        
        print(f"🎵 Audio descargado: {audio_filename}")
        return audio_filename

    except Exception as e:
        print(f"❌ Error descargando el audio: {e}")
        return None

def extract_bpm(file_path):
    try:
        print("🔹 Detectando BPM...")
        audio = es.MonoLoader(filename=file_path)()
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, _, _, _, _ = rhythm_extractor(audio)
        return round(bpm, 2)
    except Exception as e:
        print(f"❌ Error detectando BPM: {e}")
        return None

def extract_tonality(file_path):
    try:
        print("🔹 Detectando tonalidad...")
        audio = es.MonoLoader(filename=file_path)()
        key_extractor = es.KeyExtractor()
        key, scale, strength = key_extractor(audio)
        
        if strength < 0.5:
            print("⚠️ Baja confianza en la detección de tonalidad. Revisar el archivo.")
            return None, None
        
        print(f"🎵 Tonalidad detectada: {key} {scale} (confianza: {strength:.2f})")
        return key, scale
            
    except Exception as e:
        print(f"❌ Error detectando tonalidad: {e}")
        return None, None

@app.get("/analyze_youtube/")
async def analyze_youtube(youtube_url: str):
    try:
        # Descargar el audio desde YouTube
        audio_filename = download_audio(youtube_url)
        if not audio_filename or not os.path.exists(audio_filename):
            raise HTTPException(status_code=400, detail="Error al descargar el audio desde YouTube")

        # Analizar el audio
        bpm = extract_bpm(audio_filename)
        key, mode = extract_tonality(audio_filename)

        if bpm is None or key is None or mode is None:
            raise HTTPException(status_code=500, detail="Error procesando el audio")

        # Eliminar el archivo descargado después del análisis (opcional)
        os.remove(audio_filename)

        return {
            "tonality": key,
            "mode": mode,
            "bpm": bpm
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error procesando el archivo: {str(e)}"
        )