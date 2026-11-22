#------------------------------------------------------------------------------
# Fase 4 - Componente Práctico (Prácticas Simuladas) 
#    Universidad Nacional Abierta y a Distancia
#             Curso: Programación
# Sistema Integral de Gestión de Clientes, Servicios y Reservas 'Software FJ'
#        Alberto Eduardo Avila Hernandez 
#------------------------------------------------------------------------------

import abc
import logging
import re
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURACIÓN DEL SISTEMA DE LOGS
# ==========================================
log_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')

log_dir = Path(__file__).resolve().parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "software_fj.log"

file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger("SoftwareFJLogger")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorSoftwareFJ(Exception):
    """Clase base para excepciones en el sistema Software FJ."""
    pass

class ClienteInvalidoError(ErrorSoftwareFJ):
    """Excepción lanzada cuando los datos del cliente son inválidos."""
    pass

class ServicioInvalidoError(ErrorSoftwareFJ):
    """Excepción lanzada cuando los parámetros de un servicio no cumplen las reglas de negocio."""
    pass

class ReservaInvalidaError(ErrorSoftwareFJ):
    """Excepción lanzada cuando una operación sobre una reserva es errónea."""
    pass

class CapacidadExcedidaError(ServicioInvalidoError):
    """Excepción lanzada cuando la capacidad o disponibilidad del servicio es superada."""
    pass

# ==========================================
# ENTIDAD ABSTRACTA BASE Y CLASE CLIENTE
# ==========================================
class EntidadBase(abc.ABC):
    """Clase abstracta base para entidades del sistema."""
    
    def __init__(self, id_entidad: str):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @abc.abstractmethod
    def obtener_resumen(self) -> str:
        pass


class Cliente(EntidadBase):
    """Clase que representa un cliente con encapsulación y validaciones estrictas."""
    
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ClienteInvalidoError(f"El nombre del cliente '{valor}' es inválido (mínimo 2 caracteres).")
        self._nombre = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not valor or not re.match(patron, valor):
            raise ClienteInvalidoError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self._email = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.isdigit() or len(valor) < 7:
            raise ClienteInvalidoError(f"El teléfono '{valor}' es inválido (debe contener solo dígitos y al menos 7 números).")
        self._telefono = valor.strip()

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id_entidad}]: {self.nombre} | Email: {self.email} | Tel: {self.telefono}"


# ==========================================
# CLASE ABSTRACTA SERVICIO Y DERIVADAS
# ==========================================
class Servicio(EntidadBase):
    """Clase abstracta que define la interfaz general para servicios en Software FJ."""

    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float):
        super().__init__(id_servicio)
        if tarifa_base <= 0:
            raise ServicioInvalidoError(f"La tarifa base debe ser un valor positivo. Valor ingresado: {tarifa_base}")
        self._nombre_servicio = nombre_servicio
        self._tarifa_base = tarifa_base

    @property
    def nombre_servicio(self) -> str:
        return self._nombre_servicio

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @abc.abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """Método polimórfico para calcular el costo total del servicio."""
        pass

    @abc.abstractmethod
    def describir_servicio(self) -> str:
        """Método polimórfico para describir las características del servicio."""
        pass


class ReservaSalas(Servicio):
    """Servicio especializado en alquiler/reserva de salas de reuniones/eventos."""

    def __init__(self, id_servicio: str, nombre_sala: str, tarifa_por_hora: float, capacidad_maxima: int):
        super().__init__(id_servicio, f"Reserva de Sala: {nombre_sala}", tarifa_por_hora)
        if capacidad_maxima <= 0 or capacidad_maxima > 200:
            raise CapacidadExcedidaError(f"La capacidad de la sala debe estar entre 1 y 200 personas. Valor: {capacidad_maxima}")
        self._capacidad_maxima = capacidad_maxima

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        if duracion_horas <= 0:
            raise ServicioInvalidoError(f"La duración de la reserva debe ser mayor a 0 horas. Ingresado: {duracion_horas}")
        
        costo = self._tarifa_base * duracion_horas
        descuento = kwargs.get('descuento', 0.0)
        iva = kwargs.get('iva', 0.19)
        
        costo_con_descuento = costo * (1 - descuento)
        costo_total = costo_con_descuento * (1 + iva)
        return round(costo_total, 2)

    def describir_servicio(self) -> str:
        return f"Servicio [Salas]: {self.nombre_servicio} | Capacidad Máx: {self._capacidad_maxima} personas | Tarifa/Hora: ${self.tarifa_base:,.2f}"

    def obtener_resumen(self) -> str:
        return self.describir_servicio()


