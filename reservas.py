# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: reservas.py
# Descripcion: Gestion de reservas con control de estados y manejo de errores.
# ==============================================================================

from modelos_base import EntidadBase, Cliente  # Entidad raiz y modelo Cliente
from servicios import Servicio  # Clase abstracta base de servicios
from excepciones_y_logs import (  # Excepciones y gestor de logs del sistema
    DatoInvalidoError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    GestorLogs,
)


class Reserva(EntidadBase):
    """Representa una reserva de un servicio para un cliente con control de estados."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        horas: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        gestor_logs: GestorLogs | None = None,
    ):
        # Inicializa ID y fecha de registro en EntidadBase
        super().__init__(id_reserva)
        # Inicializa el gestor de auditoria en archivo .log
        self._logger = gestor_logs if gestor_logs is not None else GestorLogs()
        # Asigna y valida las relaciones y parametros de la reserva
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.impuesto = impuesto
        self.descuento = descuento
        # Toda reserva inicia en estado PENDIENTE
        self._estado = "PENDIENTE"
        # Calcula el total inicial aplicando manejo de excepciones
        self._total = self._calcular_total_seguro()
        # Valida la consistencia general de la reserva
        self.validar()
        # Registra la creacion en el archivo de logs
        self._logger.registrar_evento(
            "INFO",
            "reservas.py",
            f"Reserva '{self.id_entidad}' creada en estado {self.estado} para '{self.cliente.nombre}'.",
        )

    @property
    def cliente(self) -> Cliente:
        """Retorna el cliente asociado."""
        return self.__cliente

    @cliente.setter
    def cliente(self, valor: Cliente):
        # Verifica que sea una instancia valida de Cliente
        if not isinstance(valor, Cliente):
            raise DatoInvalidoError("Debe asignar una instancia valida de Cliente.")
        self.__cliente = valor

    @property
    def servicio(self) -> Servicio:
        """Retorna el servicio reservado."""
        return self.__servicio

    @servicio.setter
    def servicio(self, valor: Servicio):
        # Verifica que sea una instancia valida de Servicio
        if not isinstance(valor, Servicio):
            raise DatoInvalidoError("Debe asignar una instancia valida de Servicio.")
        self.__servicio = valor

    @property
    def horas(self) -> int:
        """Retorna la cantidad de horas reservadas."""
        return self.__horas

    @horas.setter
    def horas(self, valor: int):
        # Convierte a entero y encadena la excepcion si el valor no es valido
        try:
            horas_int = int(valor)
        except (TypeError, ValueError) as exc:
            raise ReservaInvalidaError(f"Cantidad de horas invalida: '{valor}'.") from exc
        if horas_int <= 0:
            raise ReservaInvalidaError("Las horas de la reserva deben ser mayores a cero.")
        self.__horas = horas_int

    @property
    def impuesto(self) -> float:
        """Retorna el porcentaje de impuesto aplicado."""
        return self.__impuesto

    @impuesto.setter
    def impuesto(self, valor: float):
        # Valida que el impuesto sea numerico y no negativo
        try:
            imp = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"Impuesto invalido: '{valor}'.") from exc
        if imp < 0 or imp > 1:
            raise DatoInvalidoError("El impuesto debe estar entre 0.0 y 1.0 (ejemplo: 0.19).")
        self.__impuesto = imp

    @property
    def descuento(self) -> float:
        """Retorna el porcentaje de descuento aplicado."""
        return self.__descuento

    @descuento.setter
    def descuento(self, valor: float):
        # Valida que el descuento este en un rango valido
        try:
            desc = float(valor)
        except (TypeError, ValueError) as exc:
            raise DatoInvalidoError(f"Descuento invalido: '{valor}'.") from exc
        if desc < 0 or desc >= 1:
            raise DatoInvalidoError("El descuento debe estar entre 0.0 y menor a 1.0.")
        self.__descuento = desc

    @property
    def estado(self) -> str:
        """Retorna el estado actual de la reserva."""
        return self._estado

    @property
    def total(self) -> float:
        """Retorna el valor total calculado de la reserva."""
        return self._total

    def _calcular_total_seguro(self) -> float:
        """Calcula el costo usando try/except/else/finally y encadenando errores."""
        try:
            # Invoca el metodo polimorfico calcular_costo del servicio
            total_calc = self.servicio.calcular_costo(
                self.horas,
                impuesto=self.impuesto,
                descuento=self.descuento,
            )
        except Exception as exc:
            # Registra el error en el log y encadena la excepcion original
            self._logger.registrar_evento(
                "ERROR",
                "reservas.py",
                f"Fallo al calcular el total de la reserva '{self.id_entidad}'.",
                detalle_error=exc,
            )
            raise ReservaInvalidaError(
                f"No fue posible calcular el costo de la reserva '{self.id_entidad}'."
            ) from exc
        else:
            # Se ejecuta solo cuando el calculo es exitoso
            self._logger.registrar_evento(
                "INFO",
                "reservas.py",
                f"Total calculado para reserva '{self.id_entidad}': ${total_calc:,.2f}.",
            )
            return total_calc
        finally:
            # Mantiene el flujo controlado al cerrar el bloque de calculo
            pass

    def confirmar(self) -> None:
        """Confirma una reserva PENDIENTE si el servicio esta disponible."""
        # Solo permite confirmar desde PENDIENTE
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id_entidad}' en estado '{self._estado}'."
            )
        # Verifica que el servicio siga disponible
        if not self.servicio.disponible:
            raise ReservaInvalidaError(
                f"El servicio '{self.servicio.nombre_servicio}' no esta disponible para confirmar."
            )
        # Recalcula el total y marca el servicio como ocupado
        self._total = self._calcular_total_seguro()
        self.servicio.disponible = False
        self._estado = "CONFIRMADA"
        self._logger.registrar_evento(
            "INFO",
            "reservas.py",
            f"Reserva '{self.id_entidad}' CONFIRMADA por ${self._total:,.2f}.",
        )

    def cancelar(self, motivo: str = "Cancelada por el usuario") -> None:
        """Cancela una reserva si no esta completada y libera el servicio si estaba confirmada."""
        # Impide cancelar reservas ya completadas
        if self._estado == "COMPLETADA":
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva '{self.id_entidad}' porque ya fue completada."
            )
        # Impide cancelar una reserva ya cancelada
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self.id_entidad}' ya se encuentra cancelada."
            )
        # Si estaba confirmada, libera la disponibilidad del servicio
        if self._estado == "CONFIRMADA":
            self.servicio.disponible = True
        self._estado = "CANCELADA"
        self._logger.registrar_evento(
            "WARNING",
            "reservas.py",
            f"Reserva '{self.id_entidad}' CANCELADA. Motivo: {motivo.strip() or 'Sin motivo'}.",
        )

    def completar(self) -> None:
        """Marca una reserva CONFIRMADA como COMPLETADA."""
        # Exige estado CONFIRMADA previo
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se pueden completar reservas CONFIRMADA. Estado actual: '{self._estado}'."
            )
        self._estado = "COMPLETADA"
        self.servicio.disponible = True
        self._logger.registrar_evento(
            "INFO",
            "reservas.py",
            f"Reserva '{self.id_entidad}' COMPLETADA.",
        )

    def validar(self) -> bool:
        """Valida integridad de cliente, servicio, horas y estado."""
        if not self.__cliente or not self.__servicio:
            raise ParametroFaltanteError("La reserva debe contar con cliente y servicio.")
        if self._estado not in self.ESTADOS_VALIDOS:
            raise ReservaInvalidaError(f"Estado no valido: '{self._estado}'.")
        return True

    def obtener_resumen(self) -> str:
        """Retorna un resumen legible de la reserva."""
        return (
            f"Reserva [{self.id_entidad}] | Estado: {self.estado} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
            f"Horas: {self.horas} | Total: ${self.total:,.2f}"
        )