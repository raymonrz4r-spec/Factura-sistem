import customtkinter as ctk
import datetime
from tkinter import messagebox
from config import COLORS, SIZES, FONTS
from ui.dialogs.add_product_modal import AddProductModal
from services.pdf_generator import PDFGenerator
from utils.validators import (
    validar_cedula,
    validar_rnc,
    validar_cedula_o_rnc,
    formatear_documento,
    formatear_telefono,
    sanitizar_alfanumerico,
    solo_numeros_callback,
    alfanumerico_callback
)

class InvoiceView(ctk.CTkFrame):
    def __init__(self, parent, db_manager, on_invoice_created_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.on_invoice_created_callback = on_invoice_created_callback
        self.pdf_generator = PDFGenerator(db_manager)
        
        self.items = []  # Lista de productos en la factura actual
        self.crear_interfaz()
        self.cargar_siguiente_numero()

    def crear_interfaz(self):
        # Panel principal dividido en 2 columnas:
        # Izquierda: Datos del cliente, botón grande de agregar, y tabla de ítems (expandible)
        # Derecha: Resumen de totales, método de pago, y botón grande de confirmar factura

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- COLUMNA IZQUIERDA (Operacional) ---
        col_izq = ctk.CTkFrame(self, fg_color="transparent")
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=0)
        col_izq.rowconfigure(2, weight=1)
        col_izq.columnconfigure(0, weight=1)

        # 1. Tarjeta: Datos del Cliente y Número de Factura
        card_cliente = ctk.CTkFrame(col_izq, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_cliente.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Encabezado interno de tarjeta
        header_row = ctk.CTkFrame(card_cliente, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(12, 6))

        lbl_sec_cliente = ctk.CTkLabel(header_row, text="📋 Datos del Cliente y Facturación", font=FONTS["subtitle"], text_color=COLORS["text_primary"])
        lbl_sec_cliente.pack(side="left")

        self.lbl_numero_factura = ctk.CTkLabel(header_row, text="Factura: FAC-0001", font=FONTS["subtitle"], text_color=COLORS["primary"])
        self.lbl_numero_factura.pack(side="right")

        # Inputs de cliente (3 columnas)
        row_inputs = ctk.CTkFrame(card_cliente, fg_color="transparent")
        row_inputs.pack(fill="x", padx=16, pady=(0, 14))
        row_inputs.columnconfigure(0, weight=2)
        row_inputs.columnconfigure(1, weight=1)
        row_inputs.columnconfigure(2, weight=1)

        # Registro de comandos de validación para entradas en tiempo real
        vcmd_alfanumerico = (self.register(lambda s, P: alfanumerico_callback(s, P, 80)), '%S', '%P')
        vcmd_telefono = (self.register(lambda s, P: solo_numeros_callback(s, P, 10)), '%S', '%P')
        vcmd_rnc = (self.register(lambda s, P: solo_numeros_callback(s, P, 11)), '%S', '%P')

        # Nombre / Razón Social (Solo caracteres alfanuméricos y signos comerciales seguros)
        col_c1 = ctk.CTkFrame(row_inputs, fg_color="transparent")
        col_c1.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        lbl_nom = ctk.CTkLabel(col_c1, text="Nombre / Razón Social (Alfanumérico)", font=FONTS["small"], text_color=COLORS["text_secondary"])
        lbl_nom.pack(anchor="w")
        self.entry_cliente_nombre = ctk.CTkEntry(col_c1, placeholder_text="Ej. Creaciones Graficas SRL / Juan Perez", font=FONTS["body"], height=SIZES["input_height"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_cliente_nombre.pack(fill="x")
        self.entry_cliente_nombre._entry.configure(validate="key", validatecommand=vcmd_alfanumerico)

        # Teléfono (Solo números, máx 10 dígitos)
        col_c2 = ctk.CTkFrame(row_inputs, fg_color="transparent")
        col_c2.grid(row=0, column=1, sticky="ew", padx=8)
        lbl_tel = ctk.CTkLabel(col_c2, text="Teléfono / WhatsApp (Solo Números)", font=FONTS["small"], text_color=COLORS["text_secondary"])
        lbl_tel.pack(anchor="w")
        self.entry_cliente_tel = ctk.CTkEntry(col_c2, placeholder_text="Ej. 8095550192", font=FONTS["body"], height=SIZES["input_height"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_cliente_tel.pack(fill="x")
        self.entry_cliente_tel._entry.configure(validate="key", validatecommand=vcmd_telefono)

        # RNC / Cédula (Solo números, 9 o 11 dígitos, con validación de dígito verificador)
        col_c3 = ctk.CTkFrame(row_inputs, fg_color="transparent")
        col_c3.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        
        lbl_rnc_header = ctk.CTkFrame(col_c3, fg_color="transparent")
        lbl_rnc_header.pack(fill="x")
        lbl_rnc = ctk.CTkLabel(lbl_rnc_header, text="RNC / Cédula (Solo Números)", font=FONTS["small"], text_color=COLORS["text_secondary"])
        lbl_rnc.pack(side="left")
        
        self.lbl_rnc_status = ctk.CTkLabel(lbl_rnc_header, text="", font=FONTS["small"])
        self.lbl_rnc_status.pack(side="right")

        self.entry_cliente_rnc = ctk.CTkEntry(col_c3, placeholder_text="9 dígitos (RNC) u 11 (Cédula)", font=FONTS["body"], height=SIZES["input_height"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_cliente_rnc.pack(fill="x")
        self.entry_cliente_rnc._entry.configure(validate="key", validatecommand=vcmd_rnc)
        self.entry_cliente_rnc.bind("<KeyRelease>", lambda e: self.al_escribir_rnc())

        # 2. BOTÓN EN GRANDE: "AGREGAR PRODUCTO A LA FACTURA" (Requisito fundamental)
        self.btn_abrir_modal = ctk.CTkButton(
            col_izq,
            text="➕  AGREGAR PRODUCTO A LA FACTURA",
            font=("Segoe UI", 15, "bold"),
            height=SIZES["btn_height_large"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=SIZES["corner_radius"],
            command=self.abrir_modal_producto
        )
        self.btn_abrir_modal.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # 3. Contenedor y Tabla de Productos Agregados
        card_tabla = ctk.CTkFrame(col_izq, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_tabla.grid(row=2, column=0, sticky="nsew")
        card_tabla.rowconfigure(1, weight=1)
        card_tabla.columnconfigure(0, weight=1)

        # Cabecera de la tabla
        table_header = ctk.CTkFrame(card_tabla, fg_color=COLORS["surface_alt"], height=38, corner_radius=0)
        table_header.grid(row=0, column=0, sticky="ew")
        
        cols_spec = [
            ("Cant.", 55),
            ("Mercancía / Descripción", 240),
            ("Talla", 80),
            ("Color", 90),
            ("Precio Unit.", 95),
            ("Subtotal", 95),
            ("Acción", 75)
        ]
        
        for idx, (title, width) in enumerate(cols_spec):
            lbl_col = ctk.CTkLabel(
                table_header,
                text=title,
                font=FONTS["body_bold"],
                text_color=COLORS["text_primary"],
                width=width,
                anchor="center" if idx in [0, 2, 3, 6] else ("w" if idx == 1 else "e")
            )
            lbl_col.pack(side="left", padx=5, pady=4)

        # Scrollable Frame para las filas
        self.scroll_items = ctk.CTkScrollableFrame(card_tabla, fg_color="transparent")
        self.scroll_items.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Placeholder si no hay ítems
        self.lbl_vacio = ctk.CTkLabel(
            self.scroll_items,
            text="No hay productos en la factura aún.\nHaga clic en 'AGREGAR PRODUCTO A LA FACTURA' para comenzar.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        self.lbl_vacio.pack(pady=60)


        # --- COLUMNA DERECHA (Liquidación y Confirmación) ---
        col_der = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        col_der.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Título Resumen
        lbl_resumen = ctk.CTkLabel(col_der, text="💰 Resumen de Factura", font=FONTS["subtitle"], text_color=COLORS["text_primary"])
        lbl_resumen.pack(anchor="w", padx=20, pady=(16, 12))

        # Desglose de Totales
        totales_box = ctk.CTkFrame(col_der, fg_color=COLORS["bg_dark"], corner_radius=SIZES["corner_radius"])
        totales_box.pack(fill="x", padx=16, pady=(0, 14))

        # Subtotal
        f_sub = ctk.CTkFrame(totales_box, fg_color="transparent")
        f_sub.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(f_sub, text="Subtotal Bruto:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left")
        self.lbl_val_subtotal = ctk.CTkLabel(f_sub, text="$ 0.00", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        self.lbl_val_subtotal.pack(side="right")

        # Descuento
        f_desc = ctk.CTkFrame(totales_box, fg_color="transparent")
        f_desc.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(f_desc, text="Descuento:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left")
        self.entry_descuento = ctk.CTkEntry(f_desc, width=90, height=30, font=FONTS["body"], justify="right", placeholder_text="0.00", fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_descuento.insert(0, "0.00")
        self.entry_descuento.pack(side="right")
        self.entry_descuento.bind("<KeyRelease>", lambda e: self.recalcular_totales())

        # ITBIS / Impuesto con switch opcional
        f_itbis = ctk.CTkFrame(totales_box, fg_color="transparent")
        f_itbis.pack(fill="x", padx=14, pady=4)
        
        self.switch_itbis_var = ctk.BooleanVar(value=True)
        self.switch_itbis = ctk.CTkSwitch(
            f_itbis,
            text="ITBIS (18%):",
            variable=self.switch_itbis_var,
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            progress_color=COLORS["primary"],
            command=self.recalcular_totales
        )
        self.switch_itbis.pack(side="left")

        self.lbl_val_itbis = ctk.CTkLabel(f_itbis, text="$ 0.00", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        self.lbl_val_itbis.pack(side="right")

        # Separador
        sep = ctk.CTkFrame(totales_box, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=14, pady=8)

        # TOTAL A PAGAR (Enorme y de alto impacto)
        f_total = ctk.CTkFrame(totales_box, fg_color="transparent")
        f_total.pack(fill="x", padx=14, pady=(2, 12))
        ctk.CTkLabel(f_total, text="TOTAL:", font=("Segoe UI", 13, "bold"), text_color=COLORS["text_primary"]).pack(side="left")
        self.lbl_val_total = ctk.CTkLabel(f_total, text="$ 0.00", font=FONTS["metric"], text_color=COLORS["primary"])
        self.lbl_val_total.pack(side="right")

        # Método de Pago
        lbl_pago = ctk.CTkLabel(col_der, text="Forma de Pago:", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_pago.pack(anchor="w", padx=20, pady=(4, 2))

        self.combo_metodo_pago = ctk.CTkComboBox(
            col_der,
            values=["Efectivo", "Transferencia Bancaria", "Tarjeta de Crédito / Débito", "Contra Entrega"],
            font=FONTS["body"],
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"]
        )
        self.combo_metodo_pago.set("Efectivo")
        self.combo_metodo_pago.pack(fill="x", padx=16, pady=(0, 10))

        # Notas / Especificaciones de Sublimación
        lbl_notas = ctk.CTkLabel(col_der, text="Notas de Sublimación / Diseño:", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_notas.pack(anchor="w", padx=20, pady=(4, 2))

        self.entry_notas = ctk.CTkTextbox(col_der, height=80, font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"], border_width=1)
        self.entry_notas.pack(fill="x", padx=16, pady=(0, 15))

        # BOTÓN GIGANTE: "CONFIRMAR FACTURA" (Requisito fundamental)
        self.btn_confirmar = ctk.CTkButton(
            col_der,
            text="✔  CONFIRMAR FACTURA\n(Emitir y Abrir PDF)",
            font=("Segoe UI", 14, "bold"),
            height=60,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=SIZES["corner_radius"],
            command=self.confirmar_y_emitir_factura
        )
        self.btn_confirmar.pack(fill="x", padx=16, pady=(0, 10))

        # Botón secundario: Limpiar factura
        btn_limpiar = ctk.CTkButton(
            col_der,
            text="🔄 Limpiar / Nueva Factura",
            font=FONTS["body"],
            height=SIZES["btn_height_small"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            corner_radius=SIZES["corner_radius"],
            command=self.limpiar_factura
        )
        btn_limpiar.pack(fill="x", padx=16, pady=(0, 14))

    def cargar_siguiente_numero(self):
        sig_num = self.db_manager.obtener_siguiente_numero_factura()
        self.lbl_numero_factura.configure(text=f"Factura: {sig_num}")

    def abrir_modal_producto(self):
        sugerencias = self.db_manager.obtener_catalogo_sugerencias()
        modal = AddProductModal(self.winfo_toplevel(), sugerencias, self.agregar_item_a_tabla)

    def agregar_item_a_tabla(self, item_data):
        self.items.append(item_data)
        self.refrescar_tabla_items()
        self.recalcular_totales()

    def eliminar_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refrescar_tabla_items()
            self.recalcular_totales()

    def refrescar_tabla_items(self):
        # Limpiar widgets actuales en scroll_items
        for widget in self.scroll_items.winfo_children():
            widget.destroy()

        if not self.items:
            self.lbl_vacio = ctk.CTkLabel(
                self.scroll_items,
                text="No hay productos en la factura aún.\nHaga clic en 'AGREGAR PRODUCTO A LA FACTURA' para comenzar.",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"],
                justify="center"
            )
            self.lbl_vacio.pack(pady=60)
            return

        cfg = self.db_manager.obtener_config()
        simbolo = cfg.get('moneda_simbolo', '$')

        for idx, item in enumerate(self.items):
            row_bg = COLORS["card_bg"] if idx % 2 == 0 else COLORS["surface_alt"]
            row_frame = ctk.CTkFrame(self.scroll_items, fg_color=row_bg, height=44, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=2)

            # Cantidad
            ctk.CTkLabel(row_frame, text=str(item['cantidad']), font=FONTS["body_bold"], width=55, anchor="center").pack(side="left", padx=5)

            # Mercancía
            ctk.CTkLabel(row_frame, text=item['producto_nombre'], font=FONTS["body"], width=240, anchor="w").pack(side="left", padx=5)

            # Talla
            ctk.CTkLabel(row_frame, text=item.get('talla_medida') or "-", font=FONTS["body"], width=80, anchor="center").pack(side="left", padx=5)

            # Color
            ctk.CTkLabel(row_frame, text=item.get('color') or "-", font=FONTS["body"], width=90, anchor="center").pack(side="left", padx=5)

            # Precio Unitario
            ctk.CTkLabel(row_frame, text=f"{simbolo} {item['precio_unitario']:,.2f}", font=FONTS["body"], width=95, anchor="e").pack(side="left", padx=5)

            # Subtotal
            ctk.CTkLabel(row_frame, text=f"{simbolo} {item['subtotal']:,.2f}", font=FONTS["body_bold"], width=95, anchor="e", text_color=COLORS["primary"]).pack(side="left", padx=5)

            # Botón Eliminar
            btn_del = ctk.CTkButton(
                row_frame,
                text="✕",
                font=("Segoe UI", 12, "bold"),
                width=35,
                height=28,
                fg_color=COLORS["danger"],
                hover_color=COLORS["danger_hover"],
                corner_radius=4,
                command=lambda i=idx: self.eliminar_item(i)
            )
            btn_del.pack(side="right", padx=10)

    def recalcular_totales(self):
        subtotal_bruto = sum(item['subtotal'] for item in self.items)

        # Descuento
        try:
            descuento = float(self.entry_descuento.get().strip() or 0.0)
            if descuento < 0:
                descuento = 0.0
        except ValueError:
            descuento = 0.0

        base_imponible = max(0.0, subtotal_bruto - descuento)

        # ITBIS
        cfg = self.db_manager.obtener_config()
        itbis_pct = float(cfg.get('itbis_porcentaje', 18.0)) if self.switch_itbis_var.get() else 0.0
        impuesto = base_imponible * (itbis_pct / 100.0)

        total_final = base_imponible + impuesto
        simbolo = cfg.get('moneda_simbolo', '$')

        self.lbl_val_subtotal.configure(text=f"{simbolo} {subtotal_bruto:,.2f}")
        self.lbl_val_itbis.configure(text=f"{simbolo} {impuesto:,.2f}")
        self.lbl_val_total.configure(text=f"{simbolo} {total_final:,.2f}")

        return {
            "subtotal": round(subtotal_bruto, 2),
            "descuento": round(descuento, 2),
            "impuesto": round(impuesto, 2),
            "total": round(total_final, 2)
        }

    def al_escribir_rnc(self):
        val = "".join(c for c in self.entry_cliente_rnc.get() if c.isdigit())
        if not val:
            self.lbl_rnc_status.configure(text="")
        elif len(val) == 9:
            es_val, _ = validar_rnc(val)
            if es_val:
                self.lbl_rnc_status.configure(text="✔ RNC Válido", text_color=COLORS["success"])
            else:
                self.lbl_rnc_status.configure(text="✕ RNC Inválido", text_color=COLORS["danger"])
        elif len(val) == 11:
            es_val, _ = validar_cedula(val)
            if es_val:
                self.lbl_rnc_status.configure(text="✔ Cédula Válida", text_color=COLORS["success"])
            else:
                self.lbl_rnc_status.configure(text="✕ Cédula Inválida", text_color=COLORS["danger"])
        else:
            self.lbl_rnc_status.configure(text=f"{len(val)}/11 dígitos", text_color=COLORS["text_secondary"])

    def confirmar_y_emitir_factura(self):
        if not self.items:
            messagebox.showwarning("Factura Vacía", "Debe agregar al menos un producto o servicio antes de confirmar la factura.")
            return

        # 1. Sanitización de Nombre / Razón Social (Alfanumérico)
        nombre_raw = self.entry_cliente_nombre.get().strip()
        cliente_nombre = sanitizar_alfanumerico(nombre_raw) or "Cliente General"

        # 2. Validación y Sanitización de Teléfono
        tel_raw = "".join(c for c in self.entry_cliente_tel.get() if c.isdigit())
        if tel_raw:
            if len(tel_raw) < 10:
                messagebox.showwarning(
                    "Teléfono Incompleto",
                    f"El número de teléfono ingresado contiene solo {len(tel_raw)} dígitos.\n"
                    "Debe contener 10 dígitos (ej. 8095550192)."
                )
                self.entry_cliente_tel.focus()
                return
            cliente_tel = formatear_telefono(tel_raw)
        else:
            cliente_tel = ""

        # 3. Validación Estricta de Cédula o RNC (Evitar datos fiscales inválidos)
        rnc_raw = "".join(c for c in self.entry_cliente_rnc.get() if c.isdigit())
        if rnc_raw:
            es_val, tipo, msg_error = validar_cedula_o_rnc(rnc_raw, obligatorio=False)
            if not es_val:
                messagebox.showerror(
                    "Identificación Fiscal Inválida",
                    f"El número de documento ingresado no es válido ({tipo}):\n\n"
                    f"{msg_error}\n\n"
                    "Por favor verifíquelo o borre el campo si se trata de un cliente sin comprobante fiscal."
                )
                self.entry_cliente_rnc.focus()
                return
            cliente_rnc = formatear_documento(rnc_raw)
        else:
            cliente_rnc = ""

        totales = self.recalcular_totales()
        num_factura = self.db_manager.obtener_siguiente_numero_factura()
        metodo_pago = self.combo_metodo_pago.get()
        notas = self.entry_notas.get("1.0", "end").strip()

        datos_factura = {
            "numero_factura": num_factura,
            "cliente_nombre": cliente_nombre,
            "cliente_telefono": cliente_tel,
            "cliente_rnc": cliente_rnc,
            "metodo_pago": metodo_pago,
            "subtotal": totales["subtotal"],
            "descuento": totales["descuento"],
            "impuesto": totales["impuesto"],
            "total": totales["total"],
            "notas": notas
        }

        try:
            # 1. Guardar en Base de Datos SQLite
            factura_id = self.db_manager.guardar_factura(datos_factura, self.items)

            # 2. Generar el PDF estético con espacio de firmas
            pdf_path = self.pdf_generator.generar_factura_pdf(factura_id)

            # 3. Abrir el PDF automáticamente en Windows para ver/imprimir/compartir
            self.pdf_generator.abrir_pdf(pdf_path)

            messagebox.showinfo(
                "Factura Emitida con Éxito",
                f"¡Factura {num_factura} generada exitosamente!\n\n"
                f"Cliente: {cliente_nombre}\n"
                f"RNC / Cédula: {cliente_rnc or 'Consumidor Final'}\n\n"
                f"Guardada en:\n{pdf_path}\n\nEl PDF se ha abierto listo para compartir o imprimir."
            )

            # 4. Limpiar para la siguiente factura y refrescar vistas externas
            self.limpiar_factura()

            if self.on_invoice_created_callback:
                self.on_invoice_created_callback()

        except Exception as e:
            messagebox.showerror("Error al Emitir Factura", f"Ocurrió un error al procesar la factura:\n{e}")

    def limpiar_factura(self):
        self.items.clear()
        self.entry_cliente_nombre.delete(0, "end")
        self.entry_cliente_tel.delete(0, "end")
        self.entry_cliente_rnc.delete(0, "end")
        self.lbl_rnc_status.configure(text="")
        self.entry_descuento.delete(0, "end")
        self.entry_descuento.insert(0, "0.00")
        self.entry_notas.delete("1.0", "end")
        self.combo_metodo_pago.set("Efectivo")
        self.cargar_siguiente_numero()
        self.refrescar_tabla_items()
        self.recalcular_totales()
