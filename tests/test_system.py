import os
import sys
import unittest
import tempfile
import shutil
import datetime
from pathlib import Path

# Agregar raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager
from services.backup_service import BackupService
from services.pdf_generator import PDFGenerator

class TestSublimacionSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_pos.db"
        self.db = DatabaseManager(self.db_path)
        self.backup_svc = BackupService(self.db)
        self.pdf_gen = PDFGenerator(self.db)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_empresa_config_default(self):
        cfg = self.db.obtener_config()
        self.assertIsNotNone(cfg)
        self.assertIn("Atelier", cfg['nombre_negocio'])
        self.assertEqual(cfg['itbis_porcentaje'], 18.0)
        self.assertEqual(cfg['moneda_simbolo'], '$')

    def test_actualizar_config(self):
        nuevos_datos = {
            "nombre_negocio": "Sublimaciones Express RD",
            "rnc_cedula": "131-99999-9",
            "telefono": "(809) 555-9999",
            "email": "info@express.com",
            "direccion": "Calle Sol #45",
            "mensaje_pie": "Garantía de 30 días",
            "logo_path": "",
            "itbis_porcentaje": 16.0,
            "moneda_simbolo": "RD$"
        }
        self.db.actualizar_config(nuevos_datos)
        cfg = self.db.obtener_config()
        self.assertEqual(cfg['nombre_negocio'], "Sublimaciones Express RD")
        self.assertEqual(cfg['itbis_porcentaje'], 16.0)
        self.assertEqual(cfg['moneda_simbolo'], "RD$")

    def test_guardar_y_obtener_factura(self):
        num_factura = self.db.obtener_siguiente_numero_factura()
        self.assertEqual(num_factura, "FAC-0001")

        datos_factura = {
            "numero_factura": num_factura,
            "cliente_nombre": "Carlos Santana",
            "cliente_telefono": "809-444-5555",
            "cliente_rnc": "001-1234567-8",
            "metodo_pago": "Transferencia Bancaria",
            "subtotal": 1200.0,
            "descuento": 200.0,
            "impuesto": 180.0,
            "total": 1180.0,
            "notas": "Impresión de alta resolución"
        }

        items = [
            {
                "producto_nombre": "Taza Mágica 11oz",
                "talla_medida": "11 oz",
                "color": "Negro Mate",
                "cantidad": 2,
                "precio_unitario": 350.0,
                "subtotal": 700.0
            },
            {
                "producto_nombre": "Camiseta Dry-Fit",
                "talla_medida": "L",
                "color": "Blanco",
                "cantidad": 1,
                "precio_unitario": 500.0,
                "subtotal": 500.0
            }
        ]

        factura_id = self.db.guardar_factura(datos_factura, items)
        self.assertGreater(factura_id, 0)

        # Verificar incremento de número
        sig_num = self.db.obtener_siguiente_numero_factura()
        self.assertEqual(sig_num, "FAC-0002")

        # Verificar factura completa
        completa = self.db.obtener_factura_completa(factura_id)
        self.assertEqual(completa['factura']['cliente_nombre'], "Carlos Santana")
        self.assertEqual(len(completa['items']), 2)
        self.assertEqual(completa['items'][0]['producto_nombre'], "Taza Mágica 11oz")

    def test_pdf_generacion(self):
        # Insertar factura
        num = self.db.obtener_siguiente_numero_factura()
        factura_id = self.db.guardar_factura(
            {
                "numero_factura": num,
                "cliente_nombre": "Maria Lopez",
                "cliente_telefono": "809-888-9999",
                "cliente_rnc": "101-9988776-5",
                "metodo_pago": "Efectivo",
                "subtotal": 800.0,
                "descuento": 0.0,
                "impuesto": 144.0,
                "total": 944.0,
                "notas": "Sublimado full color"
            },
            [
                {
                    "producto_nombre": "Gorra Trucker",
                    "talla_medida": "Ajustable",
                    "color": "Blanco/Azul",
                    "cantidad": 4,
                    "precio_unitario": 200.0,
                    "subtotal": 800.0
                }
            ]
        )

        pdf_path = self.pdf_gen.generar_factura_pdf(factura_id)
        self.assertTrue(Path(pdf_path).exists())
        self.assertGreater(Path(pdf_path).stat().st_size, 1000)

    def test_metricas_dashboard(self):
        num = self.db.obtener_siguiente_numero_factura()
        self.db.guardar_factura(
            {
                "numero_factura": num,
                "cliente_nombre": "Pedro Martinez",
                "metodo_pago": "Efectivo",
                "subtotal": 1000.0,
                "total": 1000.0
            },
            [
                {"producto_nombre": "Taza Cerámica 11oz", "talla_medida": "11 oz", "color": "Blanco", "cantidad": 4, "precio_unitario": 250.0, "subtotal": 1000.0}
            ]
        )

        metricas = self.db.obtener_metricas_dashboard("todos")
        self.assertGreaterEqual(metricas['total_facturas'], 1)
        self.assertGreaterEqual(metricas['ventas_totales'], 1000.0)
        self.assertTrue(len(metricas['top_productos']) > 0)

    def test_backup_y_restore(self):
        callback_called = []
        def on_backup(fecha):
            callback_called.append(fecha)

        self.backup_svc.set_callback(on_backup)

        # 1. Crear backup manual
        backup_file, fecha = self.backup_svc.crear_backup(tipo="test")
        self.assertTrue(Path(backup_file).exists())
        self.assertEqual(len(callback_called), 1)

        # 2. Verificar que se registró la fecha
        ultimo_bkp = self.db.obtener_ultimo_backup()
        self.assertEqual(ultimo_bkp, fecha)

        # 3. Insertar factura adicional
        num = self.db.obtener_siguiente_numero_factura()
        self.db.guardar_factura(
            {"numero_factura": num, "subtotal": 500.0, "total": 500.0},
            [{"producto_nombre": "Item Test", "cantidad": 1, "precio_unitario": 500.0, "subtotal": 500.0}]
        )
        self.assertEqual(len(self.db.obtener_facturas()), 1)

        # 4. Restaurar backup (cuando no había facturas)
        self.backup_svc.restaurar_backup(backup_file)
        facturas_post_restore = self.db.obtener_facturas()
        self.assertEqual(len(facturas_post_restore), 0)

    def test_backup_recurrente_semanal_logica(self):
        # Simular fecha de último backup hace 8 días
        hace_8_dias = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
        self.db.registrar_ultimo_backup(hace_8_dias)

        ejecutado, archivo, fecha = self.backup_svc.verificar_y_ejecutar_backup_semanal()
        self.assertTrue(ejecutado)
        self.assertIsNotNone(archivo)
        self.assertTrue(Path(archivo).exists())

if __name__ == "__main__":
    unittest.main()
