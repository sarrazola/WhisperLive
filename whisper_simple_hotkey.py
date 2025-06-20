#!/usr/bin/env python3
"""
WhisperLive Simple Push-to-Talk
Presiona F12 para iniciar grabación, presiona de nuevo para parar y transcribir
"""
import time
import threading
import pyperclip
import subprocess
import sys
from pynput import keyboard
from pynput.keyboard import Key, Listener
from whisper_live.client import TranscriptionClient

class SimpleWhisperHotkey:
    def __init__(self):
        self.is_recording = False
        self.client = None
        self.recording_thread = None
        self.transcription_result = ""
        
        print("🎤 WhisperLive Simple Push-to-Talk")
        print("📋 Presiona F12 para INICIAR grabación")
        print("📋 Presiona F12 de nuevo para PARAR y transcribir")
        print("📝 El texto se pegará automáticamente donde tengas el cursor")
        print("❌ Presiona ESC para salir")
        print("-" * 50)
        
    def transcription_callback(self, text, segments):
        """Callback para recibir transcripción"""
        if text.strip():
            self.transcription_result = text.strip()
            print(f"📝 Transcrito: '{self.transcription_result}'")
    
    def start_recording(self):
        """Iniciar grabación"""
        if self.is_recording:
            return
            
        print("🔴 INICIANDO grabación... (presiona F12 para parar)")
        self.is_recording = True
        self.transcription_result = ""
        
        # Crear cliente en hilo separado
        def record():
            try:
                client = TranscriptionClient(
                    host="localhost",
                    port=9090,
                    lang="es",
                    translate=False,
                    model="small",
                    use_vad=True,
                    save_output_recording=False,
                    log_transcription=False,
                    transcription_callback=self.transcription_callback
                )
                
                # Simular grabación continua
                client()
                
            except Exception as e:
                print(f"❌ Error en grabación: {e}")
                self.is_recording = False
        
        self.recording_thread = threading.Thread(target=record, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """Parar grabación y procesar transcripción"""
        if not self.is_recording:
            return
            
        print("⏹️  PARANDO grabación...")
        self.is_recording = False
        
        # Esperar un poco para que se complete la transcripción
        print("🔄 Procesando transcripción...")
        time.sleep(3)
        
        # Pegar el texto
        if self.transcription_result:
            self.paste_text(self.transcription_result)
        else:
            print("❌ No se detectó texto. Intenta hablar más claro y cerca del micrófono")
    
    def paste_text(self, text):
        """Pegar texto en la aplicación activa"""
        try:
            # Copiar al portapapeles
            pyperclip.copy(text)
            print(f"📋 Copiado al portapapeles: '{text}'")
            
            # Esperar un momento
            time.sleep(0.5)
            
            # Pegar usando AppleScript en macOS
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            print("✅ Texto pegado automáticamente")
            
        except subprocess.CalledProcessError:
            print(f"⚠️  No se pudo pegar automáticamente, pero está en el portapapeles")
            print(f"💡 Usa Cmd+V para pegar: '{text}'")
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"📋 Texto disponible en portapapeles: '{text}'")
    
    def on_key_press(self, key):
        """Manejar teclas presionadas"""
        try:
            if key == Key.f12:
                if not self.is_recording:
                    self.start_recording()
                else:
                    self.stop_recording()
            elif key == Key.esc:
                print("\n👋 Saliendo del WhisperLive Push-to-Talk...")
                return False
        except AttributeError:
            pass
    
    def run(self):
        """Ejecutar el listener de teclado"""
        print("🚀 Sistema listo. Presiona F12 para empezar...")
        
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

def check_server():
    """Verificar si el servidor está corriendo"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 9090))
        sock.close()
        return result == 0
    except:
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🎤 WHISPERLIVE PUSH-TO-TALK")
    print("=" * 60)
    
    # Verificar servidor
    if not check_server():
        print("❌ El servidor WhisperLive no está corriendo")
        print("💡 Ejecuta en otra terminal:")
        print("   python run_server.py --port 9090 --backend faster_whisper")
        print()
        input("Presiona Enter cuando el servidor esté listo...")
        
        if not check_server():
            print("❌ Aún no se puede conectar al servidor. Saliendo...")
            return
    
    print("✅ Servidor detectado")
    print()
    
    try:
        app = SimpleWhisperHotkey()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 