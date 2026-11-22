# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: excepciones_y_logs.py
# Descripcion: Jerarquia de excepciones personalizadas y gestor de logs en archivo.
# ==============================================================================

from datetime import datetime  # Importa datetime para marcar fecha y hora exacta en cada log


class SoftwareFJError(Exception):
    """Excepcion base para todos los errores controlados del sistema Software FJ."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-000"):
        # Llama al constructor de la clase padre Exception con el mensaje descriptivo
        super().__init__(mensaje)
        # Almacena un codigo interno para clasificar el tipo de fallo
        self.codigo_error = codigo_error
        # Registra el momento exacto en que se instancio la excepcion
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos ingresados (nombre, documento, email, tarifas) son incorrectos."""

    def __init__(self, mensaje: str):
        # Inicializa con codigo ERR-101 asociado a validaciones de entrada
        super().__init__(mensaje, codigo_error="ERR-101")


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parametro obligatorio para crear un servicio o reserva."""

    def __init__(self, mensaje: str):
        # Inicializa con codigo ERR-102 asociado a parametros incompletos
        super().__init__(mensaje, codigo_error="ERR-102")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio ocupado o inactivo."""

    def __init__(self, mensaje: str):
        # Inicializa con codigo ERR-201 asociado a disponibilidad de recursos
        super().__init__(mensaje, codigo_error="ERR-201")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza ante duraciones negativas, estados incompatibles o fallos de calculo."""

    def __init__(self, mensaje: str):
        # Inicializa con codigo ERR-301 asociado al flujo de reservas
        super().__init__(mensaje, codigo_error="ERR-301")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta realizar una transicion de estado prohibida."""

    def __init__(self, mensaje: str):
        # Inicializa con codigo ERR-401 asociado a reglas de negocio
        super().__init__(mensaje, codigo_error="ERR-401")


class GestorLogs:
    """Clase encargada de registrar eventos y excepciones en un archivo plano (.log)."""

    def __init__(self, ruta_archivo: str = "sistema_fj.log"):
        # Define el nombre del archivo de salida donde quedara la auditoria
        self.ruta_archivo = ruta_archivo

    def registrar_evento(self, nivel: str, modulo: str, mensaje: str, detalle_error: Exception = None):
        """
        Escribe una linea estructurada en el archivo de logs usando try/except/finally.
        Nivel puede ser 'INFO', 'WARNING' o 'ERROR'.
        """
        # Obtiene la marca de tiempo actual formateada
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Construye la linea principal del registro
        linea = f"[{fecha_hora}] [{nivel}] [{modulo}] {mensaje}"

        # Si se adjunta una excepcion, extrae su causa encadenada (__cause__) si existe
        if detalle_error is not None:
            codigo = getattr(detalle_error, "codigo_error", "EX-STD")
            linea += f" | Codigo: {codigo} | Detalle: {repr(detalle_error)}"
            if detalle_error.__cause__ is not None:
                linea += f" | Causa original encadenada: {repr(detalle_error.__cause__)}"

        archivo = None  # Inicializa referencia del archivo en None
        try:
            # Abre el archivo en modo 'a' (append) con codificacion UTF-8 para no sobrescribir
            archivo = open(self.ruta_archivo, mode="a", encoding="utf-8")
            # Escribe el evento seguido de un salto de linea
            archivo.write(linea + "\n")
        except IOError as io_err:
            # Si falla la escritura en disco, notifica por consola sin detener el sistema
            print(f"[ALERTA LOG] No se pudo escribir en {self.ruta_archivo}: {io_err}")
        finally:
            # Bloque finally garantiza que el recurso de archivo siempre se cierre si fue abierto
            if archivo is not None and not archivo.closed:
                archivo.close()
