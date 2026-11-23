# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

**Universidad Nacional Abierta y a Distancia – UNAD**  
**Programa:** Ingeniería de Sistemas  
**Curso:** Programación (Código: 213023)  
**Actividad:** Fase 4 – Componente práctico (Prácticas simuladas)  
**Grupo:** 213023A_2204  
**Tutor:** Jaider José Lineros Fragoso  

---

## Descripción del Proyecto

Aplicación desarrollada en **Python 3** bajo el paradigma de **Programación Orientada a Objetos (POO)** sin el uso de bases de datos (gestión en memoria mediante objetos y listas), orientada a la administración de clientes, servicios tecnológicos y reservas para la empresa **Software FJ**.

El sistema implementa:
- Clases abstractas (`EntidadBase` y `Servicio`), herencia, encapsulación estricta (`@property`) y polimorfismo.
- Jerarquía de excepciones personalizadas (`SoftwareFJError`, `DatoInvalidoError`, `ParametroFaltanteError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`).
- Manejo avanzado de errores mediante bloques `try / except`, `try / except / else`, `try / except / finally` y encadenamiento de excepciones (`raise ... from`).
- Registro persistente de eventos y errores en el archivo plano `sistema_fj.log`.

---

## Estructura Modular del Repositorio

| Archivo | Descripción | Responsable |
| :--- | :--- | :--- |
| `excepciones_y_logs.py` | Jerarquía de excepciones personalizadas y gestor de auditoría en archivo `.log`. | John Eyder Cano Chavez (`jecanounad`) |
| `modelos_base.py` | Clase abstracta `EntidadBase` y clase `Cliente` con encapsulación y validaciones. | John Eyder Cano Chavez (`jecanounad`) |
| `servicios.py` | Clase abstracta `Servicio` y servicios especializados (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`). | Juan Esteban Saavedra Guevara |
| `reservas.py` | Clase `Reserva` con gestión de estados, confirmación, cancelación y procesamiento. | Juan Esteban Saavedra Guevara |
| `main.py` | Controlador principal en memoria y ejecución secuencial de 12 operaciones de prueba. | Juan Esteban Saavedra Guevara |

---

## Ejecución del Proyecto

1. Clonar o descargar el repositorio en un entorno con **Python 3.10 o superior**.
2. Abrir una terminal en la carpeta raíz del proyecto.
3. Ejecutar el archivo principal:
   ```bash
   python main.py
