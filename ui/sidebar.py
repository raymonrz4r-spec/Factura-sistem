import customtkinter as ctk
from config import COLORS, SIZES, FONTS

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate_callback, db_manager):
        super().__init__(parent, fg_color=COLORS["sidebar_bg"], corner_radius=0, width=240)
        self.on_navigate_callback = on_navigate_callback
        self.db_manager = db_manager
        self.botones_nav = {}
        self.vista_actual = "factura"

        self.crear_interfaz()
        self.refrescar_ultimo_backup()

    def crear_interfaz(self):
        # Evitar que el frame se reduzca
        self.pack_propagate(False)

        # 1. Cabecera / Identidad de la Marca
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(24, 20))

        lbl_logo_icon = ctk.CTkLabel(
            brand_frame,
            text="🖨️  SUBLI-CORE",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_logo_icon.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="Taller de Sublimación & POS",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        lbl_sub.pack(anchor="w")

        # Separador superior
        sep1 = ctk.CTkFrame(self, height=1, fg_color=COLORS["border"])
        sep1.pack(fill="x", padx=16, pady=(0, 16))

        # 2. Botones de Navegación
        nav_items = [
            ("factura", "📄  Nueva Factura"),
            ("dashboard", "📊  Dashboard / Ventas"),
            ("historial", "📜  Historial de Facturas"),
            ("configuracion", "⚙️  Configuración & Logo"),
        ]

        for clave, texto in nav_items:
            btn = ctk.CTkButton(
                self,
                text=texto,
                font=FONTS["body_bold"],
                height=SIZES["btn_height_medium"],
                anchor="w",
                corner_radius=SIZES["corner_radius"],
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["surface_alt"],
                command=lambda c=clave: self.seleccionar_vista(c)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.botones_nav[clave] = btn

        # Marcar la primera vista (Factura) como activa por defecto
        self.resaltar_boton_activo("factura")

        # 3. Espaciador flexible para empujar el footer al fondo
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # 4. Sección Inferior: ESTADO DEL ÚLTIMO BACKUP (Requisito explícito del cliente)
        footer_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=SIZES["corner_radius"])
        footer_frame.pack(fill="x", padx=12, pady=16)

        header_bkp = ctk.CTkFrame(footer_frame, fg_color="transparent")
        header_bkp.pack(fill="x", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            header_bkp,
            text="🔄  Copia de Seguridad",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["primary"]
        ) .pack(side="left")

        # Etiqueta de la fecha del último backup
        self.lbl_ultimo_backup = ctk.CTkLabel(
            footer_frame,
            text="Último backup:\nCargando...",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.lbl_ultimo_backup.pack(anchor="w", padx=12, pady=(0, 10))

    def seleccionar_vista(self, clave):
        self.vista_actual = clave
        self.resaltar_boton_activo(clave)
        if self.on_navigate_callback:
            self.on_navigate_callback(clave)

    def resaltar_boton_activo(self, clave_activa):
        for clave, btn in self.botones_nav.items():
            if clave == clave_activa:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color=COLORS["text_primary"],
                    hover_color=COLORS["primary_hover"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["surface_alt"]
                )

    def refrescar_ultimo_backup(self, fecha_backup=None):
        if not fecha_backup:
            fecha_backup = self.db_manager.obtener_ultimo_backup()

        if fecha_backup:
            self.lbl_ultimo_backup.configure(text=f"Último backup:\n{fecha_backup}")
        else:
            self.lbl_ultimo_backup.configure(text="Último backup:\nSin backups aún")
