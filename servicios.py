# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: servicios.py
# Descripcion: Clase abstracta Servicio y 3 servicios especializados con polimorfismo.
# ==============================================================================

from abc import abstractmethod
from modelos_base import EntidadBase
from excepciones_y_logs import DatoInvalidoError, ParametroFaltanteError


class Servicio(EntidadBase):
    """Clase abstracta que define el contrato base para los servicios de Software FJ."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float):
        # Inicializa ID y fecha desde EntidadBase
        super().__init__(id_servicio)
        # Valida nombre del servicio
        if not nombre_servicio or not nombre_servicio.strip():
            raise ParametroFaltanteError("El nombre del servicio no puede estar vacio.")
        self._nombre_servicio = nombre_servicio.strip()
        # Asigna tarifa base validando que sea positiva
        self.tarifa_hora = tarifa_hora
        # Estado booleano de disponibilidad operativa
        self._disponible = True

    @property
    def nombre_servicio(self) -> str:
        return self._nombre_servicio

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @tarifa_hora.setter
    def tarifa_hora(self, valor: float):
        # Intenta convertir a flotante y encadena excepcion si ocurre ValueError/TypeError
        try:
            tarifa = float(valor)
        except (ValueError, TypeError) as err:
            raise DatoInvalidoError(f"La tarifa '{valor}' no es un numero valido.") from err

        if tarifa <= 0:
            raise DatoInvalidoError(f"La tarifa por hora debe ser mayor a cero. Recibido: {tarifa}")
        self._tarifa_hora = tarifa

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self) -> bool:
        """Valida los atributos especificos de cada tipo de servicio."""
        pass

    @abstractmethod
    def calcular_costo(self, horas: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """
        Metodo polimorfico y sobrecargado mediante parametros opcionales para calcular
        tarifa base, recargos propios, descuentos e impuestos.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Retorna la descripcion detallada y especializada del servicio."""
        pass

    def validar(self) -> bool:
        """Implementa la validacion general heredada de EntidadBase."""
        return self.validar_parametros()

    def obtener_resumen(self) -> str:
        """Implementa el resumen general heredado de EntidadBase."""
        estado_txt = "DISPONIBLE" if self.disponible else "OCUPADO"
        return f"[{self.id_entidad}] {self.describir_servicio()} | Estado: {estado_txt}"


class ReservaSala(Servicio):
    """Servicio especializado 1: Reserva de salas tecnologicas y de conferencias."""

    def __init__(self, id_servicio: str, nombre_sala: str, tarifa_hora: float, capacidad: int, tiene_proyector: bool = True):
        # Guarda atributos especificos antes de llamar a super() si es necesario validar
        self.capacidad = capacidad
        self.tiene_proyector = bool(tiene_proyector)
        super().__init__(id_servicio, nombre_sala, tarifa_hora)
        self.validar_parametros()

    def validar_parametros(self) -> bool:
        # Verifica que la capacidad de personas sea un entero positivo razonable
        if not isinstance(self.capacidad, int) or self.capacidad < 2 or self.capacidad > 200:
            raise DatoInvalidoError(f"Capacidad de sala invalida ({self.capacidad}). Debe estar entre 2 y 200 personas.")
        return True

    def calcular_costo(self, horas: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """Calcula el costo de la sala sumando recargo fijo por proyector 4K si aplica."""
        if horas <= 0:
            raise DatoInvalidoError("Las horas de reserva de sala deben ser mayores a 0.")
        # Recargo de $15.000 COP si incluye equipo de proyeccion multimedia
        recargo_proyector = 15000.0 if self.tiene_proyector else 0.0
        subtotal = (self.tarifa_hora * horas) + recargo_proyector
        subtotal_con_desc = subtotal * (1 - descuento)
        total = subtotal_con_desc * (1 + impuesto)
        return round(total, 2)

    def describir_servicio(self) -> str:
        proy_txt = "Con Proyector 4K" if self.tiene_proyector else "Sin Proyector"
        return f"Sala '{self.nombre_servicio}' (Cap: {self.capacidad} pers, {proy_txt}) - ${self.tarifa_hora:,.0f}/h"


class AlquilerEquipo(Servicio):
    """Servicio especializado 2: Alquiler de estaciones de trabajo y servidores."""

    def __init__(self, id_servicio: str, nombre_equipo: str, tarifa_hora: float, gama: str, incluye_seguro: bool = True):
        self.gama = gama
        self.incluye_seguro = bool(incluye_seguro)
        super().__init__(id_servicio, nombre_equipo, tarifa_hora)
        self.validar_parametros()

    def validar_parametros(self) -> bool:
        # Solo admite gamas corporativas homologadas
        gamas_validas = ("MEDIA", "ALTA", "WORKSTATION")
        if not self.gama or self.gama.strip().upper() not in gamas_validas:
            raise DatoInvalidoError(f"Gama de equipo invalida: '{self.gama}'. Opciones: {gamas_validas}")
        self.gama = self.gama.strip().upper()
        return True

    def calcular_costo(self, horas: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """Calcula el costo del alquiler aplicando poliza de seguro del 10% si esta activa."""
        if horas <= 0:
            raise DatoInvalidoError("Las horas de alquiler de equipo deben ser mayores a 0.")
        base = self.tarifa_hora * horas
        # Poliza contra danos accidentales equivale al 10% del valor base
        costo_seguro = base * 0.10 if self.incluye_seguro else 0.0
        subtotal_con_desc = (base + costo_seguro) * (1 - descuento)
        total = subtotal_con_desc * (1 + impuesto)
        return round(total, 2)

    def describir_servicio(self) -> str:
        seg_txt = "Con Seguro" if self.incluye_seguro else "Sin Seguro"
        return f"Equipo '{self.nombre_servicio}' [Gama {self.gama}, {seg_txt}] - ${self.tarifa_hora:,.0f}/h"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado 3: Consultoria en ingenieria, arquitectura y ciberseguridad."""

    def __init__(self, id_servicio: str, tema_asesoria: str, tarifa_hora: float, especialidad: str, es_urgente: bool = False):
        self.especialidad = especialidad
        self.es_urgente = bool(es_urgente)
        super().__init__(id_servicio, tema_asesoria, tarifa_hora)
        self.validar_parametros()

    def validar_parametros(self) -> bool:
        # Valida que el campo de especialidad tecnica este especificado
        if not self.especialidad or len(self.especialidad.strip()) < 4:
            raise ParametroFaltanteError("Debe especificar una especialidad tecnica valida (minimo 4 caracteres).")
        self.especialidad = self.especialidad.strip()
        return True

    def calcular_costo(self, horas: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """Calcula el costo de consultoria aplicando factor de prioridad (1.25x) si es urgente."""
        if horas <= 0:
            raise DatoInvalidoError("Las horas de asesoria deben ser mayores a 0.")
        factor_urgencia = 1.25 if self.es_urgente else 1.0
        subtotal = (self.tarifa_hora * horas) * factor_urgencia
        subtotal_con_desc = subtotal * (1 - descuento)
        total = subtotal_con_desc * (1 + impuesto)
        return round(total, 2)

    def describir_servicio(self) -> str:
        urg_txt = "PRIORIDAD URGENTE" if self.es_urgente else "Estandar"
        return f"Asesoria '{self.nombre_servicio}' ({self.especialidad} - {urg_txt}) - ${self.tarifa_hora:,.0f}/h"
