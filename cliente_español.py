#!/usr/bin/env python3
"""
Cliente de WhisperLive configurado para transcribir en español
"""
import sys
import os
from whisper_live.client import TranscriptionClient

def transcribir_microfono():
    """Transcribir desde el micrófono en tiempo real"""
    print("=== Transcripción desde Micrófono en Español ===")
    
    # Configurar cliente para español
    client = TranscriptionClient(
        host="localhost",
        port=9090,
        lang="es",                                          # Idioma español
        translate=False,                                    # No traducir, mantener en español
        model="small",                                      # Modelo recomendado
        use_vad=True,                                       # Detección de actividad de voz
        save_output_recording=True,                         # Guardar grabación
        output_recording_filename="./grabacion_microfono.wav"
    )
    
    print("🎤 Habla por el micrófono (presiona Ctrl+C para parar)")
    print("📝 La transcripción aparecerá en tiempo real")
    print("💾 Se guardará en: grabacion_microfono.wav")
    print("-" * 50)
    
    try:
        client()
    except KeyboardInterrupt:
        print("\n✅ Transcripción terminada")
    except Exception as e:
        print(f"❌ Error: {e}")

def transcribir_archivo(archivo_audio):
    """Transcribir desde un archivo de audio"""
    print(f"=== Transcribiendo archivo: {archivo_audio} ===")
    
    if not os.path.exists(archivo_audio):
        print(f"❌ Error: El archivo {archivo_audio} no existe")
        return
    
    # Configurar cliente para español
    client = TranscriptionClient(
        host="localhost",
        port=9090,
        lang="es",                                          # Idioma español
        translate=False,                                    # No traducir, mantener en español
        model="small",                                      # Modelo recomendado
        use_vad=True,                                       # Detección de actividad de voz
        mute_audio_playback=True                            # No reproducir el audio
    )
    
    print("📁 Transcribiendo archivo...")
    print("-" * 50)
    
    try:
        client(archivo_audio)
        print("✅ Transcripción completada")
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_ayuda():
    """Mostrar información de uso"""
    print("""
🎯 Cliente de WhisperLive - Transcripción en Español

Uso:
    python cliente_español.py                  # Transcribir desde micrófono
    python cliente_español.py <archivo.wav>    # Transcribir archivo de audio
    python cliente_español.py --help           # Mostrar esta ayuda

Ejemplos:
    python cliente_español.py                          # Usar micrófono
    python cliente_español.py mi_audio.wav             # Transcribir archivo
    python cliente_español.py assets/jfk.flac          # Usar archivo de ejemplo

Notas:
    - Asegúrate de que el servidor esté ejecutándose primero
    - Formatos soportados: .wav, .mp3, .flac, .m4a, etc.
    - El modelo detectará automáticamente el español
""")

def main():
    if len(sys.argv) == 1:
        # Sin argumentos: usar micrófono
        transcribir_microfono()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ["--help", "-h", "help"]:
            mostrar_ayuda()
        else:
            # Con archivo: transcribir archivo
            transcribir_archivo(arg)
    else:
        print("❌ Demasiados argumentos")
        mostrar_ayuda()

if __name__ == "__main__":
    main() 