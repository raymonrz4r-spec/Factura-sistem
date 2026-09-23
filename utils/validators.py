import re

def validar_cedula(cedula: str) -> tuple[bool, str]:
    """
    Valida una Cédula de Identidad y Electoral Dominicana (11 dígitos numéricos).
    Utiliza el algoritmo de Módulo 10 (Luhn con pesos alternados 1 y 2).
    """
    numeros = "".join(c for c in str(cedula) if c.isdigit())
    
    if len(numeros) != 11:
        return False, f"La cédula debe contener exactamente 11 dígitos (tiene {len(numeros)})."

    if len(set(numeros)) == 1:
        return False, "Cédula inválida (dígitos repetidos)."

    # Algoritmo de validación de cédula dominicana
    pesos = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0

    for i in range(10):
        mult = int(numeros[i]) * pesos[i]
        if mult >= 10:
            mult = (mult // 10) + (mult % 10)
        suma += mult

    digito_verificador = (10 - (suma % 10)) % 10

    if digito_verificador == int(numeros[10]):
        return True, "Cédula válida"
    else:
        return False, f"Cédula inválida: el dígito verificador no coincide (esperado {digito_verificador}, recibido {numeros[10]})."


def validar_rnc(rnc: str) -> tuple[bool, str]:
    """
    Valida un Registro Nacional de Contribuyentes (RNC) de República Dominicana (9 dígitos numéricos).
    Utiliza el algoritmo oficial de Módulo 11 con pesos [7, 9, 8, 6, 5, 4, 3, 2].
    """
    numeros = "".join(c for c in str(rnc) if c.isdigit())

    if len(numeros) != 9:
        return False, f"El RNC debe contener exactamente 9 dígitos (tiene {len(numeros)})."

    if len(set(numeros)) == 1:
        return False, "RNC inválido (dígitos repetidos)."

    pesos = [7, 9, 8, 6, 5, 4, 3, 2]
    suma = sum(int(numeros[i]) * pesos[i] for i in range(8))
    resto = suma % 11

    if resto == 0:
        digito_verificador = 2
    elif resto == 1:
        digito_verificador = 1
    else:
        digito_verificador = 11 - resto

    if digito_verificador == int(numeros[8]):
        return True, "RNC válido"
    else:
        return False, f"RNC inválido: el dígito verificador no coincide (esperado {digito_verificador}, recibido {numeros[8]})."


def validar_cedula_o_rnc(documento: str, obligatorio: bool = False) -> tuple[bool, str, str]:
    """
    Evalúa si un documento es una Cédula (11 dígitos) o un RNC (9 dígitos) válido.
    Retorna: (es_valido, tipo_detectado, mensaje_error_o_confirmacion)
    tipo_detectado: 'CÉDULA', 'RNC' o 'VACÍO'
    """
    doc_limpio = "".join(c for c in str(documento or "") if c.isdigit())

    if not doc_limpio:
        if obligatorio:
            return False, "VACÍO", "El campo de Cédula o RNC es obligatorio."
        return True, "VACÍO", "Documento no especificado (Consumidor Final)"

    if len(doc_limpio) == 9:
        es_val, msg = validar_rnc(doc_limpio)
        return es_val, "RNC", msg
    elif len(doc_limpio) == 11:
        es_val, msg = validar_cedula(doc_limpio)
        return es_val, "CÉDULA", msg
    else:
        return False, "DESCONOCIDO", f"Longitud incorrecta ({len(doc_limpio)} dígitos). Debe ser un RNC (9 dígitos) o Cédula (11 dígitos)."


def formatear_documento(documento: str) -> str:
    """Formatea la cédula como XXX-XXXXXXX-X o el RNC como XXX-XXXXX-X"""
    digits = "".join(c for c in str(documento or "") if c.isdigit())
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:10]}-{digits[10]}"
    elif len(digits) == 9:
        return f"{digits[:3]}-{digits[3:8]}-{digits[8]}"
    return documento


def formatear_telefono(telefono: str) -> str:
    """Formatea un teléfono de 10 dígitos como (XXX) XXX-XXXX"""
    digits = "".join(c for c in str(telefono or "") if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return telefono


def sanitizar_alfanumerico(texto: str) -> str:
    """
    Permite caracteres alfanuméricos, letras acentuadas, espacios y puntuación comercial básica.
    Remueve caracteres potencialmente peligrosos o de control.
    """
    if not texto:
        return ""
    # Permitir letras, números, espacios, acentos y signos comerciales básicos: . , - & / '
    limpio = re.sub(r"[^\w\s\.,\-&/']", "", texto, flags=re.UNICODE)
    # Limpiar espacios repetidos
    return re.sub(r"\s+", " ", limpio).strip()


def solo_numeros_callback(char: str, nuevo_valor: str, max_len: int = 11) -> bool:
    """
    Callback para validación a nivel de Tkinter (validate='key').
    Solo permite ingresar caracteres numéricos y controla la longitud máxima.
    """
    if not nuevo_valor:
        return True
    if len(nuevo_valor) > max_len:
        return False
    return nuevo_valor.isdigit()


def alfanumerico_callback(char: str, nuevo_valor: str, max_len: int = 80) -> bool:
    """
    Callback para validación de campos de texto alfanuméricos en Tkinter.
    """
    if not nuevo_valor:
        return True
    if len(nuevo_valor) > max_len:
        return False
    # Permitir caracteres alfanuméricos, espacios y signos comerciales seguros
    return bool(re.match(r"^[\w\s\.,\-&/']*$", nuevo_valor, flags=re.UNICODE))
