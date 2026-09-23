import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from config import COLORS, SIZES, FONTS
from services.pdf_generator import PDFGenerator

class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.pdf_generator = PDFGenerator(db_manager)
        self.crear_interfaz()
        self.cargar_facturas()

    def crear_interfaz(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # 1. Barra Superior con Título y Buscador
        top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        lbl_tit = ctk.CTkLabel(top_bar, text="📜 Historial de Facturas Emitidas", font=FONTS["title"], text_color=COLORS["text_primary"])
        lbl_tit.pack(side="left", padx=20, pady=16)

        # Buscador y botón refrescar
        btn_refresh = ctk.CTkButton(
            top_bar,
            text="🔄 Actualizar",
            width=100,
            height=SIZES["btn_height_small"],
            font=FONTS["body_bold"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            command=self.cargar_facturas
        )
        btn_refresh.pack(side="right", padx=(10, 20), pady=16)

        self.entry_busqueda = ctk.CTkEntry(
            top_bar,
            placeholder_text="Buscar por número o cliente...",
            width=280,
            height=SIZES["input_height"],
            font=FONTS["body"],
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"]
        )
        self.entry_busqueda.pack(side="right", padx=10, pady=16)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.cargar_facturas())

        # 2. Cabecera de la tabla de historial
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["surface_alt"], height=38, corner_radius=4)
        header_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))

        cols = [
            ("No. Factura", 120, "center"),
            ("Fecha y Hora", 160, "center"),
            ("Cliente", 260, "w"),
            ("Método Pago", 130, "center"),
            ("Total Facturado", 140, "e"),
            ("Acciones", 150, "center")
        ]

        for name, width, align in cols:
            lbl = ctk.CTkLabel(header_frame, text=name, font=FONTS["body_bold"], text_color=COLORS["text_primary"], width=width, anchor=align)
            lbl.pack(side="left", padx=5, pady=4)

        # 3. Lista con scroll para facturas
        self.scroll_historial = ctk.CTkScrollableFrame(self, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        self.scroll_historial.grid(row=2, column=0, sticky="nsew")

    def cargar_facturas(self):
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()

        termino = self.entry_busqueda.get().strip()
        facturas = self.db_manager.obtener_facturas(termino)

        if not facturas:
            lbl_empty = ctk.CTkLabel(
                self.scroll_historial,
                text="No se encontraron facturas registradas.",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            )
            lbl_empty.pack(pady=50)
            return

        cfg = self.db_manager.obtener_config()
        simbolo = cfg.get('moneda_simbolo', '$')

        for idx, f in enumerate(facturas):
            bg = COLORS["card_bg"] if idx % 2 == 0 else COLORS["surface_alt"]
            row = ctk.CTkFrame(self.scroll_historial, fg_color=bg, height=48, corner_radius=4)
            row.pack(fill="x", pady=2, padx=4)

            # Factura #
            ctk.CTkLabel(row, text=f['numero_factura'], font=FONTS["body_bold"], text_color=COLORS["primary"], width=120, anchor="center").pack(side="left", padx=5)

            # Fecha
            ctk.CTkLabel(row, text=f['fecha_hora'], font=FONTS["body"], width=160, anchor="center").pack(side="left", padx=5)

            # Cliente
            cliente_str = f['cliente_nombre'] or "Cliente General"
            ctk.CTkLabel(row, text=cliente_str, font=FONTS["body"], width=260, anchor="w").pack(side="left", padx=5)

            # Método
            ctk.CTkLabel(row, text=f['metodo_pago'] or "Efectivo", font=FONTS["body"], width=130, anchor="center").pack(side="left", padx=5)

            # Total
            ctk.CTkLabel(row, text=f"{simbolo} {f['total']:,.2f}", font=FONTS["body_bold"], width=140, anchor="e").pack(side="left", padx=5)

            # Botones de Acción
            btn_box = ctk.CTkFrame(row, fg_color="transparent", width=150)
            btn_box.pack(side="left", padx=5, fill="y")

            btn_pdf = ctk.CTkButton(
                btn_box,
                text="📄 PDF",
                font=FONTS["small"],
                width=65,
                height=28,
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                corner_radius=4,
                command=lambda f_id=f['id'], r=f.get('pdf_ruta'): self.abrir_o_regenerar_pdf(f_id, r)
            )
            btn_pdf.pack(side="left", padx=2, pady=8)

            btn_det = ctk.CTkButton(
                btn_box,
                text="🔍 Ver",
                font=FONTS["small"],
                width=60,
                height=28,
                fg_color=COLORS["surface_alt"],
                hover_color=COLORS["border"],
                corner_radius=4,
                command=lambda f_id=f['id']: self.mostrar_detalle(f_id)
            )
            btn_det.pack(side="left", padx=2, pady=8)

    def abrir_o_regenerar_pdf(self, factura_id, ruta_guardada):
        if ruta_guardada and Path(ruta_guardada).exists():
            self.pdf_generator.abrir_pdf(ruta_guardada)
        else:
            # Si el PDF fue movido o borrado, regenerarlo
            try:
                nueva_ruta = self.pdf_generator.generar_factura_pdf(factura_id)
                self.pdf_generator.abrir_pdf(nueva_ruta)
                messagebox.showinfo("PDF Regenerado", f"El archivo PDF se ha regenerado exitosamente:\n{nueva_ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

    def mostrar_detalle(self, factura_id):
        datos = self.db_manager.obtener_factura_completa(factura_id)
        if not datos:
            return
        
        f = datos['factura']
        items = datos['items']
        cfg = self.db_manager.obtener_config()
        simbolo = cfg.get('moneda_simbolo', '$')

        det_win = ctk.CTkToplevel(self)
        det_win.title(f"Detalle de Factura - {f['numero_factura']}")
        det_win.geometry("540x500")
        det_win.resizable(False, False)
        det_win.grab_set()

        main_box = ctk.CTkFrame(det_win, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        main_box.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main_box, text=f"Factura: {f['numero_factura']}", font=FONTS["title"], text_color=COLORS["primary"]).pack(anchor="w", padx=15, pady=(15, 2))
        ctk.CTkLabel(main_box, text=f"Fecha: {f['fecha_hora']} | Cliente: {f['cliente_nombre']}", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=15, pady=(0, 10))

        # Items
        scroll = ctk.CTkScrollableFrame(main_box, fg_color=COLORS["bg_dark"], height=220)
        scroll.pack(fill="x", padx=15, pady=5)

        for i in items:
            talla = f"Talla: {i['talla_medida']}" if i.get('talla_medida') else ""
            color = f"Color: {i['color']}" if i.get('color') else ""
            specs = f"({talla}, {color})".replace(", )", ")").replace("(, ", "(")
            if specs == "()":
                specs = ""
            
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{i['cantidad']}x {i['producto_nombre']} {specs}", font=FONTS["body"], anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"{simbolo} {i['subtotal']:,.2f}", font=FONTS["body_bold"], text_color=COLORS["primary"]).pack(side="right")

        # Totales
        tot_frame = ctk.CTkFrame(main_box, fg_color="transparent")
        tot_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(tot_frame, text=f"Subtotal: {simbolo} {f['subtotal']:,.2f}  |  ITBIS: {simbolo} {f['impuesto']:,.2f}", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(anchor="e")
        ctk.CTkLabel(tot_frame, text=f"TOTAL: {simbolo} {f['total']:,.2f}", font=FONTS["metric"], text_color=COLORS["primary"]).pack(anchor="e")

        btn_close = ctk.CTkButton(main_box, text="Cerrar", font=FONTS["body_bold"], fg_color=COLORS["surface_alt"], hover_color=COLORS["border"], command=det_win.destroy)
        btn_close.pack(anchor="e", padx=15, pady=(5, 15))
