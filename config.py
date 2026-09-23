import os
from pathlib import Path

# Directorios principales del sistema en la carpeta Documentos del usuario
DOCUMENTS_DIR = Path(os.path.expanduser("~")) / "Documents" / "Facturas_Sublimacion"
PDF_STORAGE_DIR = DOCUMENTS_DIR / "Facturas_PDF"
BACKUP_STORAGE_DIR = DOCUMENTS_DIR / "Backups"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DB_PATH = DOCUMENTS_DIR / "sublimacion_pos.db"

# Asegurar que las carpetas existan sin necesidad de permisos especiales
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Paleta de Colores de Carga Cromática Baja (Inspirada en Stitch - Atelier Print Engine)
# Base neutra: Slate / Grises Pizarra + Acento funcional: Deep Teal
COLORS = {
    # Fondos y superficies
    "bg_dark": "#0F172A",          # Slate 900 (Fondo principal o sidebar)
    "sidebar_bg": "#1E293B",       # Slate 800 (Sidebar lateral)
    "card_bg": "#1E293B",          # Slate 800 (Tarjetas en tema oscuro)
    "card_bg_light": "#FFFFFF",    # Superficie blanca para tema claro
    "surface_alt": "#334155",      # Slate 700 (Separadores, inputs inactivos)
    "border": "#475569",           # Slate 600 (Bordes definidos)
    "border_light": "#CBD5E1",     # Slate 300 (Bordes claros)

    # Textos
    "text_primary": "#F8FAFC",     # Slate 50 (Texto de alto contraste)
    "text_secondary": "#94A3B8",   # Slate 400 (Etiquetas y subtítulos)
    "text_dark": "#0F172A",        # Slate 900 para fondos claros

    # Acentos (1 color principal y sus tonos + tonos neutros)
    "primary": "#0F766E",          # Deep Teal (Acción principal, confirmar, botones)
    "primary_hover": "#115E59",    # Deep Teal Oscuro (Hover)
    "primary_subtle": "#134E4A",   # Deep Teal Muy Oscuro
    
    # Secundario / Acciones de apoyo
    "secondary": "#334155",        # Slate intermedio
    "secondary_hover": "#475569",
    
    # Estados funcionales
    "success": "#059669",          # Esmeralda discreto
    "warning": "#D97706",          # Ámbar discreto
    "danger": "#DC2626",           # Rojo para eliminar/cancelar
    "danger_hover": "#B91C1C",
}

# Dimensiones y Ergonomía
SIZES = {
    "btn_height_large": 52,        # Botón extra grande para fácil uso / táctil
    "btn_height_medium": 44,       # Botones estándar
    "btn_height_small": 34,        # Botones de fila / acciones
    "corner_radius": 6,            # Bordes redondeados sutiles (Modern Utilitarian)
    "input_height": 42,            # Inputs cómodos y espaciosos
}

# Tipografía predeterminada
FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 10),
    "metric": ("Segoe UI", 26, "bold"),
    "currency": ("Consolas", 15, "bold"),
}