class AlquilerEquipos(Servicio):
    """Servicio especializado en alquiler de equipos tecnológicos."""

    def __init__(self, id_servicio: str, tipo_equipo: str, tarifa_por_hora: float, cantidad_disponible: int):
        super().__init__(id_servicio, f"Alquiler de Equipo: {tipo_equipo}", tarifa_por_hora)
        if cantidad_disponible <= 0:
            raise ServicioInvalidoError(f"La cantidad de equipos disponibles debe ser mayor a 0. Ingresado: {cantidad_disponible}")
        self._cantidad_disponible = cantidad_disponible

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        if duracion_horas <= 0:
            raise ServicioInvalidoError("La duración del alquiler debe ser mayor a 0 horas.")
        
        cantidad = kwargs.get('cantidad_unidades', 1)
        if cantidad > self._cantidad_disponible:
            raise CapacidadExcedidaError(f"No hay suficientes equipos disponibles. Solicitados: {cantidad}, Disponibles: {self._cantidad_disponible}")
        
        costo_base = self._tarifa_base * duracion_horas * cantidad
        seguro = kwargs.get('seguro_equipo', 15000.0)
        descuento = kwargs.get('descuento', 0.0)
        
        costo_total = (costo_base + seguro) * (1 - descuento)
        return round(costo_total, 2)

    def describir_servicio(self) -> str:
        return f"Servicio [Equipos]: {self.nombre_servicio} | Stock Disponible: {self._cantidad_disponible} unid. | Tarifa/Hora: ${self.tarifa_base:,.2f}"

    def obtener_resumen(self) -> str:
        return self.describir_servicio()


class AsesoriaEspecializada(Servicio):
    """Servicio especializado en consultoría y asesoría técnica."""

    def __init__(self, id_servicio: str, area_especialidad: str, tarifa_por_hora: float, nivel_consultor: str):
        super().__init__(id_servicio, f"Asesoría en {area_especialidad}", tarifa_por_hora)
        niveles_validos = ["Junior", "Senior", "Master"]
        if nivel_consultor not in niveles_validos:
            raise ServicioInvalidoError(f"Nivel de consultor no válido. Opciones: {niveles_validos}")
        self._nivel_consultor = nivel_consultor

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        if duracion_horas <= 0:
            raise ServicioInvalidoError("La duración de la asesoría debe ser mayor a 0 horas.")
        
        multiplicadores = {"Junior": 1.0, "Senior": 1.3, "Master": 1.6}
        mult = multiplicadores.get(self._nivel_consultor, 1.0)
        
        costo = self._tarifa_base * duracion_horas * mult
        recargo_urgencia = kwargs.get('urgencia', False)
        if recargo_urgencia:
            costo *= 1.25
        
        descuento = kwargs.get('descuento', 0.0)
        return round(costo * (1 - descuento), 2)

    def describir_servicio(self) -> str:
        return f"Servicio [Asesoría]: {self.nombre_servicio} | Consultor Nivel: {self._nivel_consultor} | Tarifa/Hora: ${self.tarifa_base:,.2f}"

    def obtener_resumen(self) -> str:
        return self.describir_servicio()


