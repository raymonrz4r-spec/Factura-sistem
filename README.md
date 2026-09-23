# Sistema de Facturación - Taller de Sublimación & Personalizados

Aplicación de escritorio moderna, ergonómica y minimalista diseñada específicamente para tiendas y talleres de sublimación. Construida con **CustomTkinter**, base de datos **SQLite**, motor de reportes **ReportLab** y sistema de **respaldos automáticos semanales**.

---

## Características Principales

1. **Flujo de Trabajo Directo y Ágil**:
   - Inicia inmediatamente en la pantalla de **Nueva Factura** (sin pantallas de login innecesarias).
   - Botón de gran tamaño **"➕ AGREGAR PRODUCTO A LA FACTURA"** para fácil uso con mouse o pantallas táctiles.
   - Selección rápida de mercancía (Camisetas, Tazas 11oz/15oz, Gorras Trucker, Termos, Mousepads, etc.), Talla/Medida y Color.
   - **Precio libre a mano**: Permite ingresar el precio unitario exacto para cada trabajo o pedido especial.
   - Tabla dinámica de productos con eliminación y cálculo de subtotales en tiempo real.
   - Botón gigante **"✔ CONFIRMAR FACTURA"** que guarda la venta, genera el PDF y lo abre de inmediato listo para imprimir o enviar al cliente.

2. **Diseño Visual con Carga Cromática Baja**:
   - Paleta inspirada en lineamientos de diseño de **Stitch** (*Atelier Print Engine*).
   - Fondo neutro gris pizarra (*Slate 900 / 800 / 700*) con acento funcional en **Teal Profundo** (`#0F766E`), evitando la fatiga visual en jornadas largas de trabajo.

3. **Facturas en PDF Estéticas y Profesionales**:
   - Guardadas automáticamente en la carpeta de **Documentos del usuario** (`Documentos/Facturas_Sublimacion/Facturas_PDF/`).
   - Incluye logo de la empresa, datos fiscales del taller (RNC, teléfono, dirección), datos del cliente, tabla formateada con desglose, y **espacios para firmas** (*Firma Autorizada / Vendedor* y *Recibido Conforme / Cliente*).

4. **Copias de Seguridad (Backup Semanal & Manual)**:
   - **Backup Recurrente**: Evalúa al iniciar si han pasado 7 días o más desde el último respaldo y genera automáticamente una copia segura en `Documentos/Facturas_Sublimacion/Backups/`.
   - **Visualización en el Sidebar**: La parte inferior del sidebar muestra en todo momento el estado: `🔄 Último backup: YYYY-MM-DD HH:MM:SS`.
   - Soporte para creación manual inmediata y restauración con un clic.

5. **Reportes y Dashboard de Ventas**:
   - Filtros por: *Hoy*, *Últimos 7 Días*, *Este Mes*, *Todo el Historial*.
   - Indicadores clave: Ventas Totales, Facturas Emitidas, Ticket Promedio.
   - Ranking de los **Top 5 productos más vendidos** (unidades e ingresos).
   - Distribución gráfica por método de pago (Efectivo, Tarjeta, Transferencia).

6. **Historial de Facturas**:
   - Búsqueda interactiva por número de factura o nombre de cliente.
   - Botón para re-abrir o regenerar el PDF en cualquier momento.

---

## Estructura del Proyecto

```text
Factura/
├── main.py                  # Ventana principal y arranque
├── config.py                # Rutas, colores Slate/Teal y tamaños de botones
├── database/
│   ├── __init__.py
│   └── db_manager.py        # Tablas SQLite: facturas, detalles, empresa, catálogo
├── services/
│   ├── __init__.py
│   ├── backup_service.py    # Backup semanal automático, manual y restore
│   └── pdf_generator.py     # Generador de PDF con ReportLab y firmas
├── ui/
│   ├── __init__.py
│   ├── sidebar.py           # Menú lateral con indicador de último backup
│   ├── dialogs/
│   │   ├── __init__.py
│   │   └── add_product_modal.py # Modal para mercancía, talla, color y precio a mano
│   └── views/
│       ├── __init__.py
│       ├── invoice_view.py  # Pantalla principal de facturación
│       ├── dashboard_view.py# Reporte de ventas y métricas
│       ├── history_view.py  # Historial de ventas y apertura de PDF
│       └── settings_view.py # Configuración de negocio, logo y backup
├── assets/
│   └── logo_ejemplo.png     # Logo de ejemplo para pruebas
└── tests/
    ├── test_system.py       # Pruebas unitarias de BD, PDF y Backup
    └── test_ui.py           # Pruebas de integración de la UI
```

---

## Cómo Ejecutar la Aplicación

Todas las dependencias están instaladas y aisladas en el entorno virtual local **`.venv`**.

### Opción 1: Con el lanzador directo (Recomendado en Windows)
Simplemente haz doble clic en:
```text
iniciar.bat
```
*(Inicia la aplicación en segundo plano usando `.venv\Scripts\pythonw.exe` sin dejar consolas negras abiertas).*

### Opción 2: Desde la terminal de PowerShell o CMD
```powershell
.\.venv\Scripts\python main.py
```

### Opción 3: Activando el entorno virtual
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```
