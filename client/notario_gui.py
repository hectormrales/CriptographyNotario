"""
Cliente de escritorio del Notario Digital con interfaz gráfica.
Permite seleccionar archivos, notarizarlos y verificar recibos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto, guardar_recibo, cargar_recibo


class NotarioDigitalApp:
    """Aplicación de escritorio del Notario Digital."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏛️ Notario Digital - Cliente")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configuración del servidor API
        self.api_url = "http://127.0.0.1:8000"
        self.archivo_actual = None
        self.hash_actual = None
        self.recibo_actual = None
        
        # Instancia de crypto para calcular hashes
        self.crypto = NotarioCrypto()
        
        # Directorio de recibos
        self.receipts_dir = os.path.join(os.path.dirname(__file__), '..', 'receipts')
        os.makedirs(self.receipts_dir, exist_ok=True)
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Verificar conexión con servidor
        self.root.after(100, self.verificar_servidor)
    
    def configurar_estilo(self):
        """Configura el estilo visual de la aplicación."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Segoe UI', 9, 'bold'), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Segoe UI', 9, 'bold'), foreground='#e74c3c')
        
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Secondary.TButton', font=('Segoe UI', 9))
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica principal."""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🏛️ Notario Digital", style='Title.TLabel')
        titulo.grid(row=0, column=0, pady=(0, 5))
        
        subtitulo = ttk.Label(main_frame, 
                             text="Sistema de notarización y verificación de documentos digitales",
                             style='Info.TLabel')
        subtitulo.grid(row=1, column=0, pady=(0, 20))
        
        # Crear notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        # Pestaña 1: Notarizar
        self.crear_tab_notarizar(notebook)
        
        # Pestaña 2: Verificar
        self.crear_tab_verificar(notebook)
        
        # Pestaña 3: Información
        self.crear_tab_info(notebook)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, style='Info.TLabel')
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def crear_tab_notarizar(self, notebook):
        """Crea la pestaña de notarización."""
        tab = ttk.Frame(notebook, padding="15")
        notebook.add(tab, text="📝 Notarizar Documento")
        
        # Sección: Seleccionar archivo
        ttk.Label(tab, text="1. Seleccionar Archivo", style='Header.TLabel').grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.archivo_label = ttk.Label(tab, text="Ningún archivo seleccionado", 
                                       style='Info.TLabel')
        self.archivo_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(tab, text="📂 Seleccionar Archivo", 
                  command=self.seleccionar_archivo,
                  style='Primary.TButton').grid(
            row=1, column=2, sticky=tk.E, pady=5
        )
        
        # Sección: Hash del archivo
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        ttk.Label(tab, text="2. Hash SHA-256 del Archivo", style='Header.TLabel').grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.hash_text = scrolledtext.ScrolledText(tab, height=3, width=70, 
                                                   wrap=tk.WORD, state=tk.DISABLED)
        self.hash_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Sección: Notarizar
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        ttk.Label(tab, text="3. Notarizar", style='Header.TLabel').grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.btn_notarizar = ttk.Button(tab, text="🔏 Notarizar Documento", 
                                       command=self.notarizar_documento,
                                       style='Primary.TButton',
                                       state=tk.DISABLED)
        self.btn_notarizar.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Resultado
        self.resultado_notarizar = scrolledtext.ScrolledText(tab, height=8, width=70, 
                                                             wrap=tk.WORD, state=tk.DISABLED)
        self.resultado_notarizar.grid(row=8, column=0, columnspan=3, 
                                     sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(8, weight=1)
    
    def crear_tab_verificar(self, notebook):
        """Crea la pestaña de verificación."""
        tab = ttk.Frame(notebook, padding="15")
        notebook.add(tab, text="✓ Verificar Recibo")
        
        # Sección: Cargar recibo
        ttk.Label(tab, text="1. Cargar Recibo Digital", style='Header.TLabel').grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.recibo_label = ttk.Label(tab, text="Ningún recibo cargado", 
                                     style='Info.TLabel')
        self.recibo_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(tab, text="📂 Cargar Recibo (.json)", 
                  command=self.cargar_recibo_archivo,
                  style='Secondary.TButton').grid(
            row=1, column=2, sticky=tk.E, pady=5
        )
        
        # Sección: Archivo a verificar
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        ttk.Label(tab, text="2. Archivo a Verificar", style='Header.TLabel').grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.archivo_verificar_label = ttk.Label(tab, text="Ningún archivo seleccionado", 
                                                style='Info.TLabel')
        self.archivo_verificar_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Button(tab, text="📂 Seleccionar Archivo", 
                  command=self.seleccionar_archivo_verificar,
                  style='Secondary.TButton').grid(
            row=4, column=2, sticky=tk.E, pady=5
        )
        
        # Sección: Verificar
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        ttk.Label(tab, text="3. Verificar", style='Header.TLabel').grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        self.btn_verificar = ttk.Button(tab, text="✓ Verificar Autenticidad", 
                                       command=self.verificar_recibo,
                                       style='Primary.TButton',
                                       state=tk.DISABLED)
        self.btn_verificar.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Resultado
        self.resultado_verificar = scrolledtext.ScrolledText(tab, height=10, width=70, 
                                                            wrap=tk.WORD, state=tk.DISABLED)
        self.resultado_verificar.grid(row=8, column=0, columnspan=3, 
                                     sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(8, weight=1)
    
    def crear_tab_info(self, notebook):
        """Crea la pestaña de información."""
        tab = ttk.Frame(notebook, padding="15")
        notebook.add(tab, text="ℹ️ Información")
        
        info_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, width=70, height=25)
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        
        # Contenido informativo
        contenido = """
🏛️ NOTARIO DIGITAL - Sistema de Notarización Criptográfica

═══════════════════════════════════════════════════════════════

📋 ¿QUÉ ES?

El Notario Digital es un sistema que permite certificar la existencia e
integridad de documentos digitales en un momento específico del tiempo,
utilizando criptografía de curva elíptica (ECDSA).

═══════════════════════════════════════════════════════════════

🔐 ¿CÓMO FUNCIONA?

1. PRIVACIDAD: El usuario NUNCA envía su archivo completo. Solo se envía
   el hash SHA-256 del archivo.

2. TIMESTAMP: El servidor añade un sello de tiempo oficial que certifica
   el momento exacto de la notarización.

3. FIRMA DIGITAL: El servidor firma el hash + timestamp con su clave
   privada ECDSA, generando un recibo digital infalsificable.

4. VERIFICACIÓN: Cualquiera puede verificar el recibo usando la clave
   pública del notario, sin necesidad de confiar en terceros.

═══════════════════════════════════════════════════════════════

🛡️ SEGURIDAD

• Algoritmo: ECDSA con curva SECP256R1
• Hash: SHA-256 (256 bits de seguridad)
• Clave privada: Protegida en el servidor, nunca expuesta
• Firmas: Matemáticamente imposibles de falsificar sin la clave privada

═══════════════════════════════════════════════════════════════

📝 CASOS DE USO

✓ Protección de propiedad intelectual
✓ Contratos digitales
✓ Código fuente y desarrollo de software
✓ Arte digital y NFTs
✓ Documentos legales
✓ Registros académicos
✓ Cualquier archivo que requiera certificación temporal

═══════════════════════════════════════════════════════════════

🔑 CONCEPTOS CLAVE

• Hash SHA-256: Una "huella digital" única de 64 caracteres que
  identifica unívocamente un archivo. Cualquier cambio en el archivo,
  por mínimo que sea, produce un hash completamente diferente.

• Firma Digital ECDSA: Una firma matemática que solo puede ser creada
  por quien posee la clave privada, pero que cualquiera puede verificar
  con la clave pública.

• Timestamp: Marca de tiempo certificada que prueba que el hash existía
  en ese momento específico.

═══════════════════════════════════════════════════════════════

📖 CÓMO USAR

NOTARIZAR:
1. Selecciona el archivo que deseas notarizar
2. El sistema calculará automáticamente su hash SHA-256
3. Click en "Notarizar Documento"
4. Guarda el recibo digital (.json) que se genera

VERIFICAR:
1. Carga el recibo digital (.json)
2. Selecciona el archivo original
3. Click en "Verificar Autenticidad"
4. El sistema confirmará si el archivo es auténtico

═══════════════════════════════════════════════════════════════

⚠️ IMPORTANTE

• Guarda siempre tus recibos en un lugar seguro
• Un recibo solo es válido para el archivo específico que se notarizó
• Si el archivo cambia aunque sea un bit, la verificación fallará
• La clave privada del notario nunca debe ser compartida

═══════════════════════════════════════════════════════════════

Desarrollado con Python, cryptography.io, FastAPI y tkinter
"""
        
        info_text.insert('1.0', contenido)
        info_text.config(state=tk.DISABLED)
    
    def verificar_servidor(self):
        """Verifica la conexión con el servidor API."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                self.status_var.set("✅ Conectado al servidor")
            else:
                self.status_var.set("⚠️ Servidor respondió con error")
        except requests.exceptions.ConnectionError:
            self.status_var.set("❌ No se puede conectar al servidor. Asegúrate de que esté ejecutándose.")
            messagebox.showwarning(
                "Servidor no disponible",
                "No se puede conectar al servidor API.\n\n"
                "Asegúrate de iniciar el servidor ejecutando:\n"
                "python server/api_server.py"
            )
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
    
    def seleccionar_archivo(self):
        """Permite al usuario seleccionar un archivo para notarizar."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo para notarizar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if filename:
            self.archivo_actual = filename
            nombre_archivo = os.path.basename(filename)
            self.archivo_label.config(text=f"📄 {nombre_archivo}")
            self.status_var.set("Calculando hash...")
            
            # Calcular hash
            try:
                self.hash_actual = self.crypto.calcular_hash_archivo(filename)
                
                # Mostrar hash
                self.hash_text.config(state=tk.NORMAL)
                self.hash_text.delete('1.0', tk.END)
                self.hash_text.insert('1.0', self.hash_actual)
                self.hash_text.config(state=tk.DISABLED)
                
                # Habilitar botón de notarizar
                self.btn_notarizar.config(state=tk.NORMAL)
                self.status_var.set(f"✅ Archivo seleccionado - Hash calculado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error calculando hash: {str(e)}")
                self.status_var.set("❌ Error calculando hash")
    
    def notarizar_documento(self):
        """Envía el hash al servidor para notarizar."""
        if not self.hash_actual:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo")
            return
        
        try:
            self.status_var.set("Notarizando documento...")
            
            # Enviar solicitud al servidor
            response = requests.post(
                f"{self.api_url}/notarizar",
                json={"hash": self.hash_actual},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Guardar recibo
                timestamp_str = data['timestamp'].replace(':', '-').replace('.', '-')
                nombre_archivo = os.path.basename(self.archivo_actual)
                nombre_recibo = f"recibo_{nombre_archivo}_{timestamp_str}.json"
                ruta_recibo = os.path.join(self.receipts_dir, nombre_recibo)
                
                recibo = {
                    "timestamp": data['timestamp'],
                    "hash": data['hash'],
                    "firma": data['firma'],
                    "archivo_original": nombre_archivo
                }
                
                guardar_recibo(recibo, ruta_recibo)
                
                # Mostrar resultado
                resultado = f"""
✅ DOCUMENTO NOTARIZADO EXITOSAMENTE

Archivo: {nombre_archivo}
Hash SHA-256: {data['hash']}
Timestamp: {data['timestamp']}
Firma Digital: {data['firma'][:50]}...

📄 Recibo guardado en:
{ruta_recibo}

⚠️ IMPORTANTE: Guarda este recibo en un lugar seguro.
Es la prueba de que este documento existía en este momento.
"""
                
                self.resultado_notarizar.config(state=tk.NORMAL)
                self.resultado_notarizar.delete('1.0', tk.END)
                self.resultado_notarizar.insert('1.0', resultado)
                self.resultado_notarizar.config(state=tk.DISABLED)
                
                self.status_var.set("✅ Documento notarizado exitosamente")
                messagebox.showinfo("Éxito", f"Documento notarizado.\n\nRecibo guardado en:\n{nombre_recibo}")
                
            else:
                error = response.json().get('detail', 'Error desconocido')
                messagebox.showerror("Error", f"Error del servidor: {error}")
                self.status_var.set("❌ Error en notarización")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", 
                               "No se puede conectar al servidor.\n"
                               "Asegúrate de que el servidor esté ejecutándose.")
            self.status_var.set("❌ Error de conexión")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("❌ Error en notarización")
    
    def cargar_recibo_archivo(self):
        """Carga un recibo digital desde un archivo JSON."""
        filename = filedialog.askopenfilename(
            title="Seleccionar recibo digital",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                self.recibo_actual = cargar_recibo(filename)
                nombre_recibo = os.path.basename(filename)
                self.recibo_label.config(text=f"📄 {nombre_recibo}")
                self.status_var.set("✅ Recibo cargado")
                self.actualizar_estado_verificar()
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando recibo: {str(e)}")
                self.status_var.set("❌ Error cargando recibo")
    
    def seleccionar_archivo_verificar(self):
        """Selecciona el archivo a verificar contra el recibo."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo a verificar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if filename:
            self.archivo_verificar = filename
            nombre_archivo = os.path.basename(filename)
            self.archivo_verificar_label.config(text=f"📄 {nombre_archivo}")
            self.status_var.set("✅ Archivo para verificar seleccionado")
            self.actualizar_estado_verificar()
    
    def actualizar_estado_verificar(self):
        """Actualiza el estado del botón de verificar."""
        if hasattr(self, 'recibo_actual') and hasattr(self, 'archivo_verificar'):
            if self.recibo_actual and self.archivo_verificar:
                self.btn_verificar.config(state=tk.NORMAL)
    
    def verificar_recibo(self):
        """Verifica la autenticidad del recibo contra el archivo."""
        if not self.recibo_actual or not hasattr(self, 'archivo_verificar'):
            messagebox.showwarning("Advertencia", "Carga un recibo y selecciona un archivo")
            return
        
        try:
            self.status_var.set("Verificando recibo...")
            
            # Calcular hash del archivo
            hash_archivo = self.crypto.calcular_hash_archivo(self.archivo_verificar)
            
            # Verificar que el hash coincida
            if hash_archivo.lower() != self.recibo_actual['hash'].lower():
                resultado = f"""
❌ VERIFICACIÓN FALLIDA

El archivo NO corresponde al recibo.

Hash del archivo actual: {hash_archivo}
Hash en el recibo: {self.recibo_actual['hash']}

⚠️ POSIBLES CAUSAS:
• El archivo ha sido modificado
• El recibo no corresponde a este archivo
• El archivo está corrupto
"""
                self.resultado_verificar.config(state=tk.NORMAL)
                self.resultado_verificar.delete('1.0', tk.END)
                self.resultado_verificar.insert('1.0', resultado)
                self.resultado_verificar.config(state=tk.DISABLED)
                
                self.status_var.set("❌ Verificación fallida - Hash no coincide")
                messagebox.showwarning("Verificación Fallida", 
                                     "El archivo NO corresponde al recibo.\n"
                                     "El hash no coincide.")
                return
            
            # Enviar a servidor para verificar firma
            response = requests.post(
                f"{self.api_url}/verificar",
                json={
                    "timestamp": self.recibo_actual['timestamp'],
                    "hash": self.recibo_actual['hash'],
                    "firma": self.recibo_actual['firma']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['valido']:
                    resultado = f"""
✅ RECIBO AUTÉNTICO Y VÁLIDO

El recibo es legítimo y el archivo no ha sido alterado.

Archivo: {os.path.basename(self.archivo_verificar)}
Hash SHA-256: {self.recibo_actual['hash']}
Timestamp: {self.recibo_actual['timestamp']}
Firma Digital: ✓ Verificada

🔐 CONFIRMACIÓN:
• El archivo existía en la fecha indicada
• El archivo NO ha sido modificado desde entonces
• La firma digital es auténtica del Notario
• El recibo NO ha sido falsificado

Este documento tiene validez probatoria.
"""
                    self.status_var.set("✅ Recibo VÁLIDO - Documento auténtico")
                    messagebox.showinfo("Verificación Exitosa", 
                                      "✅ RECIBO AUTÉNTICO\n\n"
                                      "El documento es válido y no ha sido alterado.")
                else:
                    resultado = f"""
❌ RECIBO INVÁLIDO

La firma digital NO es válida.

Hash: {self.recibo_actual['hash']}
Timestamp: {self.recibo_actual['timestamp']}
Firma: ❌ NO verificada

⚠️ ADVERTENCIA:
• El recibo ha sido alterado
• La firma no corresponde al Notario
• El recibo puede ser fraudulento

NO confíes en este recibo.
"""
                    self.status_var.set("❌ Recibo INVÁLIDO - Firma no verificada")
                    messagebox.showerror("Verificación Fallida", 
                                       "❌ RECIBO INVÁLIDO\n\n"
                                       "La firma digital no es válida.")
                
                self.resultado_verificar.config(state=tk.NORMAL)
                self.resultado_verificar.delete('1.0', tk.END)
                self.resultado_verificar.insert('1.0', resultado)
                self.resultado_verificar.config(state=tk.DISABLED)
                
            else:
                error = response.json().get('detail', 'Error desconocido')
                messagebox.showerror("Error", f"Error del servidor: {error}")
                self.status_var.set("❌ Error en verificación")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", 
                               "No se puede conectar al servidor.\n"
                               "Asegúrate de que el servidor esté ejecutándose.")
            self.status_var.set("❌ Error de conexión")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("❌ Error en verificación")


def main():
    """Función principal para iniciar la aplicación."""
    root = tk.Tk()
    app = NotarioDigitalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
