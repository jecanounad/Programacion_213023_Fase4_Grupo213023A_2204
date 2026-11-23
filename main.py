# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: main.py
# Descripcion: Orquestador del sistema Software FJ y simulacion de 12 operaciones.
# ==============================================================================

from excepciones_y_logs import SoftwareFJError, GestorLogs
from modelos_base import Cliente
from servicios import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva


class SistemaSoftwareFJ:
    """Controlador principal que administra listas en memoria sin bases de datos."""

    def __init__(self):
        # Inicializa el gestor de auditoria en archivo plano
        self.logger = GestorLogs("sistema_fj.log")
        # Listas internas en memoria para almacenar objetos del dominio
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.logger.registrar_evento("INFO", "Sistema", "=== INICIO DE EJECUCION SISTEMA SOFTWARE FJ ===")

    def registrar_cliente(self, id_c: str, nombre: str, doc: str, correo: str, tel: str):
        """Intenta instanciar y almacenar un Cliente capturando errores de validacion."""
        try:
            nuevo_cliente = Cliente(id_c, nombre, doc, correo, tel)
            self.clientes.append(nuevo_cliente)
            self.logger.registrar_evento("INFO", "Clientes", f"Cliente registrado: {nuevo_cliente.obtener_resumen()}")
            print(f"  [OK] {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente
        except SoftwareFJError as err:
            self.logger.registrar_evento("ERROR", "Clientes", f"Fallo registro cliente {id_c}", err)
            print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")
            return None

    def registrar_servicio(self, servicio_obj: Servicio):
        """Almacena un servicio especializado previamente validado en la lista interna."""
        self.servicios.append(servicio_obj)
        self.logger.registrar_evento("INFO", "Servicios", f"Servicio agregado: {servicio_obj.obtener_resumen()}")
        print(f"  [OK] {servicio_obj.obtener_resumen()}")
        return servicio_obj

    def crear_y_confirmar_reserva(
        self,
        id_r: str,
        cliente: Cliente,
        servicio: Servicio,
        horas: int,
        desc: float = 0.0,
    ):
        """Crea una reserva y ejecuta su confirmacion manteniendo el sistema estable ante fallos."""
        try:
            reserva = Reserva(
                id_r,
                cliente,
                servicio,
                horas,
                descuento=desc,
                gestor_logs=self.logger,
            )
            reserva.confirmar()
            self.reservas.append(reserva)
            print(f"  [OK] {reserva.obtener_resumen()}")
            return reserva
        except SoftwareFJError as err:
            # El error ya fue registrado en el log; el programa continua sin interrupciones
            print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")
            return None


def ejecutar_simulacion():
    """Ejecuta 12 operaciones secuenciales (validas e invalidas) para validar robustez."""
    print("==========================================================================")
    print("   SOFTWARE FJ - SISTEMA INTEGRAL DE CLIENTES, SERVICIOS Y RESERVAS       ")
    print("==========================================================================\n")

    sistema = SistemaSoftwareFJ()

    # --------------------------------------------------------------------------
    # OPERACION 1: Registro valido de Cliente 1
    # --------------------------------------------------------------------------
    print("1. Registrando cliente valido (CLI-01)...")
    cli_1 = sistema.registrar_cliente("CLI-01", "Laura Valentina Gomez", "1053849201", "laura.gomez@empresa.co", "3104567890")

    # --------------------------------------------------------------------------
    # OPERACION 2: Registro valido de Cliente 2
    # --------------------------------------------------------------------------
    print("\n2. Registrando cliente valido (CLI-02)...")
    cli_2 = sistema.registrar_cliente("CLI-02", "Carlos Andres Mendoza", "75098321", "cmendoza@techcorp.com", "3209876543")

    # --------------------------------------------------------------------------
    # OPERACION 3: Registro INVALIDO de Cliente (correo mal formado y documento corto)
    # --------------------------------------------------------------------------
    print("\n3. Intentando registrar cliente con datos invalidos (CLI-03)...")
    sistema.registrar_cliente("CLI-03", "Pedro Ruiz", "123", "pedro_sin_arroba.com", "3001112233")

    # --------------------------------------------------------------------------
    # OPERACION 4: Creacion valida de Servicio 1 (Reserva de Sala)
    # --------------------------------------------------------------------------
    print("\n4. Creando servicio valido: Sala de Juntas Ejecutiva (SRV-01)...")
    srv_sala = None
    try:
        srv_sala = ReservaSala("SRV-01", "Sala Innovacion 4K", 80000.0, capacidad=20, tiene_proyector=True)
        sistema.registrar_servicio(srv_sala)
    except SoftwareFJError as err:
        sistema.logger.registrar_evento("ERROR", "Servicios", "Fallo creando SRV-01", err)
        print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # --------------------------------------------------------------------------
    # OPERACION 5: Creacion valida de Servicio 2 (Alquiler de Equipo)
    # --------------------------------------------------------------------------
    print("\n5. Creando servicio valido: Workstation Grafica (SRV-02)...")
    srv_equipo = None
    try:
        srv_equipo = AlquilerEquipo("SRV-02", "Dell Precision RTX", 45000.0, gama="WORKSTATION", incluye_seguro=True)
        sistema.registrar_servicio(srv_equipo)
    except SoftwareFJError as err:
        sistema.logger.registrar_evento("ERROR", "Servicios", "Fallo creando SRV-02", err)
        print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # --------------------------------------------------------------------------
    # OPERACION 6: Creacion valida de Servicio 3 (Asesoria Especializada)
    # --------------------------------------------------------------------------
    print("\n6. Creando servicio valido: Consultoria Cloud & Seguridad (SRV-03)...")
    srv_asesoria = None
    try:
        srv_asesoria = AsesoriaEspecializada("SRV-03", "Auditoria DevSecOps", 120000.0, especialidad="Ciberseguridad", es_urgente=True)
        sistema.registrar_servicio(srv_asesoria)
    except SoftwareFJError as err:
        sistema.logger.registrar_evento("ERROR", "Servicios", "Fallo creando SRV-03", err)
        print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # --------------------------------------------------------------------------
    # OPERACION 7: Creacion INVALIDA de Servicio (Tarifa no numerica -> Encadenamiento)
    # --------------------------------------------------------------------------
    print("\n7. Intentando crear servicio con tarifa corrupta ('GRATIS')...")
    try:
        srv_malo = AlquilerEquipo("SRV-99", "Laptop Basica", "GRATIS", gama="MEDIA")
        sistema.registrar_servicio(srv_malo)
    except SoftwareFJError as err:
        sistema.logger.registrar_evento("ERROR", "Servicios", "Fallo controlado al crear SRV-99", err)
        print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # --------------------------------------------------------------------------
    # OPERACION 8: Reserva EXITOSA de Sala con descuento corporativo del 10%
    # --------------------------------------------------------------------------
    print("\n8. Procesando reserva exitosa (RES-01) de Sala para Laura Gomez...")
    res_1 = sistema.crear_y_confirmar_reserva("RES-01", cli_1, srv_sala, horas=4, desc=0.10)

    # --------------------------------------------------------------------------
    # OPERACION 9: Reserva FALLIDA por servicio ya ocupado (SRV-01 no disponible)
    # --------------------------------------------------------------------------
    print("\n9. Intentando reservar la misma Sala ya ocupada para Carlos Mendoza (RES-02)...")
    sistema.crear_y_confirmar_reserva("RES-02", cli_2, srv_sala, horas=2)

    # --------------------------------------------------------------------------
    # OPERACION 10: Reserva FALLIDA por duracion negativa (-5 horas)
    # --------------------------------------------------------------------------
    print("\n10. Intentando crear reserva con duracion negativa (-5 horas)...")
    sistema.crear_y_confirmar_reserva("RES-03", cli_2, srv_equipo, horas=-5)

    # --------------------------------------------------------------------------
    # OPERACION 11: Reserva EXITOSA de Asesoria Urgente + Procesamiento final
    # --------------------------------------------------------------------------
    print("\n11. Creando, confirmando y procesando Asesoria Urgente (RES-04)...")
    res_4 = sistema.crear_y_confirmar_reserva("RES-04", cli_2, srv_asesoria, horas=3, desc=0.05)
    if res_4:
        try:
            res_4.completar()
            print(f"  [OK] Reserva finalizada: {res_4.obtener_resumen()}")
        except SoftwareFJError as err:
            print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # --------------------------------------------------------------------------
    # OPERACION 12: Intento INVALIDO de cancelar una reserva ya PROCESADA
    # --------------------------------------------------------------------------
    print("\n12. Intentando cancelar reserva RES-04 que ya fue PROCESADA...")
    if res_4:
        try:
            res_4.cancelar("Cambio de agenda de ultima hora")
        except SoftwareFJError as err:
            print(f"  [ERROR CONTROLADO - {err.codigo_error}] {err}")

    # Resumen final del estado en memoria
    print("\n==========================================================================")
    print("SIMULACION COMPLETADA SIN INTERRUPCIONES.")
    print(f"Clientes activos: {len(sistema.clientes)} | Servicios: {len(sistema.servicios)} | Reservas registradas: {len(sistema.reservas)}")
    print("Todos los eventos y errores fueron registrados en 'sistema_fj.log'.")
    print("==========================================================================")
    sistema.logger.registrar_evento("INFO", "Sistema", "=== FIN DE EJECUCION SISTEMA SOFTWARE FJ ===")


if __name__ == "__main__":
    ejecutar_simulacion()