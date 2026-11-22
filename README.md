####### UNAD - Programación Aplicada (Curso 213023) #########
####### Fase 4 - Componente Práctico: Manejo de Errores y Excepciones en Python (Software FJ)
####### Estudiante:Alberto Eduardo Ávila Hernández  
####### Grupo:213023_503  
####### Universidad Nacional Abierta y a Distancia (UNAD) ##################
####### Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTIS)#######  

---

####  Descripción del Proyecto #####
Solución orientada a objetos desarrollada en Python para la empresa **Software FJ** (Anexo 3, Fase 4). 
Implementa la gestión de clientes, servicios y reservas sin uso de bases de datos externas, aplicando 
**manejo defensivo de errores y auditoría de logs**.

---

### Conceptos POO e Integrados #########

1. **Abstracción y Encapsulamiento:**
   - Clase abstracta base `EntidadBase` y setters con validación estricta usando expresiones regulares (`re`) para correos y teléfonos.
2. **Polimorfismo y Sobrecarga Simulada:**
   - Clase abstracta `Servicio` con subclases concretas: `ReservaSalas`, `AlquilerEquipos` y `AsesoriaEspecializada`.
   - Modificación dinámica de tarifas y condiciones utilizando parámetros flexibles (`**kwargs`).
3. **Manejo Robusto de Excepciones:**
   - Jerarquía de excepciones personalizadas (`ErrorSoftwareFJ`, `ClienteInvalidoError`, `ServicioInvalidoError`, `ReservaInvalidaError`, `CapacidadExcedidaError`).
   - Uso de bloques `try / except / else / finally` y encadenamiento de excepciones (`raise ... from`).
4. **Trazabilidad y Auditoría (Logs):**
   - Configuración del módulo `logging` para registrar eventos del sistema tanto en consola como en el archivo `software_fj.log`.

---

## Estructura del Repositorio

- `software_fj.py`: Código fuente ejecutable con el modelo de clases, excepciones y el harness de 14 pruebas simuladas.
- `software_fj.log`: Archivo generado automáticamente con la auditoría y trazabilidad de operaciones.
- `README.md`: Documentación del proyecto.

## Instrucciones de Instalación y Ejecución

### Requisitos Previos
- Tener instalado **Python 3.8** o superior.

### Pasos para Ejecutar

1. Clonar o descargar este repositorio:
   git clone [suspicious link removed]

2. Navegar a la carpeta del proyecto:
   cd Fase4-SoftwareFJ-UNAD

3. Ejecutar el script principal:
   python software_fj.py

---

## Resumen de Pruebas Simuladas (Salida del Sistema)
El sistema ejecuta automáticamente 14 operaciones consecutivas que demuestran:
- Registro correcto de clientes y captura de correos/teléfonos inválidos.
- Registro de servicios con validación de capacidad y tarifas.
- Transacciones de reservas con cálculo de IVA, descuentos, seguro de equipos y recargos por urgencia.
- Manejo controlado de intentos de sobre-reserva, clientes inexistentes y doble cancelación.
