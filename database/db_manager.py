import sqlite3
import datetime
from pathlib import Path
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de configuración de la empresa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empresa_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    nombre_negocio TEXT DEFAULT 'Taller de Sublimación',
                    rnc_cedula TEXT DEFAULT '101-0000000-0',
                    telefono TEXT DEFAULT '(809) 000-0000',
                    email TEXT DEFAULT 'contacto@tallerdesublimacion.com',
                    direccion TEXT DEFAULT 'Calle Principal #123, Santo Domingo',
                    mensaje_pie TEXT DEFAULT '¡Gracias por preferir nuestros servicios de sublimación y personalización!',
                    logo_path TEXT DEFAULT '',
                    itbis_porcentaje REAL DEFAULT 18.0,
                    moneda_simbolo TEXT DEFAULT '$',
                    siguiente_numero INTEGER DEFAULT 1
                );
            """)

            # Insertar registro inicial si no existe
            cursor.execute("SELECT COUNT(*) FROM empresa_config WHERE id = 1;")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO empresa_config (id, nombre_negocio, rnc_cedula, telefono, email, direccion, mensaje_pie, itbis_porcentaje, moneda_simbolo, siguiente_numero)
                    VALUES (1, 'Atelier Sublimación & Estampados', '101-5555555-1', '(809) 555-0199', 'ventas@ateliersublimacion.com', 'Av. Las Américas #45, Edif. Comercial', '¡Gracias por confiar en nosotros! Prendas personalizadas con la más alta resolución.', 18.0, '$', 1);
                """)

            # Tabla de facturas emitidas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    cliente_nombre TEXT,
                    cliente_telefono TEXT,
                    cliente_rnc TEXT,
                    metodo_pago TEXT DEFAULT 'Efectivo',
                    subtotal REAL NOT NULL,
                    descuento REAL DEFAULT 0.0,
                    impuesto REAL DEFAULT 0.0,
                    total REAL NOT NULL,
                    pdf_ruta TEXT,
                    notas TEXT,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Tabla de detalles de productos en facturas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factura_detalles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factura_id INTEGER NOT NULL,
                    producto_nombre TEXT NOT NULL,
                    talla_medida TEXT,
                    color TEXT,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE
                );
            """)

            # Tabla de catálogo base / sugerencias de sublimación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS catalogo_sugerencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    categoria TEXT,
                    talla_sugerida TEXT,
                    color_sugerido TEXT,
                    precio_sugerido REAL
                );
            """)

            # Cargar catálogo de sublimación por defecto si está vacío
            cursor.execute("SELECT COUNT(*) FROM catalogo_sugerencias;")
            if cursor.fetchone()[0] == 0:
                productos_iniciales = [
                    ('Camiseta Poliéster Cuello Redondo', 'Textil', 'M', 'Blanco', 350.0),
                    ('Camiseta Dry-Fit Deportiva', 'Textil', 'L', 'Blanco', 450.0),
                    ('Taza Cerámica 11oz Grado A', 'Cerámica', '11 oz', 'Blanca', 250.0),
                    ('Taza Mágica 11oz Termosensible', 'Cerámica', '11 oz', 'Negro Mate', 380.0),
                    ('Taza Conica 12oz', 'Cerámica', '12 oz', 'Blanca', 280.0),
                    ('Gorra Trucker Frente Poliéster', 'Gorras', 'Ajustable', 'Blanco/Negro', 220.0),
                    ('Botella Térmica / Termo Aluminio', 'Aluminio', '600 ml', 'Plateado', 550.0),
                    ('Termo Sublimable Doble Pared', 'Acero', '500 ml', 'Blanco', 650.0),
                    ('Mousepad Rectangular Antideslizante', 'Accesorios', '22x18 cm', 'Blanco', 180.0),
                    ('Cojín Cuadrado con Relleno', 'Hogar', '40x40 cm', 'Blanco', 400.0),
                    ('Rompecabezas Sublimable', 'Regalos', 'A4 (120 piezas)', 'Blanco', 300.0),
                    ('Llavero Metálico Sublimable', 'Souvenirs', 'Estándar', 'Plateado', 120.0),
                    ('Bolsa Ecológica / Tote Bag', 'Textil', '38x42 cm', 'Beige', 250.0)
                ]
                cursor.executemany("""
                    INSERT OR IGNORE INTO catalogo_sugerencias (nombre, categoria, talla_sugerida, color_sugerido, precio_sugerido)
                    VALUES (?, ?, ?, ?, ?);
                """, productos_iniciales)

            # Tabla de metadatos de la aplicación (incluyendo último backup)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_metadata (
                    clave TEXT PRIMARY KEY,
                    valor TEXT
                );
            """)
            
            conn.commit()

    # --- Métodos de Configuración ---
    def obtener_config(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empresa_config WHERE id = 1;")
            row = cursor.fetchone()
            return dict(row) if row else {}

    def actualizar_config(self, datos):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE empresa_config SET
                    nombre_negocio = ?,
                    rnc_cedula = ?,
                    telefono = ?,
                    email = ?,
                    direccion = ?,
                    mensaje_pie = ?,
                    logo_path = ?,
                    itbis_porcentaje = ?,
                    moneda_simbolo = ?
                WHERE id = 1;
            """, (
                datos.get('nombre_negocio', ''),
                datos.get('rnc_cedula', ''),
                datos.get('telefono', ''),
                datos.get('email', ''),
                datos.get('direccion', ''),
                datos.get('mensaje_pie', ''),
                datos.get('logo_path', ''),
                float(datos.get('itbis_porcentaje', 18.0)),
                datos.get('moneda_simbolo', '$')
            ))
            conn.commit()

    def obtener_siguiente_numero_factura(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT siguiente_numero FROM empresa_config WHERE id = 1;")
            row = cursor.fetchone()
            num = row[0] if row else 1
            return f"FAC-{num:04d}"

    def incrementar_numero_factura(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE empresa_config SET siguiente_numero = siguiente_numero + 1 WHERE id = 1;")
            conn.commit()

    # --- Métodos de Facturación ---
    def guardar_factura(self, datos_factura, items):
        """
        datos_factura: dict(numero_factura, cliente_nombre, cliente_telefono, cliente_rnc,
                            metodo_pago, subtotal, descuento, impuesto, total, pdf_ruta, notas)
        items: list of dict(producto_nombre, talla_medida, color, cantidad, precio_unitario, subtotal)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO facturas (
                    numero_factura, fecha_hora, cliente_nombre, cliente_telefono, cliente_rnc,
                    metodo_pago, subtotal, descuento, impuesto, total, pdf_ruta, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                datos_factura['numero_factura'],
                fecha_actual,
                datos_factura.get('cliente_nombre', 'Cliente General'),
                datos_factura.get('cliente_telefono', ''),
                datos_factura.get('cliente_rnc', ''),
                datos_factura.get('metodo_pago', 'Efectivo'),
                float(datos_factura['subtotal']),
                float(datos_factura.get('descuento', 0.0)),
                float(datos_factura.get('impuesto', 0.0)),
                float(datos_factura['total']),
                datos_factura.get('pdf_ruta', ''),
                datos_factura.get('notas', '')
            ))
            factura_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO factura_detalles (
                        factura_id, producto_nombre, talla_medida, color, cantidad, precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    factura_id,
                    item['producto_nombre'],
                    item.get('talla_medida', ''),
                    item.get('color', ''),
                    int(item['cantidad']),
                    float(item['precio_unitario']),
                    float(item['subtotal'])
                ))

            # Incrementar contador de factura
            cursor.execute("UPDATE empresa_config SET siguiente_numero = siguiente_numero + 1 WHERE id = 1;")
            conn.commit()
            return factura_id

    def actualizar_ruta_pdf_factura(self, factura_id, ruta_pdf):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE facturas SET pdf_ruta = ? WHERE id = ?;", (ruta_pdf, factura_id))
            conn.commit()

    def obtener_facturas(self, busqueda=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if busqueda:
                termino = f"%{busqueda.strip()}%"
                cursor.execute("""
                    SELECT * FROM facturas
                    WHERE numero_factura LIKE ? OR cliente_nombre LIKE ? OR cliente_rnc LIKE ?
                    ORDER BY id DESC;
                """, (termino, termino, termino))
            else:
                cursor.execute("SELECT * FROM facturas ORDER BY id DESC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def obtener_factura_completa(self, factura_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM facturas WHERE id = ?;", (factura_id,))
            factura = cursor.fetchone()
            if not factura:
                return None
            
            cursor.execute("SELECT * FROM factura_detalles WHERE factura_id = ?;", (factura_id,))
            items = cursor.fetchall()
            
            return {
                "factura": dict(factura),
                "items": [dict(i) for i in items]
            }

    # --- Catálogo de Sugerencias ---
    def obtener_catalogo_sugerencias(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM catalogo_sugerencias ORDER BY nombre ASC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def agregar_o_actualizar_sugerencia(self, nombre, categoria, talla, color, precio):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO catalogo_sugerencias (nombre, categoria, talla_sugerida, color_sugerido, precio_sugerido)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(nombre) DO UPDATE SET
                    categoria = excluded.categoria,
                    talla_sugerida = excluded.talla_sugerida,
                    color_sugerido = excluded.color_sugerido,
                    precio_sugerido = excluded.precio_sugerido;
            """, (nombre, categoria, talla, color, precio))
            conn.commit()

    # --- Métricas para Dashboard ---
    def obtener_metricas_dashboard(self, periodo="todos"):
        """
        periodo: 'hoy', 'semana', 'mes', 'todos'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            hoy = datetime.date.today()
            filtro_fecha = ""
            params = []

            if periodo == "hoy":
                filtro_fecha = "WHERE date(fecha_hora) = date(?)"
                params = [hoy.strftime("%Y-%m-%d")]
            elif periodo == "semana":
                filtro_fecha = "WHERE date(fecha_hora) >= date(?, '-7 days')"
                params = [hoy.strftime("%Y-%m-%d")]
            elif periodo == "mes":
                primer_dia_mes = hoy.replace(day=1).strftime("%Y-%m-%d")
                filtro_fecha = "WHERE date(fecha_hora) >= date(?)"
                params = [primer_dia_mes]

            # Totales monetarios y conteo de facturas
            query_totales = f"""
                SELECT 
                    COUNT(*) as total_facturas,
                    COALESCE(SUM(total), 0.0) as ventas_totales,
                    COALESCE(AVG(total), 0.0) as ticket_promedio
                FROM facturas {filtro_fecha};
            """
            cursor.execute(query_totales, params)
            totales = dict(cursor.fetchone())

            # Top 5 productos más vendidos en el período
            query_top_prod = f"""
                SELECT 
                    fd.producto_nombre,
                    SUM(fd.cantidad) as total_unidades,
                    SUM(fd.subtotal) as total_monto
                FROM factura_detalles fd
                JOIN facturas f ON fd.factura_id = f.id
                {filtro_fecha}
                GROUP BY fd.producto_nombre
                ORDER BY total_unidades DESC
                LIMIT 5;
            """
            cursor.execute(query_top_prod, params)
            top_productos = [dict(r) for r in cursor.fetchall()]

            # Desglose por método de pago
            query_pagos = f"""
                SELECT 
                    metodo_pago,
                    COUNT(*) as cantidad,
                    COALESCE(SUM(total), 0.0) as monto
                FROM facturas
                {filtro_fecha}
                GROUP BY metodo_pago;
            """
            cursor.execute(query_pagos, params)
            metodos_pago = [dict(r) for r in cursor.fetchall()]

            return {
                "total_facturas": totales['total_facturas'],
                "ventas_totales": totales['ventas_totales'],
                "ticket_promedio": totales['ticket_promedio'],
                "top_productos": top_productos,
                "metodos_pago": metodos_pago
            }

    # --- Metadata y Backup Tracking ---
    def obtener_ultimo_backup(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM app_metadata WHERE clave = 'ultimo_backup';")
            row = cursor.fetchone()
            return row[0] if row else None

    def registrar_ultimo_backup(self, fecha_str=None):
        if not fecha_str:
            fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO app_metadata (clave, valor)
                VALUES ('ultimo_backup', ?)
                ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor;
            """, (fecha_str,))
            conn.commit()
            return fecha_str