# ==========================================
# CLASE RESERVA Y GESTOR DEL SISTEMA
# ==========================================
class Reserva:
    """Clase que integra Cliente, Servicio, Duración y Estado de la transacción."""

    _contador_reserva = 1000

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: float, **kwargs_costo):
        if not cliente or not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere un objeto Cliente válido para efectuar una reserva.")
        if not servicio or not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se requiere un objeto Servicio válido para efectuar una reserva.")
        if duracion_horas <= 0:
            raise ReservaInvalidaError(f"La duración ({duracion_horas} hs) no es válida.")

        Reserva._contador_reserva += 1
        self._id_reserva = f"RES-{Reserva._contador_reserva}"
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = "Pendiente"
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self._costo_total = self._servicio.calcular_costo(self._duracion_horas, **kwargs_costo)
        except Exception as err:
            logger.error(f"Fallo en cálculo de costo para reserva {self._id_reserva}: {err}")
            raise ReservaInvalidaError(f"Error al calcular el costo de la reserva: {err}") from err

    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar_reserva(self):
        try:
            if self._estado == "Confirmada":
                raise ReservaInvalidaError(f"La reserva {self._id_reserva} ya se encuentra confirmada.")
            if self._estado == "Cancelada":
                raise ReservaInvalidaError("No se puede confirmar una reserva que ha sido cancelada previamente.")
            
            self._estado = "Confirmada"
            logger.info(f"Reserva {self._id_reserva} confirmada exitosamente por un total de ${self._costo_total:,.2f}.")
        except Exception as e:
            logger.warning(f"Excepción en confirmación de reserva {self._id_reserva}: {e}")
            raise
        else:
            logger.info(f"Notificación enviada a {self._cliente.email} para la reserva {self._id_reserva}.")
        finally:
            logger.info(f"Finalizado proceso de confirmación para {self._id_reserva} [Estado final: {self._estado}].")

    def cancelar_reserva(self):
        try:
            if self._estado == "Cancelada":
                raise ReservaInvalidaError(f"La reserva {self._id_reserva} ya fue cancelada.")
            self._estado = "Cancelada"
            logger.info(f"Reserva {self._id_reserva} cancelada correctamente.")
        except Exception as e:
            logger.warning(f"Excepción en cancelación de reserva {self._id_reserva}: {e}")
            raise
        finally:
            logger.info(f"Finalizado proceso de cancelación para {self._id_reserva} [Estado final: {self._estado}].")

    def obtener_detalle(self) -> str:
        return (f"Reserva [{self._id_reserva}] ({self._fecha_creacion})\n"
                f"  - Cliente: {self._cliente.nombre} ({self._cliente.email})\n"
                f"  - Servicio: {self._servicio.nombre_servicio}\n"
                f"  - Duración: {self._duracion_horas} horas | Costo Total: ${self._costo_total:,.2f}\n"
                f"  - Estado Actual: {self._estado}")


class SistemaSoftwareFJ:
    """Clase gestora principal que administra colecciones de objetos sin base de datos."""

    def __init__(self):
        self._clientes = {}
        self._servicios = {}
        self._reservas = {}

    def registrar_cliente(self, id_cliente: str, nombre: str, email: str, telefono: str) -> Cliente:
        logger.info(f"Intentando registrar cliente: {nombre} ({id_cliente})...")
        try:
            if id_cliente in self._clientes:
                raise ClienteInvalidoError(f"El cliente con ID '{id_cliente}' ya está registrado.")
            cliente = Cliente(id_cliente, nombre, email, telefono)
            self._clientes[id_cliente] = cliente
            logger.info(f"Cliente registrado con éxito: {cliente.obtener_resumen()}")
            return cliente
        except ErrorSoftwareFJ as e:
            logger.error(f"[ERROR DE NEGOCIO] Fallo al registrar cliente '{id_cliente}': {e}")
            raise
        except Exception as e:
            logger.critical(f"[ERROR INESPERADO] Error del sistema al registrar cliente: {e}")
            raise ErrorSoftwareFJ("Error interno en el sistema de clientes.") from e

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        logger.info(f"Intentando registrar servicio: {servicio.nombre_servicio} ({servicio.id_entidad})...")
        try:
            if servicio.id_entidad in self._servicios:
                raise ServicioInvalidoError(f"El servicio con ID '{servicio.id_entidad}' ya existe.")
            self._servicios[servicio.id_entidad] = servicio
            logger.info(f"Servicio registrado con éxito: {servicio.describir_servicio()}")
            return servicio
        except ErrorSoftwareFJ as e:
            logger.error(f"[ERROR DE NEGOCIO] Fallo al registrar servicio: {e}")
            raise

    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion_horas: float, **kwargs) -> Reserva:
        logger.info(f"Iniciando solicitud de reserva para Cliente '{id_cliente}' y Servicio '{id_servicio}'...")
        try:
            cliente = self._clientes.get(id_cliente)
            if not cliente:
                raise ReservaInvalidaError(f"El cliente con ID '{id_cliente}' no existe en el sistema.")
            
            servicio = self._servicios.get(id_servicio)
            if not servicio:
                raise ReservaInvalidaError(f"El servicio con ID '{id_servicio}' no está disponible.")

            reserva = Reserva(cliente, servicio, duracion_horas, **kwargs)
            self._reservas[reserva.id_reserva] = reserva
            logger.info(f"Reserva creada exitosamente: {reserva.id_reserva} por ${reserva.costo_total:,.2f}")
            return reserva
        except ErrorSoftwareFJ as e:
            logger.error(f"[ERROR DE TRANSACCIÓN] No se pudo crear la reserva: {e}")
            raise


