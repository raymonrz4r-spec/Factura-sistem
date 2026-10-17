"""
SISTEMA DE FACTURACION PARA TALLER DE SUBLIMACION (main.py)

EXPLICACION PARA PERSONAS NO TECNICAS:
Este archivo es el punto de partida de todo el programa de escritorio.
Cuando el usuario hace doble clic en el icono para abrir la aplicacion,
este codigo se encarga de:

1. Armar la Ventana: Abre la ventana principal con un diseño oscuro y elegante
   que no cansa la vista durante horas de trabajo.
2. Iniciar en Facturacion Directa: Para ahorrar tiempo en el negocio, no pide
   claves al abrir; te lleva directo a cobrar y crear una nueva factura.
3. El Menu Lateral (Sidebar): Organiza los accesos a 'Factura', 'Historial',
   'Dashboard (Metricas)' y 'Ajustes del Taller'.
4. Guardian de Respaldos (Backup): Revisa en silencio si han pasado mas de
   7 dias desde la ultima copia de seguridad. Si es asi, crea un respaldo
   automatico de toda la base de datos para no perder dinero ni registros.
"""

import sys
import os
import customtkinter as ctk
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import COLORS, FONTS
from database import DatabaseManager
from services import BackupService
from ui import Sidebar
from ui.views import InvoiceView, HistoryView, DashboardView, SettingsView

class SublimacionFacturaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración básica de ventana
        self.title("Sistema de Facturación - Taller de Sublimación")
        self.geometry("1240x780")
        self.minsize(1080, 680)

        # Apariencia sobria de carga cromática baja
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=COLORS["bg_dark"])

        # Inicialización de servicios y datos
        self.db_manager = DatabaseManager()
        self.backup_service = BackupService(self.db_manager)

        # Estructura de layout: Sidebar (izq) y Contenedor de Vistas (der)
        self.sidebar = Sidebar(self, on_navigate_callback=self.cambiar_vista, db_manager=self.db_manager)
        self.sidebar.pack(side="left", fill="y")

        # Conectar callback de backup para actualizar la etiqueta del sidebar
        self.backup_service.set_callback(self.sidebar.refrescar_ultimo_backup)

        # Contenedor principal donde se cargan las vistas
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=16, pady=16)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # Inicializar vistas
        self.vistas = {}
        self.inicializar_vistas()

        # Verificar y ejecutar backup semanal automático si corresponde (> 7 días)
        self.after(500, self.verificar_backup_semanal)

        # Iniciar directamente en la pantalla de Facturación (Requisito explícito)
        self.cambiar_vista("factura")

    def inicializar_vistas(self):
        # 1. Facturación (Inicio inmediato)
        self.vistas["factura"] = InvoiceView(
            self.content_frame,
            self.db_manager,
            on_invoice_created_callback=self.al_crear_factura
        )
        self.vistas["factura"].grid(row=0, column=0, sticky="nsew")

        # 2. Dashboard / Reportes
        self.vistas["dashboard"] = DashboardView(
            self.content_frame,
            self.db_manager
        )
        self.vistas["dashboard"].grid(row=0, column=0, sticky="nsew")

        # 3. Historial de Facturas
        self.vistas["historial"] = HistoryView(
            self.content_frame,
            self.db_manager
        )
        self.vistas["historial"].grid(row=0, column=0, sticky="nsew")

        # 4. Configuración & Backup
        self.vistas["configuracion"] = SettingsView(
            self.content_frame,
            self.db_manager,
            self.backup_service,
            on_config_updated_callback=self.al_actualizar_config
        )
        self.vistas["configuracion"].grid(row=0, column=0, sticky="nsew")

    def cambiar_vista(self, nombre_vista):
        if nombre_vista in self.vistas:
            # Traer al frente la vista seleccionada
            vista = self.vistas[nombre_vista]
            vista.tkraise()

            # Refrescar datos según la vista
            if nombre_vista == "dashboard":
                vista.cargar_datos()
            elif nombre_vista == "historial":
                vista.cargar_facturas()
            elif nombre_vista == "factura":
                vista.cargar_siguiente_numero()

    def al_crear_factura(self):
        # Refrescar historial y dashboard cuando se emite una nueva factura
        if "historial" in self.vistas:
            self.vistas["historial"].cargar_facturas()
        if "dashboard" in self.vistas:
            self.vistas["dashboard"].cargar_datos()

    def al_actualizar_config(self):
        # Refrescar cálculos y datos si cambia moneda o ITBIS
        if "factura" in self.vistas:
            self.vistas["factura"].recalcular_totales()
            self.vistas["factura"].refrescar_tabla_items()

    def verificar_backup_semanal(self):
        ejecutado, archivo, fecha = self.backup_service.verificar_y_ejecutar_backup_semanal()
        if ejecutado:
            print(f"[Backup Semanal Automático] Creado con éxito en: {archivo} ({fecha})")
            self.sidebar.refrescar_ultimo_backup(fecha)
        else:
            self.sidebar.refrescar_ultimo_backup()

def main():
    app = SublimacionFacturaApp()
    app.mainloop()

if __name__ == "__main__":
    main()
