import customtkinter as ctk
from config import COLORS, SIZES, FONTS

class AddProductModal(ctk.CTkToplevel):
    def __init__(self, parent, catalogo_sugerencias, on_add_callback):
        super().__init__(parent)
        self.parent = parent
        self.catalogo = {item['nombre']: item for item in catalogo_sugerencias}
        self.on_add_callback = on_add_callback

        self.title("Agregar Producto a la Factura")
        self.geometry("560x650")
        self.resizable(False, False)
        self.grab_set()  # Modal bloqueante

        # Centrar ventana respecto al padre
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 560) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{max(50, x)}+{max(50, y)}")

        self.configure(fg_color=COLORS["bg_dark"])
        self.crear_widgets()

    def crear_widgets(self):
        container = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título del modal
        lbl_titulo = ctk.CTkLabel(
            container,
            text="Detalle de Mercancía / Artículo",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        lbl_titulo.pack(anchor="w", padx=25, pady=(20, 5))

        lbl_sub = ctk.CTkLabel(
            container,
            text="Seleccione un artículo común o escriba uno personalizado:",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        lbl_sub.pack(anchor="w", padx=25, pady=(0, 15))

        # 1. Mercancía / Producto
        lbl_prod = ctk.CTkLabel(container, text="Mercancía / Producto *", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_prod.pack(anchor="w", padx=25, pady=(5, 2))

        nombres_sugeridos = list(self.catalogo.keys()) if self.catalogo else ["Camiseta Poliéster", "Taza Cerámica 11oz"]
        self.combo_producto = ctk.CTkComboBox(
            container,
            values=nombres_sugeridos,
            font=FONTS["body"],
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            command=self.al_seleccionar_producto
        )
        self.combo_producto.pack(fill="x", padx=25, pady=(0, 12))

        # 2. Talla / Medida y Color (Fila doble)
        row_specs = ctk.CTkFrame(container, fg_color="transparent")
        row_specs.pack(fill="x", padx=25, pady=(0, 12))

        # Talla
        col_talla = ctk.CTkFrame(row_specs, fg_color="transparent")
        col_talla.pack(side="left", fill="x", expand=True, padx=(0, 10))

        lbl_talla = ctk.CTkLabel(col_talla, text="Talla / Medida", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_talla.pack(anchor="w", pady=(0, 2))

        tallas_comunes = ["S", "M", "L", "XL", "XXL", "11 oz", "15 oz", "A4", "A3", "Ajustable", "Estándar", "Personalizado"]
        self.combo_talla = ctk.CTkComboBox(
            col_talla,
            values=tallas_comunes,
            font=FONTS["body"],
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"]
        )
        self.combo_talla.set("M")
        self.combo_talla.pack(fill="x")

        # Color
        col_color = ctk.CTkFrame(row_specs, fg_color="transparent")
        col_color.pack(side="right", fill="x", expand=True, padx=(10, 0))

        lbl_color = ctk.CTkLabel(col_color, text="Color / Acabado", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_color.pack(anchor="w", pady=(0, 2))

        colores_comunes = ["Blanco", "Negro", "Gris", "Azul Marino", "Rojo", "Blanco/Negro", "Plateado", "Multicolor"]
        self.combo_color = ctk.CTkComboBox(
            col_color,
            values=colores_comunes,
            font=FONTS["body"],
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"]
        )
        self.combo_color.set("Blanco")
        self.combo_color.pack(fill="x")

        # 3. Cantidad y Precio Unitario a Mano (Fila doble)
        row_qty_price = ctk.CTkFrame(container, fg_color="transparent")
        row_qty_price.pack(fill="x", padx=25, pady=(0, 15))

        # Cantidad con botones +/-
        col_qty = ctk.CTkFrame(row_qty_price, fg_color="transparent")
        col_qty.pack(side="left", fill="x", expand=True, padx=(0, 10))

        lbl_qty = ctk.CTkLabel(col_qty, text="Cantidad *", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_qty.pack(anchor="w", pady=(0, 2))

        stepper_frame = ctk.CTkFrame(col_qty, fg_color="transparent")
        stepper_frame.pack(fill="x")

        btn_minus = ctk.CTkButton(
            stepper_frame,
            text="-",
            font=("Segoe UI", 16, "bold"),
            width=40,
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            command=self.disminuir_cantidad
        )
        btn_minus.pack(side="left", padx=(0, 5))

        self.entry_cantidad = ctk.CTkEntry(
            stepper_frame,
            font=FONTS["body_bold"],
            height=SIZES["input_height"],
            justify="center",
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"]
        )
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(side="left", fill="x", expand=True)
        self.entry_cantidad.bind("<KeyRelease>", lambda e: self.recalcular_subtotal())

        btn_plus = ctk.CTkButton(
            stepper_frame,
            text="+",
            font=("Segoe UI", 16, "bold"),
            width=40,
            height=SIZES["input_height"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            command=self.aumentar_cantidad
        )
        btn_plus.pack(side="right", padx=(5, 0))

        # Precio Unitario a Mano
        col_price = ctk.CTkFrame(row_qty_price, fg_color="transparent")
        col_price.pack(side="right", fill="x", expand=True, padx=(10, 0))

        lbl_price = ctk.CTkLabel(col_price, text="Precio Unitario (a mano) *", font=FONTS["body_bold"], text_color=COLORS["text_primary"])
        lbl_price.pack(anchor="w", pady=(0, 2))

        self.entry_precio = ctk.CTkEntry(
            col_price,
            font=FONTS["body_bold"],
            height=SIZES["input_height"],
            placeholder_text="0.00",
            fg_color=COLORS["surface_alt"],
            border_color=COLORS["border"]
        )
        self.entry_precio.insert(0, "350.00")
        self.entry_precio.pack(fill="x")
        self.entry_precio.bind("<KeyRelease>", lambda e: self.recalcular_subtotal())

        # 4. Preview de Subtotal
        subtotal_card = ctk.CTkFrame(container, fg_color=COLORS["bg_dark"], corner_radius=SIZES["corner_radius"])
        subtotal_card.pack(fill="x", padx=25, pady=(0, 20))

        lbl_subtotal_title = ctk.CTkLabel(subtotal_card, text="Subtotal de este artículo:", font=FONTS["body"], text_color=COLORS["text_secondary"])
        lbl_subtotal_title.pack(side="left", padx=15, pady=12)

        self.lbl_subtotal_val = ctk.CTkLabel(subtotal_card, text="$ 350.00", font=FONTS["currency"], text_color=COLORS["primary"])
        self.lbl_subtotal_val.pack(side="right", padx=15, pady=12)

        # Mensaje de error / validación
        self.lbl_error = ctk.CTkLabel(container, text="", font=FONTS["small"], text_color=COLORS["danger"])
        self.lbl_error.pack(padx=25, pady=(0, 10))

        # 5. Botones de Gran Tamaño para Fácil Uso
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", padx=25, pady=(0, 15))

        btn_cancelar = ctk.CTkButton(
            btn_box,
            text="Cancelar",
            font=FONTS["body_bold"],
            height=SIZES["btn_height_medium"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=SIZES["corner_radius"],
            command=self.destroy
        )
        btn_cancelar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_agregar = ctk.CTkButton(
            btn_box,
            text="✔ Agregar a Factura",
            font=FONTS["subtitle"],
            height=SIZES["btn_height_large"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=SIZES["corner_radius"],
            command=self.confirmar_agregar
        )
        btn_agregar.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Cargar datos iniciales del combo si existe
        if nombres_sugeridos:
            self.combo_producto.set(nombres_sugeridos[0])
            self.al_seleccionar_producto(nombres_sugeridos[0])

    def al_seleccionar_producto(self, nombre):
        if nombre in self.catalogo:
            item = self.catalogo[nombre]
            if item.get('talla_sugerida'):
                self.combo_talla.set(item['talla_sugerida'])
            if item.get('color_sugerido'):
                self.combo_color.set(item['color_sugerido'])
            if item.get('precio_sugerido'):
                self.entry_precio.delete(0, "end")
                self.entry_precio.insert(0, f"{item['precio_sugerido']:.2f}")
            self.recalcular_subtotal()

    def aumentar_cantidad(self):
        try:
            val = int(self.entry_cantidad.get().strip() or 0) + 1
        except ValueError:
            val = 1
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, str(val))
        self.recalcular_subtotal()

    def disminuir_cantidad(self):
        try:
            val = int(self.entry_cantidad.get().strip() or 1) - 1
            if val < 1:
                val = 1
        except ValueError:
            val = 1
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, str(val))
        self.recalcular_subtotal()

    def recalcular_subtotal(self):
        try:
            cant = int(self.entry_cantidad.get().strip() or 0)
            precio = float(self.entry_precio.get().strip() or 0.0)
            subtotal = cant * precio
            self.lbl_subtotal_val.configure(text=f"$ {subtotal:,.2f}")
            self.lbl_error.configure(text="")
        except ValueError:
            self.lbl_subtotal_val.configure(text="$ 0.00")

    def confirmar_agregar(self):
        nombre = self.combo_producto.get().strip()
        if not nombre:
            self.lbl_error.configure(text="Debe ingresar o seleccionar un nombre de artículo.")
            return

        try:
            cant = int(self.entry_cantidad.get().strip())
            if cant <= 0:
                raise ValueError()
        except ValueError:
            self.lbl_error.configure(text="La cantidad debe ser un número entero mayor a 0.")
            return

        try:
            precio = float(self.entry_precio.get().strip())
            if precio < 0:
                raise ValueError()
        except ValueError:
            self.lbl_error.configure(text="El precio unitario debe ser un valor numérico válido.")
            return

        item_data = {
            "producto_nombre": nombre,
            "talla_medida": self.combo_talla.get().strip(),
            "color": self.combo_color.get().strip(),
            "cantidad": cant,
            "precio_unitario": precio,
            "subtotal": round(cant * precio, 2)
        }

        self.on_add_callback(item_data)
        self.destroy()