# ==========================================
# HARNESS DE SIMULACIÓN (10+ OPERACIONES)
# ==========================================
def ejecutar_simulacion_10_operaciones():
    print("\n" + "=" * 70)
    print("      INICIO DE SIMULACIÓN DE OPERACIONES - SOFTWARE FJ")
    print("=" * 70 + "\n")

    sistema = SistemaSoftwareFJ()

    print("--- 1. REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS) ---")
    try:
        sistema.registrar_cliente("CLI-001", "Eduardo Ávila", "eduardo.avila@unad.edu.co", "3101234567")
    except Exception as e:
        print(f"Capta: {e}")

    try:
        sistema.registrar_cliente("CLI-002", "María Pérez", "correo_invalido_sin_arroba", "3009876543")
    except Exception as e:
        print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    try:
        sistema.registrar_cliente("CLI-003", "Carlos Gómez", "carlos@gmail.com", "ABC12345")
    except Exception as e:
        print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    try:
        sistema.registrar_cliente("CLI-004", "Ana Sofía Martínez", "ana.martinez@empresa.com", "3158889900")
    except Exception as e:
        print(f"Capta: {e}")

    print("\n--- 2. CREACIÓN DE SERVICIOS (POLIMORFISMO Y VALIDACIONES) ---")
    try:
        sistema.registrar_servicio(
            ReservaSalas("SRV-SAL-01", "Auditorio Principal FJ", tarifa_por_hora=150000.0, capacidad_maxima=100)
        )
    except Exception as e:
        print(f"Capta: {e}")

    try:
        s_bad = AlquilerEquipos("SRV-EQ-01", "Laptops I7 High-End", tarifa_por_hora=25000.0, cantidad_disponible=0)
        sistema.registrar_servicio(s_bad)
    except Exception as e:
        print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    try:
        sistema.registrar_servicio(
            AlquilerEquipos("SRV-EQ-02", "Videoproyectores 4K", tarifa_por_hora=35000.0, cantidad_disponible=5)
        )
    except Exception as e:
        print(f"Capta: {e}")

    try:
        sistema.registrar_servicio(
            AsesoriaEspecializada("SRV-ASE-01", "Arquitectura de Software POO", tarifa_por_hora=200000.0, nivel_consultor="Master")
        )
    except Exception as e:
        print(f"Capta: {e}")

    print("\n--- 3. CREACIÓN Y PROCESAMIENTO DE RESERVAS (SOBRECARGA Y EXCEPCIONES) ---")
    r1 = None
    try:
        r1 = sistema.crear_reserva("CLI-001", "SRV-SAL-01", duracion_horas=4.0, descuento=0.10, iva=0.19)
        r1.confirmar_reserva()
    except Exception as e:
        print(f"Capta: {e}")

    try:
        r2 = sistema.crear_reserva("CLI-004", "SRV-ASE-01", duracion_horas=3.0, urgencia=True, descuento=0.05)
        r2.confirmar_reserva()
    except Exception as e:
        print(f"Capta: {e}")

    try:
        sistema.crear_reserva("CLI-999", "SRV-SAL-01", duracion_horas=2.0)
    except Exception as e:
        print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    try:
        sistema.crear_reserva("CLI-001", "SRV-EQ-02", duracion_horas=2.0, cantidad_unidades=10)
    except Exception as e:
        print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    if r1:
        try:
            r1.cancelar_reserva()
        except Exception as e:
            print(f"Capta: {e}")

        try:
            r1.cancelar_reserva()
        except Exception as e:
            print(f"-> EXCEPCIÓN CONTROLADA CAPTURADA: {e}")

    print("\n" + "=" * 70)
    print("      SIMULACIÓN FINALIZADA CON ÉXITO Y SISTEMA ESTABLE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    ejecutar_simulacion_10_operaciones()
