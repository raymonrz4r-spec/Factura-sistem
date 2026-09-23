import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

class TestValidatorsAndSanitization(unittest.TestCase):
    def test_validar_cedula_valida(self):
        # 40200000004 cumple con el algoritmo Módulo 10 de Cédula Dominicana
        es_val, msg = validar_cedula("40200000004")
        self.assertTrue(es_val)
        self.assertIn("válida", msg.lower())

        # Con guiones
        es_val_g, _ = validar_cedula("402-0000000-4")
        self.assertTrue(es_val_g)

    def test_validar_cedula_invalida(self):
        # Dígito verificador incorrecto
        es_val, msg = validar_cedula("40200000005")
        self.assertFalse(es_val)

        # Longitud incorrecta
        es_val_len, _ = validar_cedula("4020000000")
        self.assertFalse(es_val_len)

        # Dígitos repetidos
        es_val_rep, _ = validar_cedula("00000000000")
        self.assertFalse(es_val_rep)

    def test_validar_rnc_valido(self):
        # 101000007 cumple con el algoritmo Módulo 11 oficial
        es_val, msg = validar_rnc("101000007")
        self.assertTrue(es_val)
        self.assertIn("válido", msg.lower())

        # Con guiones
        es_val_g, _ = validar_rnc("101-00000-7")
        self.assertTrue(es_val_g)

    def test_validar_rnc_invalido(self):
        # Dígito verificador incorrecto
        es_val, _ = validar_rnc("101000008")
        self.assertFalse(es_val)

        # Longitud incorrecta
        es_val_len, _ = validar_rnc("1010000")
        self.assertFalse(es_val_len)

        # Dígitos repetidos
        es_val_rep, _ = validar_rnc("111111111")
        self.assertFalse(es_val_rep)

    def test_validar_cedula_o_rnc_detector(self):
        # RNC de 9 dígitos
        es_val_rnc, tipo_rnc, _ = validar_cedula_o_rnc("101000007")
        self.assertTrue(es_val_rnc)
        self.assertEqual(tipo_rnc, "RNC")

        # Cédula de 11 dígitos
        es_val_ced, tipo_ced, _ = validar_cedula_o_rnc("40200000004")
        self.assertTrue(es_val_ced)
        self.assertEqual(tipo_ced, "CÉDULA")

        # Vacío no obligatorio
        es_val_vacio, tipo_vacio, _ = validar_cedula_o_rnc("", obligatorio=False)
        self.assertTrue(es_val_vacio)
        self.assertEqual(tipo_vacio, "VACÍO")

        # Vacío obligatorio
        es_val_vacio_ob, tipo_vacio_ob, _ = validar_cedula_o_rnc("", obligatorio=True)
        self.assertFalse(es_val_vacio_ob)

        # Longitud inválida (ej. 10 dígitos)
        es_val_10, tipo_10, _ = validar_cedula_o_rnc("1234567890")
        self.assertFalse(es_val_10)

    def test_formateo(self):
        self.assertEqual(formatear_documento("40200000004"), "402-0000000-4")
        self.assertEqual(formatear_documento("101000007"), "101-00000-7")
        self.assertEqual(formatear_telefono("8095551234"), "(809) 555-1234")

    def test_sanitizar_alfanumerico(self):
        # Caracteres especiales peligrosos deben removerse, pero mantener letras, números, espacios y acentos
        sucio = "Sublimaciones Pérez & Hnos. <script>alert(1)</script> / S.R.L."
        limpio = sanitizar_alfanumerico(sucio)
        self.assertNotIn("<", limpio)
        self.assertNotIn(">", limpio)
        self.assertIn("Sublimaciones Pérez & Hnos.", limpio)
        self.assertIn("S.R.L.", limpio)

    def test_callbacks_teclado(self):
        # Solo números
        self.assertTrue(solo_numeros_callback("5", "809555"))
        self.assertFalse(solo_numeros_callback("a", "809a"))
        self.assertFalse(solo_numeros_callback("5", "123456789012"))  # Excede 11

        # Alfanumérico
        self.assertTrue(alfanumerico_callback("A", "Creaciones Gráficas & Eventos"))
        self.assertFalse(alfanumerico_callback("<", "Test <script>"))

if __name__ == "__main__":
    unittest.main()
