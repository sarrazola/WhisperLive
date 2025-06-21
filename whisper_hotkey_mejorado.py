#!/usr/bin/env python3
"""
WhisperLive Push-to-Talk MEJORADO
Presiona F12 para iniciar, F12 de nuevo para parar y pegar automáticamente
"""
import time
import threading
import pyperclip
import subprocess
import sys
from pynput import keyboard
from pynput.keyboard import Key, Listener
from whisper_live.client import TranscriptionClient

class MejoradoWhisperHotkey:
    def __init__(self):
        self.is_recording = False
        self.client = None
        self.recording_thread = None
        self.final_transcription = ""
        self.temp_transcription = ""
        
        print("🎤 WhisperLive Push-to-Talk MEJORADO")
        print("📋 Presiona F12 para INICIAR grabación")
        print("📋 Presiona F12 de nuevo para PARAR y pegar automáticamente")
        print("📝 El texto se pegará donde tengas el cursor")
        print("❌ Presiona ESC para salir")
        print("-" * 50)
        
    def transcription_callback(self, text, segments):
        """Callback para recibir transcripción - solo guarda, no imprime repetidamente"""
        if text.strip():
            self.temp_transcription = text.strip()
            # Solo imprimir la primera vez o si cambió significativamente
            if not self.final_transcription or len(text.strip()) > len(self.final_transcription) + 5:
                print(f"🎤 Escuchando: '{text.strip()}'")
                self.final_transcription = text.strip()
    
    def start_recording(self):
        """Iniciar grabación"""
        if self.is_recording:
            return
            
        print("🔴 INICIANDO grabación... (presiona F12 para parar y pegar)")
        self.is_recording = True
        self.final_transcription = ""
        self.temp_transcription = ""
        
        # Crear cliente en hilo separado
        def record():
            try:
                self.client = TranscriptionClient(
                    host="localhost",
                    port=9090,
                    lang="es",
                    translate=False,
                    model="small",
                    use_vad=True,
                    save_output_recording=False,
                    log_transcription=False,  # Desactivar logs repetitivos
                    transcription_callback=self.transcription_callback
                )
                
                # Iniciar grabación continua
                self.client()
                
            except Exception as e:
                print(f"❌ Error en grabación: {e}")
                self.is_recording = False
        
        self.recording_thread = threading.Thread(target=record, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """Parar grabación y pegar transcripción"""
        if not self.is_recording:
            return
            
        print("⏹️  PARANDO grabación...")
        self.is_recording = False
        
        # Cerrar cliente si existe
        if self.client:
            try:
                self.client.close_websocket()
            except:
                pass
        
        # Esperar un momento para obtener transcripción final
        print("🔄 Obteniendo transcripción final...")
        time.sleep(1.5)
        
        # Usar la última transcripción disponible
        final_text = self.temp_transcription or self.final_transcription
        
        if final_text:
            print(f"✅ Transcripción final: '{final_text}'")
            self.paste_text(final_text)
        else:
            print("❌ No se detectó texto. Intenta hablar más claro")
    
    def paste_text(self, text):
        """Pegar texto en la aplicación activa con múltiples métodos"""
        try:
            # Método 1: Copiar al portapapeles
            pyperclip.copy(text)
            print(f"📋 Copiado: '{text}'")
            
            # Método 2: Intentar pegar con AppleScript mejorado
            time.sleep(0.3)
            
            script = f'''
            tell application "System Events"
                set the clipboard to "{text}"
                delay 0.1
                keystroke "v" using command down
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Texto pegado automáticamente")
            else:
                # Método 3: Usar método alternativo
                self.paste_alternative(text)
                
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout en pegado, pero texto está en portapapeles")
            print(f"💡 Usa Cmd+V para pegar: '{text}'")
        except Exception as e:
            print(f"⚠️  {e}")
            print(f"💡 Usa Cmd+V para pegar: '{text}'")
    
    def paste_alternative(self, text):
        """Método alternativo de pegado"""
        try:
            # Usar osascript más simple
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using command down'
            ], timeout=3)
            print("✅ Texto pegado (método alternativo)")
        except:
            print(f"💡 Usa Cmd+V para pegar: '{text}'")
    
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
                if self.client:
                    try:
                        self.client.close_websocket()
                    except:
                        pass
                return False
        except AttributeError:
            pass
    
    def run(self):
        """Ejecutar el listener de teclado"""
        print("🚀 Sistema listo. Presiona F12 para empezar...")
        
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

def check_accessibility_permissions():
    """Verificar permisos de accesibilidad"""
    try:
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to keystroke "test"'
        ], capture_output=True, timeout=2)
        return result.returncode == 0
    except:
        return False

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
    print("🎤 WHISPERLIVE PUSH-TO-TALK MEJORADO")
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
    
    # Verificar permisos de accesibilidad
    if not check_accessibility_permissions():
        print("\n⚠️  PERMISOS NECESARIOS:")
        print("1. Ve a: Configuración del Sistema → Privacidad y Seguridad → Accesibilidad")
        print("2. Agrega 'Terminal' y actívalo")
        print("3. Reinicia este script")
        print()
        input("Presiona Enter cuando hayas dado los permisos...")
    
    print()
    
    try:
        app = MejoradoWhisperHotkey()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 