import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import SublimacionFacturaApp

class TestUISmoke(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_app_instantiation_and_navigation(self):
        # Iniciar app sin entrar en el mainloop
        app = SublimacionFacturaApp()
        app.withdraw()  # Ocultar ventana para no parpadear en pantalla

        try:
            # 1. Verificar que arranca en la vista de facturación
            self.assertEqual(app.sidebar.vista_actual, "factura")
            self.assertIn("factura", app.vistas)
            self.assertIn("dashboard", app.vistas)
            self.assertIn("historial", app.vistas)
            self.assertIn("configuracion", app.vistas)

            # 2. Probar navegación a todas las vistas
            for vista in ["dashboard", "historial", "configuracion", "factura"]:
                app.sidebar.seleccionar_vista(vista)
                self.assertEqual(app.sidebar.vista_actual, vista)

            # 3. Probar agregar item a la factura y verificar totales
            factura_view = app.vistas["factura"]
            test_item = {
                "producto_nombre": "Taza Cerámica 11oz",
                "talla_medida": "11 oz",
                "color": "Blanco",
                "cantidad": 3,
                "precio_unitario": 200.0,
                "subtotal": 600.0
            }
            factura_view.agregar_item_a_tabla(test_item)
            self.assertEqual(len(factura_view.items), 1)

            totales = factura_view.recalcular_totales()
            self.assertEqual(totales["subtotal"], 600.0)
            self.assertGreater(totales["total"], 600.0)  # Con ITBIS

            # 4. Probar actualización del label de último backup en el sidebar
            fecha_test = "2026-09-21 22:30:00"
            app.sidebar.refrescar_ultimo_backup(fecha_test)
            self.assertIn(fecha_test, app.sidebar.lbl_ultimo_backup.cget("text"))

            # 5. Probar estado dinámico de RNC/Cédula en vivo
            factura_view.entry_cliente_rnc.delete(0, "end")
            factura_view.entry_cliente_rnc.insert(0, "101000007")  # RNC válido
            factura_view.al_escribir_rnc()
            self.assertIn("RNC Válido", factura_view.lbl_rnc_status.cget("text"))

            factura_view.entry_cliente_rnc.delete(0, "end")
            factura_view.entry_cliente_rnc.insert(0, "101000008")  # RNC inválido
            factura_view.al_escribir_rnc()
            self.assertIn("RNC Inválido", factura_view.lbl_rnc_status.cget("text"))

            factura_view.entry_cliente_rnc.delete(0, "end")
            factura_view.entry_cliente_rnc.insert(0, "40200000004")  # Cédula válida
            factura_view.al_escribir_rnc()
            self.assertIn("Cédula Válida", factura_view.lbl_rnc_status.cget("text"))

        finally:
            app.destroy()

if __name__ == "__main__":
    unittest.main()
