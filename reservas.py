# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: reservas.py
# Descripcion: Gestion transaccional de reservas con manejo avanzado de excepciones.
# ==============================================================================

from modelos_base import EntidadBase, Cliente
from servicios import Servicio
from excepciones_y_logs import (
    DatoInvalidoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    GestorLogs
)


class Reserva(EntidadBase):
    """Integra un Cliente, un Servicio y la duracion para gestionar el ciclo de reserva."""

    # Estados validos del ciclo de vida de una reserva
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_PROCESADA = "PROCESADA"
    ESTADO_CANCELADA = "CANCELADA"

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion_horas: int, logger: GestorLogs):
        super().__init__(id_reserva)
        # Valida que se reciban instancias reales de Cliente y Servicio
        if not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("La reserva requiere una instancia valida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("La reserva requiere una instancia valida de Servicio.")

        self.cliente = cliente
        self.servicio = servicio
        self.logger = logger
        self._estado = self.ESTADO_PENDIENTE
        self._costo_total = 0.0

        # Valida la duracion en horas
        self.duracion_horas = duracion_horas
        self.validar()

    @property
    def duracion_horas(self) -> int:
        return self._duracion_horas

    @duracion_horas.setter
    def duracion_horas(self, valor: int):
        # Valida que la duracion sea un entero positivo (1 a 720 horas)
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0 or valor > 720:
            raise ReservaInvalidaError(f"Duracion de reserva invalida: '{valor}'. Debe ser entre 1 y 720 horas.")
        self._duracion_horas = valor

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def validar(self) -> bool:
        """Verifica integridad de la reserva antes de confirmar."""
        self.cliente.validar()
        self.servicio.validar()
        return True

    def confirmar(self, descuento: float = 0.0, impuesto: float = 0.19):
        """
        Confirma la reserva verificando disponibilidad y calculando costos.
        Implementa try / except / else / finally y encadenamiento de excepciones.
        """
        try:
            # Verifica que la reserva este en estado PENDIENTE
            if self._estado != self.ESTADO_PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar la reserva {self.id_entidad} porque su estado es {self._estado}."
                )

            # Verifica que el servicio no haya sido ocupado por otra reserva activa
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.servicio.nombre_servicio}' ({self.servicio.id_entidad}) no esta disponible."
                )

            # Valida rango logico del descuento (0% a 50%)
            if not (0.0 <= descuento <= 0.50):
                raise DatoInvalidoError(f"Descuento fuera de rango permitido (0.0 - 0.50): {descuento}")

            # Calcula costo polimorficamente segun el tipo de servicio
            self._costo_total = self.servicio.calcular_costo(
                horas=self.duracion_horas,
                impuesto=impuesto,
                descuento=descuento
            )

        except (ServicioNoDisponibleError, OperacionNoPermitidaError) as err_negocio:
            # Registra error de negocio en log y relanza sin perder traza
            self.logger.registrar_evento("ERROR", "Reservas", f"Fallo al confirmar {self.id_entidad}", err_negocio)
            raise
        except Exception as err_inesperado:
            # Encadena cualquier otro fallo dentro de ReservaInvalidaError usando 'from'
            error_encadenado = ReservaInvalidaError(
                f"Error critico calculando o confirmando reserva {self.id_entidad}."
            )
            error_encadenado.__cause__ = err_inesperado
            self.logger.registrar_evento("ERROR", "Reservas", "Excepcion encadenada en confirmacion", error_encadenado)
            raise error_encadenado from err_inesperado
        else:
            # Bloque else: solo se ejecuta si NO hubo ninguna excepcion en el try
            self._estado = self.ESTADO_CONFIRMADA
            self.servicio.disponible = False  # Bloquea el recurso para evitar doble reserva
            self.logger.registrar_evento(
                "INFO",
                "Reservas",
                f"Reserva {self.id_entidad} CONFIRMADA para {self.cliente.nombre}. Total: ${self._costo_total:,.2f}"
            )
        finally:
            # Bloque finally: auditoria de cierre de transaccion siempre ejecutada
            self.logger.registrar_evento(
                "INFO",
                "Reservas",
                f"Auditoria de intento de confirmacion finalizada para {self.id_entidad} (Estado: {self._estado})."
            )

    def cancelar(self, motivo: str = "Solicitud del cliente"):
        """Cancela una reserva activa y libera nuevamente la disponibilidad del servicio."""
        try:
            if self._estado == self.ESTADO_CANCELADA:
                raise OperacionNoPermitidaError(f"La reserva {self.id_entidad} ya se encuentra CANCELADA.")
            if self._estado == self.ESTADO_PROCESADA:
                raise OperacionNoPermitidaError(f"No se puede cancelar la reserva {self.id_entidad} porque ya fue PROCESADA.")

            # Si estaba confirmada, libera el recurso ocupado
            if self._estado == self.ESTADO_CONFIRMADA:
                self.servicio.disponible = True

            self._estado = self.ESTADO_CANCELADA
            self.logger.registrar_evento(
                "WARNING",
                "Reservas",
                f"Reserva {self.id_entidad} CANCELADA. Motivo: {motivo}. Servicio liberado."
            )
        except OperacionNoPermitidaError as err:
            self.logger.registrar_evento("ERROR", "Reservas", f"Cancelacion rechazada en {self.id_entidad}", err)
            raise

    def procesar(self):
        """Finaliza la ejecucion del servicio reservado y lo deja disponible para futuros clientes."""
        try:
            if self._estado != self.ESTADO_CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de {self.id_entidad}: {self._estado}."
                )
        except OperacionNoPermitidaError as err:
            self.logger.registrar_evento("ERROR", "Reservas", f"Procesamiento fallido en {self.id_entidad}", err)
            raise
        else:
            self._estado = self.ESTADO_PROCESADA
            self.servicio.disponible = True  # El servicio vuelve a estar libre tras culminar
            self.logger.registrar_evento(
                "INFO",
                "Reservas",
                f"Reserva {self.id_entidad} PROCESADA y cerrada con exito. Facturado: ${self._costo_total:,.2f}"
            )

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
            f"Horas: {self.duracion_horas} | Total: ${self.costo_total:,.2f}"
        )
