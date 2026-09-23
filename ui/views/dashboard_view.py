import customtkinter as ctk
from config import COLORS, SIZES, FONTS

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.periodo_actual = "todos"
        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # 1. Barra de Control y Filtros de Tiempo
        control_card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        control_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        lbl_tit = ctk.CTkLabel(control_card, text="📊 Reporte de Ventas & Dashboard", font=FONTS["title"], text_color=COLORS["text_primary"])
        lbl_tit.pack(side="left", padx=20, pady=16)

        # Segmented button para período
        self.seg_periodo = ctk.CTkSegmentedButton(
            control_card,
            values=["Hoy", "Últimos 7 Días", "Este Mes", "Todo el Historial"],
            font=FONTS["body_bold"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["surface_alt"],
            unselected_hover_color=COLORS["border"],
            command=self.al_cambiar_periodo
        )
        self.seg_periodo.set("Todo el Historial")
        self.seg_periodo.pack(side="right", padx=20, pady=16)

        # 2. Tarjetas de Métricas Clave (KPIs)
        kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        kpi_container.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        kpi_container.columnconfigure(0, weight=1)
        kpi_container.columnconfigure(1, weight=1)
        kpi_container.columnconfigure(2, weight=1)

        # KPI 1: Ventas Totales
        card_ventas = ctk.CTkFrame(kpi_container, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_ventas.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(card_ventas, text="Ventas Totales", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_kpi_ventas = ctk.CTkLabel(card_ventas, text="$ 0.00", font=FONTS["metric"], text_color=COLORS["primary"])
        self.lbl_kpi_ventas.pack(anchor="w", padx=16, pady=(0, 14))

        # KPI 2: Cantidad de Facturas
        card_facturas = ctk.CTkFrame(kpi_container, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_facturas.grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(card_facturas, text="Facturas Emitidas", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_kpi_facturas = ctk.CTkLabel(card_facturas, text="0", font=FONTS["metric"], text_color=COLORS["text_primary"])
        self.lbl_kpi_facturas.pack(anchor="w", padx=16, pady=(0, 14))

        # KPI 3: Ticket Promedio
        card_ticket = ctk.CTkFrame(kpi_container, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        card_ticket.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(card_ticket, text="Ticket Promedio", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_kpi_ticket = ctk.CTkLabel(card_ticket, text="$ 0.00", font=FONTS["metric"], text_color=COLORS["text_primary"])
        self.lbl_kpi_ticket.pack(anchor="w", padx=16, pady=(0, 14))

        # 3. Paneles Inferiores: Top Productos y Desglose de Pagos
        panels_row = ctk.CTkFrame(self, fg_color="transparent")
        panels_row.grid(row=2, column=0, sticky="nsew")
        panels_row.columnconfigure(0, weight=3)
        panels_row.columnconfigure(1, weight=2)
        panels_row.rowconfigure(0, weight=1)

        # Panel Izquierdo: Top Artículos Sublimados
        p_top = ctk.CTkFrame(panels_row, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        p_top.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(p_top, text="🏆 Top 5 Productos Más Vendidos", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(anchor="w", padx=16, pady=(14, 10))
        
        self.scroll_top_prod = ctk.CTkScrollableFrame(p_top, fg_color="transparent")
        self.scroll_top_prod.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Panel Derecho: Métodos de Pago
        p_pagos = ctk.CTkFrame(panels_row, fg_color=COLORS["card_bg"], corner_radius=SIZES["corner_radius"], border_width=1, border_color=COLORS["border"])
        p_pagos.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(p_pagos, text="💳 Desglose por Método de Pago", font=FONTS["subtitle"], text_color=COLORS["text_primary"]).pack(anchor="w", padx=16, pady=(14, 10))

        self.scroll_pagos = ctk.CTkScrollableFrame(p_pagos, fg_color="transparent")
        self.scroll_pagos.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def al_cambiar_periodo(self, val):
        mapping = {
            "Hoy": "hoy",
            "Últimos 7 Días": "semana",
            "Este Mes": "mes",
            "Todo el Historial": "todos"
        }
        self.periodo_actual = mapping.get(val, "todos")
        self.cargar_datos()

    def cargar_datos(self):
        metricas = self.db_manager.obtener_metricas_dashboard(self.periodo_actual)
        cfg = self.db_manager.obtener_config()
        simbolo = cfg.get('moneda_simbolo', '$')

        # Actualizar KPIs
        self.lbl_kpi_ventas.configure(text=f"{simbolo} {metricas['ventas_totales']:,.2f}")
        self.lbl_kpi_facturas.configure(text=str(metricas['total_facturas']))
        self.lbl_kpi_ticket.configure(text=f"{simbolo} {metricas['ticket_promedio']:,.2f}")

        # Actualizar Top Productos
        for w in self.scroll_top_prod.winfo_children():
            w.destroy()

        if not metricas['top_productos']:
            ctk.CTkLabel(self.scroll_top_prod, text="No hay ventas registradas en este período.", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=40)
        else:
            for idx, p in enumerate(metricas['top_productos'], 1):
                card = ctk.CTkFrame(self.scroll_top_prod, fg_color=COLORS["surface_alt"], height=42, corner_radius=4)
                card.pack(fill="x", pady=3)
                
                # Ranking
                ctk.CTkLabel(card, text=f"#{idx}", font=FONTS["body_bold"], width=30, text_color=COLORS["primary"]).pack(side="left", padx=8)
                
                # Nombre
                ctk.CTkLabel(card, text=p['producto_nombre'], font=FONTS["body"], anchor="w").pack(side="left", fill="x", expand=True, padx=5)
                
                # Unidades y total
                txt_stats = f"{p['total_unidades']} uds.  |  {simbolo} {p['total_monto']:,.2f}"
                ctk.CTkLabel(card, text=txt_stats, font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(side="right", padx=12)

        # Actualizar Métodos de Pago
        for w in self.scroll_pagos.winfo_children():
            w.destroy()

        if not metricas['metodos_pago']:
            ctk.CTkLabel(self.scroll_pagos, text="Sin datos de pago en este período.", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=40)
        else:
            total_monto_periodo = max(1.0, metricas['ventas_totales'])
            for pago in metricas['metodos_pago']:
                card = ctk.CTkFrame(self.scroll_pagos, fg_color=COLORS["surface_alt"], corner_radius=4)
                card.pack(fill="x", pady=4, padx=2)

                top_line = ctk.CTkFrame(card, fg_color="transparent")
                top_line.pack(fill="x", padx=10, pady=(8, 4))

                pct = (pago['monto'] / total_monto_periodo) * 100
                ctk.CTkLabel(top_line, text=pago['metodo_pago'], font=FONTS["body_bold"], text_color=COLORS["text_primary"]).pack(side="left")
                ctk.CTkLabel(top_line, text=f"{simbolo} {pago['monto']:,.2f} ({pct:.1f}%)", font=FONTS["body"], text_color=COLORS["primary"]).pack(side="right")

                # Barra de progreso proporcional
                prog = ctk.CTkProgressBar(card, height=8, progress_color=COLORS["primary"], fg_color=COLORS["bg_dark"])
                prog.set(min(1.0, max(0.0, pct / 100.0)))
                prog.pack(fill="x", padx=10, pady=(0, 8))
