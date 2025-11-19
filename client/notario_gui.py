"""
Cliente de escritorio del Notario Digital con interfaz gráfica.
Permite seleccionar archivos, notarizarlos y verificar recibos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio shared al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.crypto_utils import NotarioCrypto, guardar_recibo, cargar_recibo, CURVAS_SOPORTADAS


class NotarioDigitalApp:
    """Aplicación de escritorio del Notario Digital."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏛️ Notario Digital - Sistema Criptográfico Profesional")
        self.root.geometry("1100x800")
        self.root.minsize(950, 700)
        self.root.resizable(True, True)
        
        # Configurar grid responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configuración del servidor API
        self.api_url = "http://127.0.0.1:8000"
        self.archivo_actual = None
        self.hash_actual = None
        self.recibo_actual = None
        
        # Curva seleccionada (por defecto SECP256R1)
        self.curva_seleccionada = "SECP256R1"
        
        # Instancia de crypto para calcular hashes
        self.crypto = NotarioCrypto()
        
        # Directorio de recibos
        self.receipts_dir = os.path.join(os.path.dirname(__file__), '..', 'receipts')
        os.makedirs(self.receipts_dir, exist_ok=True)
        
        # Directorio de claves
        self.keys_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
        os.makedirs(self.keys_dir, exist_ok=True)
        
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
        
        # Paleta de colores profesional con ALTO contraste (sin grises opacos)
        self.color_primary = '#2563eb'      # Azul moderno
        self.color_primary_dark = '#1e40af' # Azul oscuro para hover
        self.color_success = '#10b981'      # Verde esmeralda
        self.color_danger = '#ef4444'       # Rojo brillante
        self.color_warning = '#f59e0b'      # Ámbar
        self.color_accent = '#8b5cf6'       # Violeta
        self.color_bg = '#f1f5f9'           # Fondo gris azulado
        self.color_card = '#ffffff'         # Blanco puro
        self.color_border = '#cbd5e1'       # Borde gris azulado
        self.color_text = '#0f172a'         # Texto MUY oscuro (máximo contraste)
        self.color_text_secondary = '#1e293b'  # Texto secundario OSCURO (antes era opaco)
        self.color_shadow = '#e2e8f0'       # Sombra sutil
        
        # Radio de bordes redondeados
        self.border_radius = 12
        
        # Configuración de fuentes profesionales
        self.font_title = ('Segoe UI', 22, 'bold')
        self.font_header = ('Segoe UI', 13, 'bold')
        self.font_subheader = ('Segoe UI', 11, 'bold')
        self.font_normal = ('Segoe UI', 10)
        self.font_small = ('Segoe UI', 9)
        self.font_mono = ('Consolas', 9)
        
        # Color de fondo principal
        self.root.configure(bg=self.color_bg)
        
        # Estilos de Notebook (pestañas) con mejor contraste
        style.configure('TNotebook', 
                       background=self.color_bg, 
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', 
                       padding=[28, 13],
                       font=self.font_header,
                       background=self.color_card,
                       foreground=self.color_text,
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.color_primary)],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [2, 2, 2, 0])],
                 padding=[('selected', [28, 13])])
        
        # Estilos de Labels con mejor legibilidad
        style.configure('Title.TLabel', 
                       font=self.font_title, 
                       foreground=self.color_text,
                       background=self.color_bg)
        
        style.configure('Header.TLabel', 
                       font=self.font_header, 
                       foreground=self.color_text,
                       background=self.color_card)
        
        style.configure('SubHeader.TLabel', 
                       font=self.font_subheader, 
                       foreground=self.color_text,
                       background=self.color_card)
        
        style.configure('Info.TLabel', 
                       font=self.font_normal, 
                       foreground=self.color_text_secondary,
                       background=self.color_card)
        
        style.configure('Success.TLabel', 
                       font=self.font_subheader, 
                       foreground=self.color_success,
                       background=self.color_card)
        
        style.configure('Error.TLabel', 
                       font=self.font_subheader, 
                       foreground=self.color_danger,
                       background=self.color_card)
        
        style.configure('Warning.TLabel', 
                       font=self.font_subheader, 
                       foreground=self.color_warning,
                       background=self.color_card)
        
        style.configure('Accent.TLabel', 
                       font=self.font_normal, 
                       foreground=self.color_accent,
                       background=self.color_card)
        
        style.configure('CardHeader.TLabel',
                       font=self.font_header,
                       foreground='white',
                       padding=[15, 10])
        
        # Estilos de Frames
        style.configure('TFrame', background=self.color_bg)
        style.configure('Card.TFrame', 
                       background=self.color_card, 
                       relief='flat',
                       borderwidth=0)
        
        # Estilos de botones con mejor contraste
        style.configure('Primary.TButton',
                       font=self.font_subheader,
                       foreground='white',
                       background=self.color_primary,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(22, 12))
        
        style.map('Primary.TButton',
                 background=[('active', self.color_primary_dark), ('pressed', '#1e3a8a')],
                 relief=[('pressed', 'flat')])
        
        style.configure('Success.TButton',
                       font=self.font_subheader,
                       foreground='white',
                       background=self.color_success,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(22, 12))
        
        style.map('Success.TButton',
                 background=[('active', '#059669'), ('pressed', '#047857')])
        
        style.configure('Secondary.TButton',
                       font=self.font_normal,
                       foreground=self.color_text,
                       background=self.color_border,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(18, 10))
        
        style.map('Secondary.TButton',
                 background=[('active', '#94a3b8'), ('pressed', '#64748b')])
        
        # Estilo para Combobox
        style.configure('TCombobox', 
                       font=self.font_normal, 
                       padding=10,
                       fieldbackground='white',
                       background='white',
                       foreground=self.color_text,
                       arrowcolor=self.color_primary)
        
        style.map('Secondary.TButton',
                 background=[('active', '#d5dbdb'), ('pressed', '#bfc9ca')])
        
        style.configure('Accent.TButton',
                       font=self.font_subheader,
                       foreground='white',
                       background=self.color_accent,
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        # Estilos de frames
        style.configure('Card.TFrame', 
                       background='white',
                       relief='raised',
                       borderwidth=2)
        
        style.configure('TNotebook', 
                       background=self.color_bg,
                       borderwidth=0)
        
        style.configure('TNotebook.Tab', 
                       font=self.font_subheader,
                       padding=(20, 10),
                       background=self.color_bg)
        
        style.map('TNotebook.Tab',
                 background=[('selected', 'white')],
                 foreground=[('selected', self.color_primary)])
        
        # ComboBox
        style.configure('TCombobox',
                       fieldbackground='white',
                       background=self.color_primary,
                       foreground=self.color_text,
                       arrowcolor=self.color_primary)
        
        # Configurar color de fondo de la ventana
        self.root.configure(bg=self.color_bg)
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica principal responsive."""
        # Frame principal con grid
        main_frame = tk.Frame(self.root, bg=self.color_bg)
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configurar expansión responsive
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # ==================== HEADER MODERNO CON LOGOTIPOS ====================
        header_frame = tk.Frame(main_frame, bg=self.color_primary, height=100)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=2)
        header_frame.grid_columnconfigure(2, weight=1)
        
        # Logo IPN (izquierda) - mantener proporción
        try:
            logo_ipn_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'logo_ipn.png')
            logo_ipn_img = Image.open(logo_ipn_path)
            
            # Mantener aspect ratio, altura fija de 70px
            aspect_ratio = logo_ipn_img.width / logo_ipn_img.height
            new_height = 70
            new_width = int(new_height * aspect_ratio)
            
            logo_ipn_img = logo_ipn_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_ipn = ImageTk.PhotoImage(logo_ipn_img)
            
            logo_ipn_label = tk.Label(header_frame, image=self.logo_ipn, bg=self.color_primary)
            logo_ipn_label.grid(row=0, column=0, padx=20, pady=15, sticky='w')
        except Exception as e:
            print(f"No se pudo cargar logo IPN: {e}")
        
        # Contenedor del título (centro)
        title_container = tk.Frame(header_frame, bg=self.color_primary)
        title_container.grid(row=0, column=1, pady=15)
        
        # Título principal con diseño moderno
        titulo = tk.Label(title_container, 
                         text="🔐 NOTARIO DIGITAL",
                         font=('Segoe UI', 28, 'bold'),
                         fg='white',
                         bg=self.color_primary)
        titulo.pack(pady=(0, 5))
        
        # Subtítulo
        subtitulo = tk.Label(title_container, 
                           text="Sistema Criptográfico Multi-Curva • ECDSA + SHA-256",
                           font=('Segoe UI', 10),
                           fg='white',
                           bg=self.color_primary)
        subtitulo.pack()
        
        # Logo ESCOM (derecha) - mantener proporción
        try:
            logo_escom_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'logo_escom.png')
            logo_escom_img = Image.open(logo_escom_path)
            
            # Mantener aspect ratio, altura fija de 70px
            aspect_ratio = logo_escom_img.width / logo_escom_img.height
            new_height = 70
            new_width = int(new_height * aspect_ratio)
            
            logo_escom_img = logo_escom_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_escom = ImageTk.PhotoImage(logo_escom_img)
            
            logo_escom_label = tk.Label(header_frame, image=self.logo_escom, bg=self.color_primary)
            logo_escom_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        except Exception as e:
            print(f"No se pudo cargar logo ESCOM: {e}")
        
        # ==================== CONTENEDOR DE PESTAÑAS ====================
        notebook_container = tk.Frame(main_frame, bg=self.color_bg)
        notebook_container.grid(row=1, column=0, sticky='nsew', padx=25, pady=20)
        notebook_container.grid_rowconfigure(0, weight=1)
        notebook_container.grid_columnconfigure(0, weight=1)
        
        notebook = ttk.Notebook(notebook_container)
        notebook.grid(row=0, column=0, sticky='nsew')
        main_frame.rowconfigure(1, weight=1)
        
        # Pestaña 1: Notarizar
        self.crear_tab_notarizar(notebook)
        
        # Pestaña 2: Verificar
        self.crear_tab_verificar(notebook)
        
        # Pestaña 3: Gestión de Llaves
        self.crear_tab_gestion_llaves(notebook)
        
        # Pestaña 4: Información
        self.crear_tab_info(notebook)
        
        # ==================== BARRA DE ESTADO PROFESIONAL ====================
        status_frame = tk.Frame(main_frame, bg='white', height=45, relief=tk.FLAT, bd=0)
        status_frame.grid(row=2, column=0, sticky='ew')
        status_frame.grid_propagate(False)
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Línea separadora superior elegante
        separator = tk.Frame(status_frame, bg=self.color_border, height=2)
        separator.pack(fill=tk.X, side=tk.TOP)
        
        # Contenedor de estado con mejor diseño
        status_container = tk.Frame(status_frame, bg='white')
        status_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # Indicador visual de estado (punto de color grande)
        self.status_indicator = tk.Label(status_container, 
                                        text="●",
                                        font=('Segoe UI', 16),
                                        fg=self.color_warning,
                                        bg='white')
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 12))
        
        # Texto de estado con mejor tipografía
        self.status_var = tk.StringVar(value="⏳ Verificando conexión con el servidor...")
        status_label = tk.Label(status_container, 
                               textvariable=self.status_var,
                               font=self.font_normal,
                               bg='white',
                               fg=self.color_text,
                               anchor='w')
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def crear_tab_notarizar(self, notebook):
        """Crea la pestaña de notarización con diseño centrado, redondeado y dinámico."""
        tab = tk.Frame(notebook, bg=self.color_bg)
        notebook.add(tab, text="  📝 Notarizar Documento  ")
        
        # Configurar grid para responsive
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        # Contenedor principal con columnas para centrado perfecto
        main_container = tk.Frame(tab, bg=self.color_bg)
        main_container.grid(row=0, column=0, sticky='nsew')
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=0)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Espaciador izquierdo
        tk.Frame(main_container, bg=self.color_bg).grid(row=0, column=0, sticky='nsew')
        
        # Contenedor central con scroll (ancho fijo 850px para mejor centrado)
        center_frame = tk.Frame(main_container, bg=self.color_bg, width=850)
        center_frame.grid(row=0, column=1, sticky='ns', pady=20)
        center_frame.grid_propagate(False)
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(center_frame, bg=self.color_bg, highlightthickness=0, width=850)
        scrollbar = ttk.Scrollbar(center_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.color_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=830)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Espaciador derecho
        tk.Frame(main_container, bg=self.color_bg).grid(row=0, column=2, sticky='nsew')
        
        # Método auxiliar para crear tarjetas (simplificado sin canvas interno)
        def crear_card(parent, header_text, header_bg, icon="", pady_top=25):
            # Contenedor de la tarjeta
            card_container = tk.Frame(parent, bg=self.color_bg)
            card_container.pack(fill=tk.X, padx=20, pady=(pady_top, 0))
            
            # Tarjeta principal con borde
            card = tk.Frame(card_container, bg=self.color_card, 
                          highlightbackground=self.color_border,
                          highlightthickness=2,
                          relief='flat')
            card.pack(fill=tk.X, pady=(0, 5))
            
            # Header
            card_header = tk.Frame(card, bg=header_bg, height=65)
            card_header.pack(fill=tk.X)
            card_header.pack_propagate(False)
            
            # Contenido del header centrado
            header_content = tk.Frame(card_header, bg=header_bg)
            header_content.place(relx=0.5, rely=0.5, anchor='center')
            
            if icon:
                tk.Label(header_content, text=icon, 
                        font=('Segoe UI', 22),
                        foreground='white',
                        background=header_bg).pack(side=tk.LEFT, padx=(0, 12))
            
            tk.Label(header_content, text=header_text, 
                    font=('Segoe UI', 14, 'bold'),
                    foreground='white',
                    background=header_bg).pack(side=tk.LEFT)
            
            # Cuerpo de la tarjeta
            card_body = tk.Frame(card, bg=self.color_card)
            card_body.pack(fill=tk.BOTH, expand=True, padx=40, pady=35)
            
            return card_body
        
        # ========== CARD 1: Seleccionar Archivo ==========
        card1_body = crear_card(scrollable_frame, "PASO 1: Seleccionar Archivo", 
                                self.color_primary, "📂")
        
        # Contenedor centrado
        content1 = tk.Frame(card1_body, bg=self.color_card)
        content1.pack(expand=True)
        
        self.archivo_label = tk.Label(content1, 
                                      text="📄 Ningún archivo seleccionado",
                                      font=('Segoe UI', 11),
                                      foreground=self.color_text_secondary,
                                      bg=self.color_card)
        self.archivo_label.pack(pady=(0, 22))
        
        btn_seleccionar = tk.Button(content1,
                                    text="📂  Seleccionar Archivo",
                                    command=self.seleccionar_archivo,
                                    font=('Segoe UI', 12, 'bold'),
                                    foreground='white',
                                    background=self.color_primary,
                                    activebackground=self.color_primary_dark,
                                    activeforeground='white',
                                    borderwidth=0,
                                    padx=40,
                                    pady=15,
                                    cursor='hand2',
                                    relief='flat')
        btn_seleccionar.pack()
        
        # ========== CARD 2: Hash SHA-256 ==========
        card2_body = crear_card(scrollable_frame, "PASO 2: Hash Criptográfico", 
                                self.color_accent, "🔐", pady_top=20)
        
        tk.Label(card2_body,
                text="El hash SHA-256 del archivo se calcula automáticamente",
                font=('Segoe UI', 10),
                foreground=self.color_text_secondary,
                bg=self.color_card).pack(pady=(0, 18), anchor='center')
        
        self.hash_text = scrolledtext.ScrolledText(card2_body, 
                                                   height=3, 
                                                   font=self.font_mono,
                                                   wrap=tk.WORD,
                                                   state=tk.DISABLED,
                                                   bg=self.color_bg,
                                                   fg=self.color_text,
                                                   relief='solid',
                                                   borderwidth=1,
                                                   highlightthickness=0)
        self.hash_text.pack(fill=tk.X)
        
        # ========== CARD 3: Notarizar ==========
        card3_body = crear_card(scrollable_frame, "PASO 3: Notarizar Documento", 
                                self.color_success, "✍️", pady_top=20)
        
        # Contenedor centrado
        content3 = tk.Frame(card3_body, bg=self.color_card)
        content3.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(content3,
                text="Firma digital con ECDSA usando la curva elíptica seleccionada",
                font=('Segoe UI', 10),
                foreground=self.color_text_secondary,
                bg=self.color_card).pack(pady=(0, 22), anchor='center')
        
        self.btn_notarizar = tk.Button(content3,
                                       text="🔏  NOTARIZAR DOCUMENTO",
                                       command=self.notarizar_documento,
                                       font=('Segoe UI', 13, 'bold'),
                                       foreground='white',
                                       background=self.color_success,
                                       activebackground='#059669',
                                       activeforeground='white',
                                       borderwidth=0,
                                       padx=55,
                                       pady=20,
                                       cursor='hand2',
                                       state=tk.DISABLED,
                                       relief='flat')
        self.btn_notarizar.pack(pady=(0, 28))
        
        # Resultado con título
        result_header = tk.Frame(content3, bg=self.color_card)
        result_header.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(result_header,
                text="📄 Resultado de la Notarización",
                font=('Segoe UI', 12, 'bold'),
                foreground=self.color_text,
                bg=self.color_card).pack(side=tk.LEFT)
        
        self.resultado_notarizar = scrolledtext.ScrolledText(content3, 
                                                             height=11,
                                                             font=self.font_normal,
                                                             wrap=tk.WORD,
                                                             state=tk.DISABLED,
                                                             bg=self.color_bg,
                                                             fg=self.color_text,
                                                             relief='solid',
                                                             borderwidth=1,
                                                             highlightthickness=0)
        self.resultado_notarizar.pack(fill=tk.BOTH, expand=True)
        
        # Espacio inferior
        tk.Frame(scrollable_frame, bg=self.color_bg, height=35).pack()
        
        # Empaquetar canvas
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
    
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
    
    def crear_tab_gestion_llaves(self, notebook):
        """Crea la pestaña de gestión de llaves criptográficas."""
        tab = ttk.Frame(notebook, padding="15")
        notebook.add(tab, text="🔑 Gestión de Llaves")
        
        # Título
        ttk.Label(tab, text="Gestión de Llaves Criptográficas", style='Header.TLabel').grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 20)
        )
        
        # Sección: Selección de curva
        ttk.Label(tab, text="1. Seleccionar Curva Elíptica", style='Header.TLabel').grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        ttk.Label(tab, text="Elige la curva criptográfica para generar llaves:", 
                 style='Info.TLabel').grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=5
        )
        
        # ComboBox para seleccionar curva
        curvas_frame = ttk.Frame(tab)
        curvas_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(curvas_frame, text="Curva:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.curva_var = tk.StringVar(value="SECP256R1")
        curvas_nombres = [f"{codigo} - {info['nombre']}" for codigo, info in CURVAS_SOPORTADAS.items()]
        self.combo_curvas = ttk.Combobox(
            curvas_frame, 
            textvariable=self.curva_var,
            values=curvas_nombres,
            state="readonly",
            width=60
        )
        self.combo_curvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_curvas.bind("<<ComboboxSelected>>", self.on_curva_seleccionada)
        
        # Descripción de la curva seleccionada
        self.descripcion_curva_label = ttk.Label(tab, text="", 
                                                 style='Info.TLabel', 
                                                 wraplength=800)
        self.descripcion_curva_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        self.actualizar_descripcion_curva()
        
        # Separador
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        # Sección: Generar claves
        ttk.Label(tab, text="2. Generar Nuevo Par de Claves", style='Header.TLabel').grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        ttk.Label(tab, text="Genera un nuevo par de claves (privada/pública) con la curva seleccionada:", 
                 style='Info.TLabel').grid(
            row=7, column=0, columnspan=3, sticky=tk.W, pady=5
        )
        
        # Opciones de generación
        self.usar_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="Proteger clave privada con contraseña", 
                       variable=self.usar_password_var,
                       command=self.toggle_password_fields).grid(
            row=8, column=0, columnspan=3, sticky=tk.W, pady=5
        )
        
        # Frame para contraseña (inicialmente oculto)
        self.password_frame = ttk.Frame(tab)
        self.password_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.password_frame, text="Contraseña:", style='Info.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(20, 10)
        )
        self.password_entry = ttk.Entry(self.password_frame, show="*", width=30)
        self.password_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(self.password_frame, text="Confirmar:", style='Info.TLabel').grid(
            row=1, column=0, sticky=tk.W, padx=(20, 10), pady=(5, 0)
        )
        self.password_confirm_entry = ttk.Entry(self.password_frame, show="*", width=30)
        self.password_confirm_entry.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Ocultar inicialmente
        self.password_frame.grid_remove()
        
        # Botón generar
        ttk.Button(tab, text="🔑 Generar Nuevo Par de Claves", 
                  command=self.generar_claves,
                  style='Primary.TButton').grid(
            row=10, column=0, columnspan=3, pady=15
        )
        
        # Separador
        ttk.Separator(tab, orient=tk.HORIZONTAL).grid(
            row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15
        )
        
        # Sección: Claves existentes
        ttk.Label(tab, text="3. Claves Existentes", style='Header.TLabel').grid(
            row=12, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        # Lista de claves
        self.claves_text = scrolledtext.ScrolledText(tab, height=8, width=80, 
                                                     wrap=tk.WORD, state=tk.DISABLED)
        self.claves_text.grid(row=13, column=0, columnspan=3, 
                             sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Button(tab, text="🔄 Actualizar Lista de Claves", 
                  command=self.listar_claves,
                  style='Secondary.TButton').grid(
            row=14, column=0, columnspan=3, pady=5
        )
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(13, weight=1)
        
        # Cargar lista inicial
        self.listar_claves()
    
    def on_curva_seleccionada(self, event=None):
        """Manejador del evento de selección de curva."""
        seleccion = self.curva_var.get()
        # Extraer código de curva (formato: "CODIGO - Nombre")
        self.curva_seleccionada = seleccion.split(" - ")[0]
        self.actualizar_descripcion_curva()
        self.status_var.set(f"Curva seleccionada: {self.curva_seleccionada}")
    
    def actualizar_descripcion_curva(self):
        """Actualiza la descripción de la curva seleccionada."""
        if self.curva_seleccionada in CURVAS_SOPORTADAS:
            info = CURVAS_SOPORTADAS[self.curva_seleccionada]
            descripcion = f"📘 {info['descripcion']}"
            self.descripcion_curva_label.config(text=descripcion)
    
    def toggle_password_fields(self):
        """Muestra u oculta los campos de contraseña."""
        if self.usar_password_var.get():
            self.password_frame.grid()
        else:
            self.password_frame.grid_remove()
    
    def generar_claves(self):
        """Genera un nuevo par de claves con la curva seleccionada."""
        try:
            # Validar contraseña si está habilitada
            password = None
            if self.usar_password_var.get():
                password = self.password_entry.get()
                confirm = self.password_confirm_entry.get()
                
                if not password:
                    messagebox.showwarning("Advertencia", "Debes ingresar una contraseña")
                    return
                
                if password != confirm:
                    messagebox.showerror("Error", "Las contraseñas no coinciden")
                    return
            
            # Confirmar generación
            respuesta = messagebox.askyesno(
                "Confirmar Generación",
                f"¿Deseas generar un nuevo par de claves usando {self.curva_seleccionada}?\n\n"
                f"Las claves se guardarán en:\n{self.keys_dir}"
            )
            
            if not respuesta:
                return
            
            self.status_var.set(f"Generando claves {self.curva_seleccionada}...")
            
            # Crear instancia de crypto con la curva seleccionada
            crypto = NotarioCrypto(curva=self.curva_seleccionada)
            crypto.generar_par_claves()
            
            # Rutas de archivo
            private_path = os.path.join(self.keys_dir, f'notario_private_{self.curva_seleccionada.lower()}.pem')
            public_path = os.path.join(self.keys_dir, f'notario_public_{self.curva_seleccionada.lower()}.pem')
            
            # Guardar claves
            crypto.guardar_clave_privada(private_path, password)
            crypto.guardar_clave_publica(public_path)
            
            # Limpiar campos de contraseña
            self.password_entry.delete(0, tk.END)
            self.password_confirm_entry.delete(0, tk.END)
            
            self.status_var.set(f"✅ Claves {self.curva_seleccionada} generadas exitosamente")
            messagebox.showinfo(
                "Éxito",
                f"Claves generadas exitosamente\n\n"
                f"Curva: {self.curva_seleccionada}\n"
                f"Privada: {os.path.basename(private_path)}\n"
                f"Pública: {os.path.basename(public_path)}\n\n"
                f"⚠️ IMPORTANTE: Guarda la clave privada en un lugar seguro."
            )
            
            # Actualizar lista
            self.listar_claves()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando claves: {str(e)}")
            self.status_var.set("❌ Error generando claves")
    
    def listar_claves(self):
        """Lista todas las claves existentes en el directorio."""
        try:
            self.claves_text.config(state=tk.NORMAL)
            self.claves_text.delete('1.0', tk.END)
            
            if not os.path.exists(self.keys_dir):
                self.claves_text.insert('1.0', "No hay directorio de claves aún.")
                self.claves_text.config(state=tk.DISABLED)
                return
            
            archivos = os.listdir(self.keys_dir)
            claves_privadas = [f for f in archivos if f.endswith('.pem') and 'private' in f.lower()]
            claves_publicas = [f for f in archivos if f.endswith('.pem') and 'public' in f.lower()]
            
            if not claves_privadas and not claves_publicas:
                self.claves_text.insert('1.0', "No hay claves generadas aún.\n\nGenera un nuevo par usando el botón de arriba.")
            else:
                texto = "CLAVES ENCONTRADAS:\n"
                texto += "=" * 70 + "\n\n"
                
                # Agrupar por curva
                curvas_encontradas = set()
                for archivo in claves_privadas + claves_publicas:
                    for curva in CURVAS_SOPORTADAS.keys():
                        if curva.lower() in archivo.lower():
                            curvas_encontradas.add(curva)
                
                for curva in sorted(curvas_encontradas):
                    texto += f"🔑 {curva} - {CURVAS_SOPORTADAS[curva]['nombre']}\n"
                    
                    priv = f"notario_private_{curva.lower()}.pem"
                    pub = f"notario_public_{curva.lower()}.pem"
                    
                    if priv in claves_privadas:
                        ruta_completa = os.path.join(self.keys_dir, priv)
                        tamaño = os.path.getsize(ruta_completa)
                        texto += f"   🔒 Privada: {priv} ({tamaño} bytes)\n"
                    
                    if pub in claves_publicas:
                        ruta_completa = os.path.join(self.keys_dir, pub)
                        tamaño = os.path.getsize(ruta_completa)
                        texto += f"   🔓 Pública: {pub} ({tamaño} bytes)\n"
                    
                    texto += "\n"
                
                texto += "=" * 70 + "\n"
                texto += f"\nDirectorio: {self.keys_dir}"
                
                self.claves_text.insert('1.0', texto)
            
            self.claves_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.claves_text.config(state=tk.NORMAL)
            self.claves_text.delete('1.0', tk.END)
            self.claves_text.insert('1.0', f"Error listando claves: {str(e)}")
            self.claves_text.config(state=tk.DISABLED)
    
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
utilizando criptografía de curva elíptica (ECDSA) con soporte para
múltiples curvas estándar.

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

🛡️ SEGURIDAD - CURVAS SOPORTADAS

El sistema ahora soporta múltiples curvas elípticas estándar:

• SECP256R1 (NIST P-256): Curva estándar usada globalmente para TLS/SSL
  - 256 bits de seguridad
  - Ampliamente adoptada y probada

• SECP256K1: La curva usada en Bitcoin y otras criptomonedas
  - 256 bits de seguridad
  - Óptima para aplicaciones blockchain

• SECP384R1 (NIST P-384): Curva de mayor seguridad
  - 384 bits de seguridad
  - Recomendada para información clasificada

• SECP521R1 (NIST P-521): Máxima seguridad
  - 521 bits de seguridad
  - Mayor nivel de protección disponible

Hash: SHA-256 (256 bits de seguridad) en todas las curvas
Clave privada: Protegida en el servidor, nunca expuesta
Firmas: Matemáticamente imposibles de falsificar sin la clave privada

═══════════════════════════════════════════════════════════════

📝 CASOS DE USO

✓ Protección de propiedad intelectual
✓ Contratos digitales
✓ Código fuente y desarrollo de software
✓ Arte digital y NFTs
✓ Documentos legales
✓ Registros académicos
✓ Transacciones blockchain (con SECP256K1)
✓ Cualquier archivo que requiera certificación temporal

═══════════════════════════════════════════════════════════════

🔑 GESTIÓN DE LLAVES

La pestaña "Gestión de Llaves" te permite:

• Seleccionar entre diferentes curvas elípticas
• Generar nuevos pares de claves para cada curva
• Proteger claves privadas con contraseña
• Ver todas las claves existentes en el sistema

Cada curva tiene su propio par de claves independiente.

═══════════════════════════════════════════════════════════════

🔑 CONCEPTOS CLAVE

• Hash SHA-256: Una "huella digital" única de 64 caracteres que
  identifica unívocamente un archivo. Cualquier cambio en el archivo,
  por mínimo que sea, produce un hash completamente diferente.

• Firma Digital ECDSA: Una firma matemática que solo puede ser creada
  por quien posee la clave privada, pero que cualquiera puede verificar
  con la clave pública.

• Curva Elíptica: Base matemática para generar claves y firmas. 
  Diferentes curvas ofrecen diferentes niveles de seguridad y 
  compatibilidad con estándares específicos.

• Timestamp: Marca de tiempo certificada que prueba que el hash existía
  en ese momento específico.

═══════════════════════════════════════════════════════════════

📖 CÓMO USAR

NOTARIZAR:
1. Ve a la pestaña "Gestión de Llaves" y selecciona la curva deseada
2. Genera claves para esa curva si aún no existen
3. En "Notarizar", selecciona el archivo que deseas notarizar
4. El sistema calculará automáticamente su hash SHA-256
5. Click en "Notarizar Documento" (usará la curva seleccionada)
6. Guarda el recibo digital (.json) que se genera

VERIFICAR:
1. Carga el recibo digital (.json)
2. Selecciona el archivo original
3. Click en "Verificar Autenticidad"
4. El sistema confirmará si el archivo es auténtico
   (detecta automáticamente la curva del recibo)

═══════════════════════════════════════════════════════════════

⚠️ IMPORTANTE

• Guarda siempre tus recibos en un lugar seguro
• Un recibo solo es válido para el archivo específico que se notarizó
• Si el archivo cambia aunque sea un bit, la verificación fallará
• La clave privada del notario nunca debe ser compartida
• Cada curva requiere su propio par de claves
• El recibo incluye información sobre qué curva se usó

═══════════════════════════════════════════════════════════════

Desarrollado con Python, cryptography.io, FastAPI y tkinter
Versión 2.0 - Soporte Multi-Curva
"""
        
        info_text.insert('1.0', contenido)
        info_text.config(state=tk.DISABLED)
    
    def verificar_servidor(self):
        """Verifica la conexión con el servidor API."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                self.status_var.set("🟢 Conectado al servidor • Listo para operar")
                self.status_indicator.config(fg=self.color_success)
            else:
                self.status_var.set("⚠️ Servidor respondió con error")
                self.status_indicator.config(fg=self.color_warning)
        except requests.exceptions.ConnectionError:
            self.status_var.set("🔴 No conectado • Inicia el servidor con: python server/api_server.py")
            self.status_indicator.config(fg=self.color_danger)
            messagebox.showwarning(
                "Servidor no disponible",
                "No se puede conectar al servidor API.\n\n"
                "Asegúrate de iniciar el servidor ejecutando:\n"
                "python server/api_server.py"
            )
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
            self.status_indicator.config(fg=self.color_danger)
    
    def seleccionar_archivo(self):
        """Permite al usuario seleccionar un archivo para notarizar."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo para notarizar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if filename:
            self.archivo_actual = filename
            nombre_archivo = os.path.basename(filename)
            
            # Actualizar label con estilo
            self.archivo_label.config(
                text=f"✓ {nombre_archivo}",
                foreground=self.color_success,
                font=self.font_subheader
            )
            
            self.status_var.set("⏳ Calculando hash SHA-256...")
            self.status_indicator.config(fg=self.color_warning)
            
            # Calcular hash
            try:
                self.hash_actual = self.crypto.calcular_hash_archivo(filename)
                
                # Mostrar hash con formato
                self.hash_text.config(state=tk.NORMAL)
                self.hash_text.delete('1.0', tk.END)
                self.hash_text.insert('1.0', self.hash_actual)
                self.hash_text.config(state=tk.DISABLED)
                
                # Habilitar botón de notarizar
                self.btn_notarizar.config(state=tk.NORMAL, 
                                         background=self.color_success,
                                         activebackground='#059669')
                
                self.status_var.set(f"✅ Hash calculado • Archivo listo para notarizar")
                self.status_indicator.config(fg=self.color_success)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error calculando hash: {str(e)}")
                self.status_var.set("❌ Error calculando hash")
                self.status_indicator.config(fg=self.color_danger)
    
    def notarizar_documento(self):
        """Envía el hash al servidor para notarizar."""
        if not self.hash_actual:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo")
            return
        
        try:
            self.status_var.set("⏳ Notarizando documento...")
            self.status_indicator.config(fg=self.color_warning)
            
            # Enviar solicitud al servidor con la curva seleccionada
            response = requests.post(
                f"{self.api_url}/notarizar",
                json={
                    "hash": self.hash_actual,
                    "curva": self.curva_seleccionada
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Guardar recibo
                timestamp_str = data['timestamp'].replace(':', '-').replace('.', '-')
                nombre_archivo = os.path.basename(self.archivo_actual)
                curva = data.get('curva', 'SECP256R1')
                nombre_recibo = f"recibo_{nombre_archivo}_{curva}_{timestamp_str}.json"
                ruta_recibo = os.path.join(self.receipts_dir, nombre_recibo)
                
                recibo = {
                    "timestamp": data['timestamp'],
                    "hash": data['hash'],
                    "firma": data['firma'],
                    "curva": curva,
                    "archivo_original": nombre_archivo
                }
                
                guardar_recibo(recibo, ruta_recibo)
                
                info_curva = CURVAS_SOPORTADAS.get(curva, {})
                nombre_curva = info_curva.get('nombre', curva)
                
                # Mostrar resultado con formato moderno
                resultado = f"""
✅ DOCUMENTO NOTARIZADO EXITOSAMENTE

📁 Archivo: {nombre_archivo}
🔐 Hash SHA-256: {data['hash']}
⏰ Timestamp: {data['timestamp']}
📊 Curva: {nombre_curva}
✍️ Firma Digital: {data['firma'][:64]}...

📄 Recibo guardado en:
{nombre_recibo}

⚠️ IMPORTANTE: Guarda este recibo en un lugar seguro.
Es la prueba de que este documento existía en este momento.
"""
                
                self.resultado_notarizar.config(state=tk.NORMAL)
                self.resultado_notarizar.delete('1.0', tk.END)
                self.resultado_notarizar.insert('1.0', resultado)
                self.resultado_notarizar.config(state=tk.DISABLED)
                
                self.status_var.set(f"✅ Documento notarizado con {nombre_curva}")
                self.status_indicator.config(fg=self.color_success)
                messagebox.showinfo("¡Éxito!", 
                                  f"✅ Documento notarizado con {nombre_curva}\n\n"
                                  f"📄 Recibo guardado:\n{nombre_recibo}")
                
            else:
                error = response.json().get('detail', 'Error desconocido')
                messagebox.showerror("Error", f"Error del servidor: {error}")
                self.status_var.set("❌ Error en notarización")
                self.status_indicator.config(fg=self.color_danger)
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", 
                               "No se puede conectar al servidor.\n"
                               "Asegúrate de que el servidor esté ejecutándose.")
            self.status_var.set("❌ Error de conexión")
            self.status_indicator.config(fg=self.color_danger)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("❌ Error en notarización")
            self.status_indicator.config(fg=self.color_danger)
    
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
                self.recibo_label.config(text=f"✓ {nombre_recibo}",
                                        foreground=self.color_success,
                                        font=self.font_subheader)
                self.status_var.set("✅ Recibo cargado correctamente")
                self.status_indicator.config(fg=self.color_success)
                self.actualizar_estado_verificar()
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando recibo: {str(e)}")
                self.status_var.set("❌ Error cargando recibo")
                self.status_indicator.config(fg=self.color_danger)
    
    def seleccionar_archivo_verificar(self):
        """Selecciona el archivo a verificar contra el recibo."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo a verificar",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if filename:
            self.archivo_verificar = filename
            nombre_archivo = os.path.basename(filename)
            self.archivo_verificar_label.config(text=f"✓ {nombre_archivo}",
                                               foreground=self.color_success,
                                               font=self.font_subheader)
            self.status_var.set("✅ Archivo seleccionado para verificar")
            self.status_indicator.config(fg=self.color_success)
            self.actualizar_estado_verificar()
    
    def actualizar_estado_verificar(self):
        """Actualiza el estado del botón de verificar."""
        if hasattr(self, 'recibo_actual') and hasattr(self, 'archivo_verificar'):
            if self.recibo_actual and self.archivo_verificar:
                self.btn_verificar.config(state=tk.NORMAL,
                                         background=self.color_accent,
                                         activebackground='#8e44ad')
    
    def verificar_recibo(self):
        """Verifica la autenticidad del recibo contra el archivo."""
        if not self.recibo_actual or not hasattr(self, 'archivo_verificar'):
            messagebox.showwarning("Advertencia", "Carga un recibo y selecciona un archivo")
            return
        
        try:
            self.status_var.set("⏳ Verificando recibo...")
            self.status_indicator.config(fg=self.color_warning)
            
            # Calcular hash del archivo
            hash_archivo = self.crypto.calcular_hash_archivo(self.archivo_verificar)
            
            # Verificar que el hash coincida
            if hash_archivo.lower() != self.recibo_actual['hash'].lower():
                resultado = f"""
❌ VERIFICACIÓN FALLIDA

El archivo NO corresponde al recibo.

🔐 Hash del archivo actual: 
{hash_archivo}

📄 Hash en el recibo: 
{self.recibo_actual['hash']}

⚠️ POSIBLES CAUSAS:
• El archivo ha sido modificado
• El recibo no corresponde a este archivo
• El archivo está corrupto
"""
                self.resultado_verificar.config(state=tk.NORMAL)
                self.resultado_verificar.delete('1.0', tk.END)
                self.resultado_verificar.insert('1.0', resultado)
                self.resultado_verificar.config(state=tk.DISABLED)
                
                self.status_var.set("❌ Verificación fallida • Hash no coincide")
                self.status_indicator.config(fg=self.color_danger)
                messagebox.showwarning("Verificación Fallida", 
                                     "❌ El archivo NO corresponde al recibo.\n\n"
                                     "El hash no coincide.")
                return
            
            # Obtener curva del recibo (por defecto SECP256R1 para compatibilidad)
            curva = self.recibo_actual.get('curva', 'SECP256R1')
            info_curva = CURVAS_SOPORTADAS.get(curva, {})
            nombre_curva = info_curva.get('nombre', curva)
            
            # Enviar a servidor para verificar firma
            response = requests.post(
                f"{self.api_url}/verificar",
                json={
                    "timestamp": self.recibo_actual['timestamp'],
                    "hash": self.recibo_actual['hash'],
                    "firma": self.recibo_actual['firma'],
                    "curva": curva
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['valido']:
                    resultado = f"""
✅ RECIBO AUTÉNTICO Y VÁLIDO

El recibo es legítimo y el archivo no ha sido alterado.

📁 Archivo: {os.path.basename(self.archivo_verificar)}
🔐 Hash SHA-256: {self.recibo_actual['hash']}
⏰ Timestamp: {self.recibo_actual['timestamp']}
📊 Curva: {nombre_curva}
✍️ Firma Digital: ✓ Verificada

🔐 CONFIRMACIÓN:
• El archivo existía en la fecha indicada
• El archivo NO ha sido modificado desde entonces
• La firma digital es auténtica del Notario
• El recibo NO ha sido falsificado

✓ Este documento tiene validez probatoria.
"""
                    self.status_var.set(f"✅ Recibo VÁLIDO ({nombre_curva}) • Documento auténtico")
                    self.status_indicator.config(fg=self.color_success)
                    messagebox.showinfo("Verificación Exitosa", 
                                      f"✅ RECIBO AUTÉNTICO\n\n"
                                      f"El documento es válido y no ha sido alterado.\n\n"
                                      f"Curva: {nombre_curva}")
                else:
                    resultado = f"""
❌ RECIBO INVÁLIDO

La firma digital NO es válida.

🔐 Hash: {self.recibo_actual['hash']}
⏰ Timestamp: {self.recibo_actual['timestamp']}
📊 Curva: {nombre_curva}
✍️ Firma: ❌ NO verificada

⚠️ ADVERTENCIA:
• El recibo ha sido alterado
• La firma no corresponde al Notario
• El recibo puede ser fraudulento

NO confíes en este recibo.
"""
                    self.status_var.set("❌ Recibo INVÁLIDO • Firma no verificada")
                    self.status_indicator.config(fg=self.color_danger)
                    messagebox.showerror("Verificación Fallida", 
                                       f"❌ RECIBO INVÁLIDO\n\n"
                                       f"La firma digital no es válida.\n"
                                       f"Curva: {nombre_curva}")
                
                self.resultado_verificar.config(state=tk.NORMAL)
                self.resultado_verificar.delete('1.0', tk.END)
                self.resultado_verificar.insert('1.0', resultado)
                self.resultado_verificar.config(state=tk.DISABLED)
                
            else:
                error = response.json().get('detail', 'Error desconocido')
                messagebox.showerror("Error", f"Error del servidor: {error}")
                self.status_var.set("❌ Error en verificación")
                self.status_indicator.config(fg=self.color_danger)
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", 
                               "No se puede conectar al servidor.\n"
                               "Asegúrate de que el servidor esté ejecutándose.")
            self.status_var.set("❌ Error de conexión")
            self.status_indicator.config(fg=self.color_danger)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
            self.status_var.set("❌ Error en verificación")
            self.status_indicator.config(fg=self.color_danger)


def main():
    """Función principal para iniciar la aplicación."""
    root = tk.Tk()
    app = NotarioDigitalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
