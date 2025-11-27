# HMI Nextion - Interfaces de Usuario

## Descripción General
Este repositorio contiene las interfaces gráficas de usuario diseñadas para el sistema HMI (Human Machine Interface) implementado con pantallas Nextion. Las interfaces fueron desarrolladas específicamente para la aplicación y optimizadas para el hardware de visualización utilizado.

## Especificaciones Técnicas

### Herramientas de Desarrollo
- **Diseño de Interfaces**: Canvas (creación propia)
- **Recursos Gráficos**: Flavicon (apoyo en iconografía)
- **Plataforma Destino**: Pantallas Nextion
- **Total de Assets**: 13 interfaces/imágenes

### Características de las Interfaces
- Diseño original y personalizado
- Optimizadas para pantallas Nextion
- Integración de iconografía profesional
- Interfaz intuitiva y funcional
- Compatibilidad con el hardware específico

## Documentación de Interfaces

### Interfaz 1: Pantalla Principal de Control

#### Descripción General
La interfaz principal funciona como centro de control del sistema, permitiendo la gestión del estado de energía y navegación entre los diferentes módulos operativos.

#### Estados de la Interfaz

**Estado 1: Sistema Apagado**
- **Archivo**: `1.png`
- **Descripción**: Estado inicial al energizar la pantalla
- **Elementos Visuales**:
  - Logo institucional "UNIVERSIDAD ECC CT"
  - Botón "Off" activo en color rojo
  - Icono de menú principal en color rojo
  - Botón "On" en estado inactivo
- **Comportamiento**:
  - Sistema en estado de reposo
  - Solo disponible la opción de encendido

![Estado 1 - Sistema Apagado](interfaces/1.png)

**Estado 2: Sistema Encendido - Menú Principal**
- **Archivo**: `2.png`
- **Descripción**: Estado activo del sistema con menú de navegación desplegado
- **Elementos Visuales**:
  - Botón "On" activo en color verde
  - Icono de menú principal en color verde
  - Botón "Off" desactivado
  - Menú de opciones disponible:
    - CALIBRACION HOME
    - AUTOMATICO
    - DIAGNOSTICO
    - OPERACION MANUAL
    - ALERTA
- **Comportamiento**:
  - Sistema operativo y listo para recibir comandos
  - Navegación habilitada entre los 5 módulos

![Estado 2 - Sistema Encendido](interfaces/2.png)

**Estado 3: Navegación Activa con Indicador STOP**
- **Archivo**: `3.png`
- **Descripción**: Estado de navegación con botón seleccionado y sistema en STOP
- **Elementos Visuales**:
  - Botón de navegación seleccionado en color amarillo
  - Indicador "STOP" visible en la esquina superior derecha
  - Resto de botones en estado normal
  - Botón "On" mantiene estado activo verde
- **Comportamiento**:
  - Visualización del módulo actualmente seleccionado
  - Indicación clara del estado de seguridad "STOP"
  - Navegación entre módulos manteniendo el estado del sistema

![Estado 3 - Navegación Activa](interfaces/3.png)

#### Funcionalidades Principales
1. **Control de Energía**: Encendido/Apagado del sistema
2. **Navegación Modular**: Acceso a los 5 módulos operativos
3. **Indicación de Estado**: Feedback visual inmediato del estado del sistema
4. **Seguridad**: Indicador visible de condición "STOP"

#### Flujo de Navegación
1. **Inicio** → Estado 1 (Sistema Apagado)
2. **Encendido** → Estado 2 (Menú Principal)
3. **Selección de Módulo** → Estado 3 (Navegación Activa)
4. **Condición STOP** → Estado 3 con indicador activo

---

### Interfaz 2: Calibración Home
*(Descripción pendiente)*
![Interfaz 2](interfaces/4.png)

### Interfaz 3: Modo Automático
*(Descripción pendiente)*
![Interfaz 3](interfaces/5.png)

### Interfaz 4: Diagnóstico del Sistema
*(Descripción pendiente)*
![Interfaz 4](interfaces/6.png)

### Interfaz 5: Operación Manual
*(Descripción pendiente)*
![Interfaz 5](interfaces/7.png)

### Interfaz 6: Panel de Alertas
*(Descripción pendiente)*
![Interfaz 6](interfaces/8.png)

### Interfaz 7: Configuración Avanzada
*(Descripción pendiente)*
![Interfaz 7](interfaces/9.png)

### Interfaz 8: Monitoreo en Tiempo Real
*(Descripción pendiente)*
![Interfaz 8](interfaces/10.png)

### Interfaz 9: Histórico de Eventos
*(Descripción pendiente)*
![Interfaz 9](interfaces/11.png)

### Interfaz 10: Ajustes de Parámetros
*(Descripción pendiente)*
![Interfaz 10](interfaces/12.png)

### Interfaz 11: Estado del Sistema
*(Descripción pendiente)*
![Interfaz 11](interfaces/13.png)

### Interfaz 12: Configuración de Red
*(Descripción pendiente)*
![Interfaz 12](interfaces/14.png)

### Interfaz 13: Acerca del Sistema
*(Descripción pendiente)*
![Interfaz 13](interfaces/15.png)

## Estructura de Archivos
