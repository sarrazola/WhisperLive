#!/usr/bin/env python3
"""
WhisperLive Push-to-Talk con Hotkey
Presiona y mantén F12 para grabar, suelta para transcribir y pegar
"""
import time
import threading
import pyperclip
import subprocess
import sys
from pynput import keyboard
from pynput.keyboard import Key, Listener
from whisper_live.client import TranscriptionClient

class WhisperHotkey:
    def __init__(self):
        self.is_recording = False
        self.client = None
        self.current_transcription = ""
        self.hotkey = Key.f12  # Tecla F12 por defecto
        
        print("🎤 WhisperLive Push-to-Talk")
        print(f"📋 Presiona y mantén {self.hotkey.name.upper()} para grabar")
        print("📝 Suelta para transcribir y pegar el texto")
        print("❌ Presiona ESC para salir")
        print("🔄 Esperando conexión al servidor...")
        
        # Intentar conectar al servidor
        self.setup_client()
        
    def setup_client(self):
        """Configurar el cliente de WhisperLive"""
        try:
            self.client = TranscriptionClient(
                host="localhost",
                port=9090,
                lang="es",                              # Español
                translate=False,                        # No traducir
                model="small",                          # Modelo pequeño
                use_vad=True,                          # Detección de voz
                save_output_recording=False,            # No guardar archivo
                log_transcription=False,                # No mostrar en consola
                transcription_callback=self.on_transcription  # Callback personalizado
            )
            print("✅ Conectado al servidor WhisperLive")
        except Exception as e:
            print(f"❌ Error conectando al servidor: {e}")
            print("💡 Asegúrate de que el servidor esté corriendo:")
            print("   python run_server.py --port 9090 --backend faster_whisper")
            sys.exit(1)
    
    def on_transcription(self, text, segments):
        """Callback cuando se recibe transcripción"""
        if text.strip():
            self.current_transcription = text.strip()
            print(f"📝 Transcrito: {self.current_transcription}")
    
    def start_recording(self):
        """Iniciar grabación"""
        if not self.is_recording:
            self.is_recording = True
            self.current_transcription = ""
            print("🔴 Grabando... (suelta F12 para parar)")
            
            # Iniciar grabación en hilo separado
            threading.Thread(target=self._record_audio, daemon=True).start()
    
    def stop_recording(self):
        """Parar grabación y procesar"""
        if self.is_recording:
            self.is_recording = False
            print("⏹️  Parando grabación...")
            print("🔄 Procesando transcripción...")
            
            # Esperar un poco para que termine la transcripción
            time.sleep(2)
            
            # Pegar el texto si hay transcripción
            if self.current_transcription:
                self.paste_text(self.current_transcription)
            else:
                print("❌ No se detectó audio")
    
    def _record_audio(self):
        """Grabar audio mientras is_recording sea True"""
        try:
            # Crear una nueva instancia temporal para grabación
            temp_client = TranscriptionClient(
                host="localhost",
                port=9090,
                lang="es",
                translate=False,
                model="small",
                use_vad=True,
                save_output_recording=False,
                log_transcription=False,
                transcription_callback=self.on_transcription
            )
            
            # Simular grabación de micrófono limitada
            # Nota: Esta es una implementación básica
            temp_client()
            
        except Exception as e:
            print(f"❌ Error en grabación: {e}")
    
    def paste_text(self, text):
        """Pegar texto en la aplicación activa"""
        try:
            # Copiar al portapapeles
            pyperclip.copy(text)
            print(f"📋 Copiado al portapapeles: {text}")
            
            # Simular Cmd+V en macOS
            import subprocess
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            print("✅ Texto pegado")
            
        except Exception as e:
            print(f"❌ Error pegando texto: {e}")
            print(f"📋 Texto copiado al portapapeles: {text}")
    
    def on_key_press(self, key):
        """Manejar teclas presionadas"""
        try:
            if key == self.hotkey:
                self.start_recording()
            elif key == Key.esc:
                print("👋 Saliendo...")
                return False
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        """Manejar teclas liberadas"""
        try:
            if key == self.hotkey:
                self.stop_recording()
        except AttributeError:
            pass
    
    def run(self):
        """Ejecutar el listener de teclado"""
        with Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
            listener.join()

def main():
    """Función principal"""
    try:
        hotkey_app = WhisperHotkey()
        hotkey_app.run()
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 