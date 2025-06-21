#!/usr/bin/env python3
"""
WhisperLive Push-to-Talk DEFINITIVO v2
SOLUCIONADO: Reinicia servidor entre grabaciones para limpiar estado
"""
import time
import threading
import pyperclip
import subprocess
import sys
import uuid
import signal
import psutil
from pynput import keyboard
from pynput.keyboard import Key, Listener
from whisper_live.client import TranscriptionClient

class DefinitivoWhisperHotkey:
    def __init__(self):
        self.is_recording = False
        self.client = None
        self.recording_thread = None
        self.current_session_text = ""
        self.session_id = None
        self.server_process = None
        self.base_port = 9090
        
        print("🎤 WhisperLive Push-to-Talk DEFINITIVO v2")
        print("📋 Presiona F12 para INICIAR grabación")
        print("📋 Presiona F12 de nuevo para PARAR y pegar automáticamente")
        print("🔄 Reinicia servidor entre grabaciones para limpiar estado")
        print("📝 El texto se pegará donde tengas el cursor")
        print("❌ Presiona ESC para salir")
        print("-" * 70)
        
    def transcription_callback(self, text, segments):
        """Callback - texto de esta sesión únicamente"""
        if text.strip() and self.is_recording and self.session_id:
            clean_text = text.strip()
            if clean_text != self.current_session_text:
                self.current_session_text = clean_text
                print(f"🎤 [{self.session_id[:8]}] '{clean_text}'")
    
    def kill_existing_servers(self):
        """Matar todos los servidores WhisperLive existentes"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('run_server.py' in cmd for cmd in cmdline):
                        print(f"🔥 Matando servidor existente PID: {proc.info['pid']}")
                        proc.kill()
                        proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"⚠️  Error matando servidores: {e}")
        
        # Esperar a que se liberen los puertos
        time.sleep(2)
    
    def start_fresh_server(self):
        """Iniciar servidor completamente nuevo"""
        try:
            print("🚀 Iniciando servidor fresco...")
            
            # Matar servidores existentes
            self.kill_existing_servers()
            
            # Iniciar nuevo servidor
            cmd = [
                sys.executable, "run_server.py",
                "--port", str(self.base_port),
                "--backend", "faster_whisper",
                "--omp_num_threads", "4"
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd="/Users/andressarrazola/Documents/GitHub/WhisperLive"
            )
            
            # Esperar a que el servidor esté listo
            print("⏳ Esperando servidor...")
            for i in range(15):  # 15 segundos máximo
                time.sleep(1)
                if self.check_server_ready():
                    print("✅ Servidor listo")
                    return True
                    
            print("❌ Timeout esperando servidor")
            return False
            
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
            return False
    
    def check_server_ready(self):
        """Verificar si el servidor está listo"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.base_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def stop_server(self):
        """Parar servidor actual"""
        if self.server_process:
            try:
                print("🛑 Parando servidor...")
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✅ Servidor parado")
            except subprocess.TimeoutExpired:
                print("🔥 Forzando cierre de servidor...")
                self.server_process.kill()
                self.server_process.wait()
            except Exception as e:
                print(f"⚠️  Error parando servidor: {e}")
            finally:
                self.server_process = None
    
    def start_recording(self):
        """Iniciar grabación con servidor fresco"""
        if self.is_recording:
            return
            
        # Generar nueva sesión
        self.session_id = str(uuid.uuid4())
        self.current_session_text = ""
        
        print("\n" + "=" * 70)
        print("🔴 NUEVA GRABACIÓN - SERVIDOR COMPLETAMENTE FRESCO")
        print(f"🆔 Sesión: {self.session_id[:8]}")
        print("=" * 70)
        
        # Iniciar servidor fresco
        if not self.start_fresh_server():
            print("❌ No se pudo iniciar servidor fresco")
            return
        
        print("🎤 Grabando... (presiona F12 para parar)")
        self.is_recording = True
        
        def record():
            try:
                # Cliente con configuración mínima
                self.client = TranscriptionClient(
                    host="localhost",
                    port=self.base_port,
                    lang="es",
                    translate=False,
                    model="small",
                    use_vad=True,
                    save_output_recording=False,
                    log_transcription=False,
                    transcription_callback=self.transcription_callback,
                    send_last_n_segments=0,  # Sin memoria
                    same_output_threshold=999,  # Sin repetición
                )
                
                # Iniciar grabación
                self.client()
                
            except Exception as e:
                print(f"❌ Error en grabación: {e}")
                self.is_recording = False
        
        self.recording_thread = threading.Thread(target=record, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """Parar grabación y servidor"""
        if not self.is_recording:
            return
            
        print("⏹️  PARANDO grabación...")
        self.is_recording = False
        
        # Cerrar cliente
        if self.client:
            try:
                print("🔌 Cerrando cliente...")
                self.client.close_websocket()
            except Exception as e:
                print(f"⚠️  Error cerrando cliente: {e}")
        
        # Capturar texto final
        print("🔄 Capturando texto final...")
        time.sleep(1.0)
        
        final_text = self.current_session_text.strip()
        
        if final_text:
            print(f"✅ Transcripción: '{final_text}'")
            self.paste_text(final_text)
        else:
            print("❌ No se detectó texto")
        
        # PARAR SERVIDOR para limpiar estado
        self.stop_server()
        
        # Limpiar sesión
        self.cleanup_session()
        
        print("-" * 70)
        print("🚀 Listo para NUEVA grabación (presiona F12)")
    
    def cleanup_session(self):
        """Limpiar estado de sesión"""
        self.client = None
        self.current_session_text = ""
        self.session_id = None
        
        import gc
        gc.collect()
        
        print("🧹 Estado completamente limpio")
    
    def paste_text(self, text):
        """Pegar texto"""
        try:
            pyperclip.copy(text)
            print(f"📋 Copiado: '{text}'")
            
            time.sleep(0.2)
            
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            
            script = f'''
            tell application "System Events"
                set the clipboard to "{escaped_text}"
                delay 0.1
                keystroke "v" using command down
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Texto pegado automáticamente")
            else:
                print(f"💡 Usa Cmd+V para pegar: '{text}'")
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
            print(f"💡 Usa Cmd+V para pegar: '{text}'")
    
    def on_key_press(self, key):
        """Manejar teclas"""
        try:
            if key == Key.f12:
                if not self.is_recording:
                    self.start_recording()
                else:
                    self.stop_recording()
            elif key == Key.esc:
                print("\n👋 Saliendo...")
                if self.client:
                    try:
                        self.client.close_websocket()
                    except:
                        pass
                self.stop_server()
                return False
        except AttributeError:
            pass
    
    def run(self):
        """Ejecutar"""
        print("🚀 Sistema listo. Presiona F12 para primera grabación...")
        
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

def check_accessibility():
    """Verificar permisos"""
    try:
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to keystroke "test"'
        ], capture_output=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("🎤 WHISPERLIVE PUSH-TO-TALK DEFINITIVO v2")
    print("🔄 REINICIA SERVIDOR ENTRE GRABACIONES")
    print("=" * 70)
    
    # Verificar permisos
    if not check_accessibility():
        print("\n⚠️  PERMISOS NECESARIOS:")
        print("1. Sistema → Privacidad → Accesibilidad")
        print("2. Agregar 'Terminal' y activar")
        print("3. Reiniciar script")
        print()
        input("Presiona Enter cuando tengas permisos...")
    
    print("✅ Permisos verificados")
    print()
    
    try:
        app = DefinitivoWhisperHotkey()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Saliendo...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 