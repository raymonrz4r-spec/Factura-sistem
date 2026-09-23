import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image
from config import COLORS, SIZES, FONTS
from utils.validators import (
    validar_cedula_o_rnc,
    formatear_documento,
    formatear_telefono,
    sanitizar_alfanumerico,
    solo_numeros_callback
)

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db_manager, backup_service, on_config_updated_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.backup_service = backup_service
        self.on_config_updated_callback = on_config_updated_callback
        self.logo_path_temp = ""
        self.logo_image_preview = None

        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.grid(row=0, column=0, sticky="nsew")
        scroll_container.columnconfigure(0, weight=1)

        # 1. Tarjeta: Perfil del Negocio y Logo
        card_empresa = ctk.CTkFrame(scroll_container, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_empresa.pack(fill="x", pady=(0, 16), padx=4)

        lbl_tit1 = ctk.CTkLabel(card_empresa, text="🏢 Configuración de la Empresa & Logo", font=FONTS["title"], text_color=COLORS["text_primary"])
        lbl_tit1.pack(anchor="w", padx=20, pady=(16, 12))

        # Fila Logo y Campos
        body_empresa = ctk.CTkFrame(card_empresa, fg_color="transparent")
        body_empresa.pack(fill="x", padx=20, pady=(0, 16))
        body_empresa.columnconfigure(0, weight=1)
        body_empresa.columnconfigure(1, weight=2)

        # Columna Izquierda: Logo
        col_logo = ctk.CTkFrame(body_empresa, fg_color=COLORS["surface_alt"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        col_logo.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=0)

        ctk.CTkLabel(col_logo, text="Logo de la Empresa", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(pady=(12, 6))

        self.lbl_preview_logo = ctk.CTkLabel(col_logo, text="Sin logo configurado", font=FONTS["small"], text_color=COLORS["text_secondary"], width=180, height=100)
        self.lbl_preview_logo.pack(pady=8, padx=12)

        btn_logo = ctk.CTkButton(
            col_logo,
            text="📁 Seleccionar Logo...",
            font=FONTS["body_bold"],
            height=SIZES["btn_height_small"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.seleccionar_logo
        )
        btn_logo.pack(fill="x", padx=16, pady=4)

        btn_quitar_logo = ctk.CTkButton(
            col_logo,
            text="✕ Quitar Logo",
            font=FONTS["small"],
            height=28,
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["danger"],
            command=self.quitar_logo
        )
        btn_quitar_logo.pack(fill="x", padx=16, pady=(0, 12))

        # Columna Derecha: Campos de datos
        col_campos = ctk.CTkFrame(body_empresa, fg_color="transparent")
        col_campos.grid(row=0, column=1, sticky="nsew")

        vcmd_telefono = (self.register(lambda s, P: solo_numeros_callback(s, P, 10)), '%S', '%P')
        vcmd_rnc = (self.register(lambda s, P: solo_numeros_callback(s, P, 11)), '%S', '%P')

        # Nombre Negocio
        lbl_n = ctk.CTkLabel(col_campos, text="Nombre del Negocio / Taller", font=FONTS["small"], text_color=COLORS["text_secondary"])
        lbl_n.pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(col_campos, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_nombre.pack(fill="x", pady=(0, 8))

        # RNC y Teléfono
        row_rnc_tel = ctk.CTkFrame(col_campos, fg_color="transparent")
        row_rnc_tel.pack(fill="x", pady=(0, 8))
        row_rnc_tel.columnconfigure(0, weight=1)
        row_rnc_tel.columnconfigure(1, weight=1)

        c_rnc = ctk.CTkFrame(row_rnc_tel, fg_color="transparent")
        c_rnc.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(c_rnc, text="RNC o Cédula Fiscal (Solo Números)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_rnc = ctk.CTkEntry(c_rnc, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_rnc.pack(fill="x")
        self.entry_rnc._entry.configure(validate="key", validatecommand=vcmd_rnc)

        c_tel = ctk.CTkFrame(row_rnc_tel, fg_color="transparent")
        c_tel.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(c_tel, text="Teléfono / Celular (Solo Números)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_telefono = ctk.CTkEntry(c_tel, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_telefono.pack(fill="x")
        self.entry_telefono._entry.configure(validate="key", validatecommand=vcmd_telefono)

        # Correo y Dirección
        row_cor_dir = ctk.CTkFrame(col_campos, fg_color="transparent")
        row_cor_dir.pack(fill="x", pady=(0, 8))
        row_cor_dir.columnconfigure(0, weight=1)
        row_cor_dir.columnconfigure(1, weight=1)

        c_cor = ctk.CTkFrame(row_cor_dir, fg_color="transparent")
        c_cor.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(c_cor, text="Correo Electrónico", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_email = ctk.CTkEntry(c_cor, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_email.pack(fill="x")

        c_dir = ctk.CTkFrame(row_cor_dir, fg_color="transparent")
        c_dir.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(c_dir, text="Dirección Física", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_direccion = ctk.CTkEntry(c_dir, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_direccion.pack(fill="x")

        # ITBIS y Moneda
        row_imp_mon = ctk.CTkFrame(col_campos, fg_color="transparent")
        row_imp_mon.pack(fill="x", pady=(0, 8))
        row_imp_mon.columnconfigure(0, weight=1)
        row_imp_mon.columnconfigure(1, weight=1)

        c_imp = ctk.CTkFrame(row_imp_mon, fg_color="transparent")
        c_imp.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(c_imp, text="Porcentaje ITBIS / Impuesto (%)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_itbis = ctk.CTkEntry(c_imp, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_itbis.pack(fill="x")

        c_mon = ctk.CTkFrame(row_imp_mon, fg_color="transparent")
        c_mon.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(c_mon, text="Símbolo de Moneda", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_moneda = ctk.CTkEntry(c_mon, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_moneda.pack(fill="x")

        # Mensaje de Pie
        ctk.CTkLabel(col_campos, text="Mensaje de Agradecimiento / Garantía (Pie de Factura)", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_mensaje = ctk.CTkEntry(col_campos, height=SIZES["input_height"], font=FONTS["body"], fg_color=COLORS["surface_alt"], border_color=COLORS["border"])
        self.entry_mensaje.pack(fill="x", pady=(0, 12))

        # Botón Guardar Cambios
        btn_guardar = ctk.CTkButton(
            col_campos,
            text="💾 Guardar Configuración del Negocio",
            font=FONTS["subtitle"],
            height=SIZES["btn_height_large"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.guardar_configuracion
        )
        btn_guardar.pack(fill="x")


        # 2. Tarjeta: Sistema de Copias de Seguridad (Backup)
        card_backup = ctk.CTkFrame(scroll_container, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_backup.pack(fill="x", pady=(0, 16), padx=4)

        lbl_tit2 = ctk.CTkLabel(card_backup, text="🛡️ Copias de Seguridad (Backup Semanal & Manual)", font=FONTS["title"], text_color=COLORS["text_primary"])
        lbl_tit2.pack(anchor="w", padx=20, pady=(16, 6))

        lbl_desc_bkp = ctk.CTkLabel(
            card_backup,
            text="El sistema realiza un respaldo automático cada semana al iniciar. También puede generar respaldos manuales o restaurar la base de datos en cualquier momento.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=700,
            justify="left"
        )
        lbl_desc_bkp.pack(anchor="w", padx=20, pady=(0, 14))

        # Acciones de Backup
        row_bkp_btns = ctk.CTkFrame(card_backup, fg_color="transparent")
        row_bkp_btns.pack(fill="x", padx=20, pady=(0, 14))

        btn_crear_bkp = ctk.CTkButton(
            row_bkp_btns,
            text="💾 Crear Copia de Seguridad Ahora",
            font=FONTS["body_bold"],
            height=SIZES["btn_height_medium"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.crear_backup_manual
        )
        btn_crear_bkp.pack(side="left", padx=(0, 12))

        btn_restaurar = ctk.CTkButton(
            row_bkp_btns,
            text="🔄 Restaurar Copia de Seguridad...",
            font=FONTS["body_bold"],
            height=SIZES["btn_height_medium"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            command=self.restaurar_backup
        )
        btn_restaurar.pack(side="left")

        # Lista de Backups Recientes
        ctk.CTkLabel(card_backup, text="Backups Disponibles en el Disco:", font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(8, 4))

        self.scroll_backups = ctk.CTkScrollableFrame(card_backup, fg_color=COLORS["bg_dark"], height=160)
        self.scroll_backups.pack(fill="x", padx=20, pady=(0, 16))

        self.cargar_lista_backups()

    def seleccionar_logo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar Logo de la Empresa",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        if archivo:
            self.logo_path_temp = archivo
            self.mostrar_preview_logo(archivo)

    def quitar_logo(self):
        self.logo_path_temp = ""
        self.lbl_preview_logo.configure(image="", text="Sin logo configurado")

    def mostrar_preview_logo(self, ruta):
        if not ruta or not Path(ruta).exists():
            self.lbl_preview_logo.configure(image="", text="Sin logo configurado")
            return

        try:
            pil_img = Image.open(ruta)
            # Redimensionar manteniendo proporción (max 180x90)
            pil_img.thumbnail((180, 90))
            self.logo_image_preview = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.lbl_preview_logo.configure(image=self.logo_image_preview, text="")
        except Exception as e:
            self.lbl_preview_logo.configure(image="", text=f"Error cargando imagen:\n{e}")

    def cargar_datos(self):
        cfg = self.db_manager.obtener_config()
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, cfg.get('nombre_negocio', ''))

        self.entry_rnc.delete(0, "end")
        self.entry_rnc.insert(0, cfg.get('rnc_cedula', ''))

        self.entry_telefono.delete(0, "end")
        self.entry_telefono.insert(0, cfg.get('telefono', ''))

        self.entry_email.delete(0, "end")
        self.entry_email.insert(0, cfg.get('email', ''))

        self.entry_direccion.delete(0, "end")
        self.entry_direccion.insert(0, cfg.get('direccion', ''))

        self.entry_mensaje.delete(0, "end")
        self.entry_mensaje.insert(0, cfg.get('mensaje_pie', ''))

        self.entry_itbis.delete(0, "end")
        self.entry_itbis.insert(0, str(cfg.get('itbis_porcentaje', 18.0)))

        self.entry_moneda.delete(0, "end")
        self.entry_moneda.insert(0, cfg.get('moneda_simbolo', '$'))

        self.logo_path_temp = cfg.get('logo_path', '')
        if self.logo_path_temp:
            self.mostrar_preview_logo(self.logo_path_temp)

    def guardar_configuracion(self):
        try:
            itbis_val = float(self.entry_itbis.get().strip() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "El porcentaje de ITBIS debe ser un número válido.")
            return

        nombre_negocio = sanitizar_alfanumerico(self.entry_nombre.get().strip()) or "Taller de Sublimación"
        
        # Validar RNC o Cédula de la empresa
        rnc_raw = "".join(c for c in self.entry_rnc.get() if c.isdigit())
        if rnc_raw:
            es_val, tipo, msg_error = validar_cedula_o_rnc(rnc_raw, obligatorio=False)
            if not es_val:
                messagebox.showerror(
                    "Identificación Fiscal Inválida",
                    f"El RNC o Cédula de la empresa no es válido ({tipo}):\n\n{msg_error}"
                )
                self.entry_rnc.focus()
                return
            rnc_formateado = formatear_documento(rnc_raw)
        else:
            rnc_formateado = ""

        # Validar teléfono de la empresa
        tel_raw = "".join(c for c in self.entry_telefono.get() if c.isdigit())
        if tel_raw and len(tel_raw) < 10:
            messagebox.showwarning(
                "Teléfono Incompleto",
                "El número de teléfono del negocio debe tener al menos 10 dígitos (ej. 8095550192)."
            )
            self.entry_telefono.focus()
            return
        tel_formateado = formatear_telefono(tel_raw) if tel_raw else ""

        datos = {
            "nombre_negocio": nombre_negocio,
            "rnc_cedula": rnc_formateado,
            "telefono": tel_formateado,
            "email": self.entry_email.get().strip(),
            "direccion": self.entry_direccion.get().strip(),
            "mensaje_pie": self.entry_mensaje.get().strip(),
            "logo_path": self.logo_path_temp,
            "itbis_porcentaje": itbis_val,
            "moneda_simbolo": self.entry_moneda.get().strip() or "$"
        }

        self.db_manager.actualizar_config(datos)
        messagebox.showinfo("Configuración Guardada", "Los datos de la empresa y preferencias se actualizaron correctamente.")
        if self.on_config_updated_callback:
            self.on_config_updated_callback()

    def crear_backup_manual(self):
        try:
            ruta, fecha = self.backup_service.crear_backup(tipo="manual")
            messagebox.showinfo(
                "Copia de Seguridad Creada",
                f"Respaldo generado con éxito:\n\n{ruta}\n\nFecha: {fecha}"
            )
            self.cargar_lista_backups()
        except Exception as e:
            messagebox.showerror("Error de Backup", f"No se pudo crear la copia de seguridad:\n{e}")

    def restaurar_backup(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de Backup (.db)",
            filetypes=[("Base de Datos SQLite", "*.db")]
        )
        if not archivo:
            return

        confirma = messagebox.askyesno(
            "Confirmar Restauración",
            "¿Está seguro de que desea restaurar la base de datos desde este archivo?\n\n"
            "Se reemplazará la información actual por la del respaldo (se guardará una copia previa de seguridad)."
        )
        if not confirma:
            return

        try:
            self.backup_service.restaurar_backup(archivo)
            messagebox.showinfo("Restauración Completa", "La base de datos ha sido restaurada con éxito.")
            self.cargar_datos()
            self.cargar_lista_backups()
        except Exception as e:
            messagebox.showerror("Error al Restaurar", f"No se pudo completar la restauración:\n{e}")

    def cargar_lista_backups(self):
        for w in self.scroll_backups.winfo_children():
            w.destroy()

        backups = self.backup_service.listar_backups()
        if not backups:
            ctk.CTkLabel(self.scroll_backups, text="No se han registrado copias de seguridad aún.", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(pady=20)
            return

        for b in backups:
            row = ctk.CTkFrame(self.scroll_backups, fg_color=COLORS["surface_alt"], height=34, corner_radius=4)
            row.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(row, text=f"💾 {b['nombre']}", font=FONTS["small"], anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{b['tamano_kb']} KB", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=b['fecha'], font=FONTS["small"], text_color=COLORS["primary"]).pack(side="right", padx=10)
