# ==============================================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Programacion (213023) - Fase 4: Componente Practico
# Modulo: modelos_base.py
# Descripcion: Clase abstracta general del sistema y clase Cliente encapsulada.
# ==============================================================================

from abc import ABC, abstractmethod
from datetime import datetime
from excepciones_y_logs import DatoInvalidoError, ParametroFaltanteError


class EntidadBase(ABC):
    """Clase abstracta raiz que representa cualquier entidad gestionada en Software FJ."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not str(id_entidad).strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio y no puede estar vacio.")
        self._id_entidad = str(id_entidad).strip()
        self._fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @property
    def fecha_registro(self) -> str:
        return self._fecha_registro

    @abstractmethod
    def validar(self) -> bool:
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        pass


class Cliente(EntidadBase):
    """Representa un cliente de Software FJ con encapsulacion y validaciones estrictas."""

    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self.validar()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3 or valor.strip().isdigit():
            raise DatoInvalidoError(f"Nombre de cliente invalido: '{valor}'. Debe tener al menos 3 letras.")
        self.__nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str):
        doc_limpio = str(valor).strip() if valor is not None else ""
        if not doc_limpio.isdigit() or not (6 <= len(doc_limpio) <= 15):
            raise DatoInvalidoError(f"Documento invalido: '{valor}'. Debe ser numerico (6 a 15 digitos).")
        self.__documento = doc_limpio

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        correo_limpio = str(valor).strip() if valor is not None else ""
        if "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
            raise DatoInvalidoError(f"Correo electronico invalido: '{valor}'.")
        self.__correo = correo_limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        tel_limpio = str(valor).strip() if valor is not None else ""
        if not tel_limpio.isdigit() or not (7 <= len(tel_limpio) <= 12):
            raise DatoInvalidoError(f"Telefono invalido: '{valor}'. Debe contener entre 7 y 12 digitos.")
        self.__telefono = tel_limpio

    def validar(self) -> bool:
        if not all([self.__nombre, self.__documento, self.__correo, self.__telefono]):
            raise ParametroFaltanteError("Faltan datos obligatorios en el perfil del cliente.")
        return True

    def obtener_resumen(self) -> str:
        return (
            f"Cliente [{self.id_entidad}] | Nombre: {self.nombre} | "
            f"Doc: {self.documento} | Email: {self.correo} | Tel: {self.telefono}"
        )