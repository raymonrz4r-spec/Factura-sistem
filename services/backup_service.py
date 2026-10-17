"""
SISTEMA DE COPIAS DE SEGURIDAD (backup_service.py)

EXPLICACION PARA PERSONAS NO TECNICAS:
Este archivo es la poliza de seguro del taller.
En cualquier negocio que use computadoras, existe el riesgo de que la máquina
falle, se apague de golpe o se dañe. Este codigo previene la perdida de datos:

1. Respaldo Silencioso: Cada 7 dias, genera automaticamente un clon exacto
   de toda la base de datos (facturas, clientes, productos y dinero).
2. Respaldo a Peticion: Permite que el dueño presione un boton y guarde una
   copia en una memoria USB o en la nube cuando quiera.
3. Restauracion Facil: Si alguna vez ocurre un desastre, permite cargar un
   respaldo anterior con un solo clic y recuperar todo como estaba.
"""

import os
import shutil
import sqlite3
import datetime
from pathlib import Path
from config import DB_PATH, BACKUP_STORAGE_DIR

class BackupService:
    def __init__(self, db_manager, on_backup_callback=None):
        self.db_manager = db_manager
        self.on_backup_callback = on_backup_callback
        BACKUP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def set_callback(self, callback):
        self.on_backup_callback = callback

    def crear_backup(self, tipo="manual", destino_personalizado=None):
        """
        Crea una copia de seguridad segura de la base de datos utilizando la API de backup de SQLite.
        tipo: 'manual' o 'auto'
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fecha_legible = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if destino_personalizado:
            backup_file = Path(destino_personalizado)
        else:
            backup_file = BACKUP_STORAGE_DIR / f"backup_{tipo}_{timestamp}.db"

        # Conexión origen y conexión destino para backup transaccional consistente
        origen_conn = sqlite3.connect(str(self.db_manager.db_path))
        destino_conn = sqlite3.connect(str(backup_file))
        try:
            with destino_conn:
                origen_conn.backup(destino_conn)
        finally:
            origen_conn.close()
            destino_conn.close()

        # Actualizar metadatos en la base de datos principal
        self.db_manager.registrar_ultimo_backup(fecha_legible)

        # Disparar callback para refrescar la UI del sidebar
        if self.on_backup_callback:
            self.on_backup_callback(fecha_legible)

        return str(backup_file), fecha_legible

    def verificar_y_ejecutar_backup_semanal(self):
        """
        Evalúa si han pasado 7 días o más desde el último respaldo o si nunca se ha hecho uno.
        Si corresponde, ejecuta el respaldo semanal automático.
        """
        ultimo_backup_str = self.db_manager.obtener_ultimo_backup()
        ejecutar = False

        if not ultimo_backup_str:
            # Nunca se ha realizado un backup
            ejecutar = True
        else:
            try:
                # Formatos esperados: "%Y-%m-%d %H:%M:%S" o "%Y-%m-%d"
                formato = "%Y-%m-%d %H:%M:%S" if " " in ultimo_backup_str else "%Y-%m-%d"
                fecha_ultimo = datetime.datetime.strptime(ultimo_backup_str, formato)
                dias_transcurridos = (datetime.datetime.now() - fecha_ultimo).days
                if dias_transcurridos >= 7:
                    ejecutar = True
            except Exception:
                ejecutar = True

        if ejecutar:
            try:
                archivo, fecha = self.crear_backup(tipo="auto")
                return True, archivo, fecha
            except Exception as e:
                print(f"Error al realizar backup automático: {e}")
                return False, None, None

        return False, None, ultimo_backup_str

    def restaurar_backup(self, archivo_backup_path):
        """
        Restaura la base de datos a partir de un archivo .db válido.
        """
        origen = Path(archivo_backup_path)
        if not origen.exists():
            raise FileNotFoundError(f"No se encontró el archivo de backup: {origen}")

        # Validar que sea una base de datos SQLite válida
        try:
            test_conn = sqlite3.connect(str(origen))
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
            test_conn.close()
            if not tablas:
                raise ValueError("El archivo no contiene tablas válidas de SQLite.")
        except Exception as e:
            raise ValueError(f"El archivo seleccionado no es una base de datos válida: {e}")

        # Realizar backup temporal de seguridad antes de sobreescribir
        target_path = Path(self.db_manager.db_path)
        temp_pre_restore = BACKUP_STORAGE_DIR / f"pre_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if target_path.exists():
            shutil.copy2(target_path, temp_pre_restore)

        # Sobreescribir de forma segura
        shutil.copy2(origen, target_path)
        
        # Registrar fecha de restauración
        fecha_act = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db_manager.registrar_ultimo_backup(fecha_act)

        if self.on_backup_callback:
            self.on_backup_callback(fecha_act)

        return True

    def listar_backups(self):
        """Retorna la lista de archivos de backup disponibles ordenados por fecha descendente."""
        if not BACKUP_STORAGE_DIR.exists():
            return []
        
        archivos = []
        for f in BACKUP_STORAGE_DIR.glob("*.db"):
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
            archivos.append({
                "nombre": f.name,
                "ruta": str(f),
                "tamano_kb": round(f.stat().st_size / 1024, 2),
                "fecha": mtime.strftime("%Y-%m-%d %H:%M:%S")
            })
        archivos.sort(key=lambda x: x["fecha"], reverse=True)
        return archivos
