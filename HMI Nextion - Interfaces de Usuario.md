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

#### Descripción General
Interfaz especializada para la calibración del sistema Home, permite configurar parámetros de posición y seguridad para el correcto funcionamiento del equipo.

#### Estados de la Interfaz

**Estado 1: Configuración Inicial**
- **Archivo**: `4.png`
- **Descripción**: Estado inicial de configuración de parámetros
- **Elementos Visuales**:
  - Título "CALIBRACIÓN HOME"
  - Campos de distancia para ejes X, Y, Z (en mm)
  - Parámetros "Debounce" y "Separación"
  - Botón "GUARDAR" y "RESET"
  - Botón de herramientas (HOME) en estado normal
- **Comportamiento**:
  - Campos editables para ingreso de valores
  - Botón de herramientas disponible para iniciar calibración
  - Navegación restringida hasta completar el proceso

![Estado 1 - Configuración Inicial](interfaces/4.png)

**Estado 2: Calibración Activa con STOP**
- **Archivo**: `5.png`
- **Descripción**: Estado durante proceso de calibración con opción de emergencia
- **Elementos Visuales**:
  - Indicador "STOP!" prominente
  - Botón de herramientas activo en color verde
  - Botón "STOP" en color rojo
  - Botón "RESET" en color amarillo cuando está presionado
  - Valores de distancia y parámetros visibles
- **Comportamiento**:
  - Calibración en progreso (botón herramientas verde)
  - Botón "STOP" disponible para interrupción de emergencia
  - Botón "RESET" para restablecimiento del sistema
  - Navegación bloqueada durante calibración

![Estado 2 - Calibración Activa](interfaces/5.png)

#### Parámetros Configurables
- **Distancias de Ejes**:
  - X: [valor] mm
  - Y: [valor] mm  
  - Z: [valor] mm
- **Parámetros de Seguridad**:
  - Debounce: [valor] mm
  - Separación: [valor] mm

#### Funcionalidades Principales
1. **Configuración de Posición**: Ajuste fino de distancias en ejes X, Y, Z
2. **Inicio de Calibración**: Activación mediante botón de herramientas
3. **Parada de Emergencia**: Interrupción inmediata con botón STOP
4. **Restablecimiento**: Recuperación del sistema con botón RESET
5. **Persistencia de Datos**: Guardado de configuración

#### Flujo Operativo
1. **Ingreso de Parámetros** → Estado 1 (Configuración)
2. **Inicio Calibración** → Estado 2 (Proceso Activo)
3. **Interrupción STOP** → Estado 2 con STOP activo
4. **Restablecimiento RESET** → Retorno a Estado 1

#### Indicadores de Estado
- **🟢 Verde**: Calibración en progreso (botón herramientas)
- **🔴 Rojo**: Sistema detenido (botón STOP)
- **🟡 Amarillo**: Reset temporalmente activado
- **⚪ Normal**: Estado listo para operar

---

### Interfaz 3: Modo Automático

#### Descripción General
Interfaz para la ejecución de rutinas automatizadas del sistema, permitiendo seleccionar y controlar diferentes secuencias operativas predefinidas.

#### Estados de la Interfaz

**Estado 1: Selección de Rutina**
- **Archivo**: `6.png`
- **Descripción**: Estado inicial para selección de rutinas automatizadas
- **Elementos Visuales**:
  - Título "AUTOMATICO"
  - Botones "Rutina 1" y "Rutina 2" en estado normal
  - Botón "RESET" disponible
  - Sin indicador STOP visible
- **Comportamiento**:
  - Selección exclusiva de una rutina (Rutina 1 o Rutina 2)
  - Botón RESET disponible para restablecimiento
  - Navegación habilitada entre rutinas

![Estado 1 - Selección de Rutina](interfaces/6.png)

**Estado 2: Ejecución con Interrupción**
- **Archivo**: `7.png`
- **Descripción**: Estado durante ejecución de rutina con capacidad de interrupción
- **Elementos Visuales**:
  - Botón de rutina seleccionada en color verde
  - Indicador "STOP!" prominente en color rojo
  - Botón "RESET" en color amarillo cuando está presionado
  - Rutina no seleccionada en estado normal
- **Comportamiento**:
  - Rutina en ejecución (botón en verde)
  - Botón STOP disponible para interrupción inmediata
  - Botón RESET para restablecimiento del sistema
  - Comandos bloqueados durante estado STOP

![Estado 2 - Ejecución con Interrupción](interfaces/7.png)

#### Funcionalidades Principales
1. **Selección de Rutinas**: Elección entre Rutina 1 y Rutina 2 (exclusiva)
2. **Ejecución Automatizada**: Puesta en marcha de secuencia seleccionada
3. **Interrupción de Emergencia**: Parada inmediata con botón STOP
4. **Restablecimiento**: Recuperación del sistema con botón RESET

#### Flujo Operativo
1. **Selección de Rutina** → Estado 1 (Selección)
2. **Inicio Ejecución** → Estado 2 (Rutina Activa en verde)
3. **Interrupción STOP** → Estado 2 con STOP activo (rojo)
4. **Restablecimiento RESET** → Retorno a Estado 1

#### Comportamiento con Sistema en STOP
- **🔴 Botón STOP en rojo**: Indica parada de emergencia activa
- **🟡 Botón RESET en amarillo**: Indica restablecimiento temporal activo
- **⚪ Botones de rutina en color inicial**: Rutinas desactivadas durante STOP
- **Bloqueo de comandos**: Solo RESET disponible durante estado STOP

#### Reglas de Operación
- **Selección Exclusiva**: Solo una rutina puede estar activa simultáneamente
- **Secuencia de Control**: STOP debe preceder a RESET
- **Bloqueo de Comandos**: En estado STOP, solo RESET está habilitado
- **Feedback Visual**: Cambios de color indican estado del sistema

#### Indicadores de Estado
- **🟢 Verde**: Rutina en ejecución
- **🔴 Rojo**: Sistema detenido (STOP activo)
- **🟡 Amarillo**: Reset temporalmente activado
- **⚪ Normal**: Rutina disponible para selección

---

### Interfaz 4: Diagnóstico del Sistema

#### Descripción General
Interfaz de monitoreo en tiempo real que muestra el estado actual de los sensores y parámetros operativos del sistema. Esta pantalla funciona exclusivamente como visualización de datos recibidos desde la ESP32.

#### Estados de la Interfaz

**Estado 1: Sensores Inactivos**
- **Archivo**: `8.png`
- **Descripción**: Estado inicial con sensores de posición desactivados
- **Elementos Visuales**:
  - Título "DIAGNÓSTICO"
  - Sección de temperaturas por eje (X, Y, Z) en °C
  - Velocidad del usillo en RPM
  - Sensores de posición (Eje X, Y, Z) en estado inactivo
  - Indicadores de sensor en color normal/desactivado
- **Comportamiento**:
  - Visualización de datos en tiempo real
  - Solo recepción de datos desde ESP32
  - Sin capacidad de envío de comandos

![Estado 1 - Sensores Inactivos](interfaces/8.png)

**Estado 2: Sensores Activos**
- **Archivo**: `9.png`
- **Descripción**: Estado con sensores de posición activados y verificados
- **Elementos Visuales**:
  - Título "DIAGNÓSTICO"
  - Sección de temperaturas por eje (X, Y, Z) en °C
  - Velocidad del usillo en RPM con formato destacado
  - Sensores de posición con indicadores de verificación (✅)
  - Tabla organizada para ejes X, Y, Z
- **Comportamiento**:
  - Visualización de estados activos de sensores
  - Feedback visual inmediato de cambios de estado
  - Monitoreo continuo sin interacción del usuario

![Estado 2 - Sensores Activos](interfaces/9.png)

#### Parámetros Monitoreados
- **Temperaturas del Sistema**:
  - Temp X: [valor] °C
  - Temp Y: [valor] °C
  - Temp Z: [valor] °C
- **Velocidad Operativa**:
  - Usillo: [valor] RPM
- **Estado de Sensores de Posición**:
  - Eje X: Inactivo/Activo ✅
  - Eje Y: Inactivo/Activo ✅
  - Eje Z: Inactivo/Activo ✅

#### Funcionalidades Principales
1. **Monitoreo de Temperatura**: Seguimiento en tiempo real de temperaturas por eje
2. **Control de Velocidad**: Visualización de RPM del usillo
3. **Estado de Sensores**: Indicación visual de activación/desactivación
4. **Recepción de Datos**: Comunicación unidireccional desde ESP32

#### Características de Comunicación
- **🔻 Solo Recepción**: La interfaz exclusivamente recibe datos
- **📊 Actualización en Tiempo Real**: Datos refrescados continuamente
- **🚫 Sin Interacción**: No envía comandos al sistema
- **👁️ Visualización**: Propósito exclusivo de monitoreo

#### Indicadores de Estado
- **✅ Verde**: Sensor de posición activo
- **⚪ Normal/Desactivado**: Sensor de posición inactivo
- **📋 Tabla Organizada**: Presentación estructurada de estados

#### Flujo de Datos
1. **ESP32 → HMI**: Envío continuo de datos de sensores
2. **HMI → Visualización**: Actualización de indicadores en pantalla
3. **Cambio de Estado**: Transición entre Estados 1 y 2 según datos recibidos

---


### Interfaz 5: Operación Manual

#### Descripción General
Interfaz para control manual de los ejes del sistema, permitiendo ajustes incrementales de posición mediante comandos JOG con control de velocidad personalizable.

#### Estados de la Interfaz

**Estado 1: Operación Normal**
- **Archivo**: `10.png`
- **Descripción**: Estado operativo para control manual de ejes
- **Elementos Visuales**:
  - Título "OPERACIÓN MANUAL"
  - Campo "Velocidad JOG" en Hertz para configuración
  - Coordenadas actuales para ejes X, Y, Z (en mm)
  - Botones "+" y "-" para cada eje
  - Botones STOP y RESET en estado normal
- **Comportamiento**:
  - Configuración de velocidad JOG mediante entrada numérica
  - Control incremental/decremental de posición por eje
  - Visualización en tiempo real de coordenadas
  - Navegación completa habilitada

![Estado 1 - Operación Normal](interfaces/10.png)

**Estado 2: Sistema en STOP**
- **Archivo**: `11.png`
- **Descripción**: Estado de interrupción con parada de emergencia activa
- **Elementos Visuales**:
  - Indicador "STOP!" prominente en color rojo
  - Velocidad JOG mostrada en mm/min
  - Coordenadas actuales para ejes X, Y, Z (en mm)
  - Botón STOP en color rojo activo
  - Botón RESET en color amarillo cuando está presionado
- **Comportamiento**:
  - Comandos JOG bloqueados durante estado STOP
  - Solo botón RESET habilitado para restablecimiento
  - Visualización de coordenadas mantiene valores actuales
  - Velocidad JOG convertida a mm/min para referencia

![Estado 2 - Sistema en STOP](interfaces/11.png)

#### Parámetros Configurables
- **Velocidad JOG**: [valor] Hertz (configuración de incremento)
- **Coordenadas Actuales**:
  - Eje X: [valor] mm
  - Eje Y: [valor] mm
  - Eje Z: [valor] mm

#### Funcionalidades Principales
1. **Control de Velocidad JOG**: Configuración del incremento/decremento por paso
2. **Movimiento por Eje**: Control independiente para ejes X, Y, Z
3. **Incremento/Decremento**: Botones "+" y "-" para cada eje
4. **Parada de Emergencia**: Interrupción inmediata con botón STOP
5. **Restablecimiento**: Recuperación del sistema con botón RESET

#### Control de Movimiento por Eje
- **Eje X**: 
  - ➕ Botón "+": Incrementa coordenada según valor JOG
  - ➖ Botón "-": Decrementa coordenada según valor JOG
- **Eje Y**:
  - ➕ Botón "+": Incrementa coordenada según valor JOG
  - ➖ Botón "-": Decrementa coordenada según valor JOG
- **Eje Z**:
  - ➕ Botón "+": Incrementa coordenada según valor JOG
  - ➖ Botón "-": Decrementa coordenada según valor JOG

#### Flujo Operativo
1. **Configuración JOG** → Ingreso de valor de velocidad
2. **Control Manual** → Pulsación de botones +/- por eje
3. **Interrupción STOP** → Estado 2 con comandos bloqueados
4. **Restablecimiento RESET** → Retorno a Estado 1

#### Comportamiento con Sistema en STOP
- **🔴 Botón STOP en rojo**: Indica parada de emergencia activa
- **🟡 Botón RESET en amarillo**: Indica restablecimiento temporal activo
- **🚫 Botones JOG bloqueados**: Comandos +/- deshabilitados durante STOP
- **📊 Coordenadas visibles**: Valores actuales mantienen visualización

#### Conversión de Unidades
- **Configuración**: Hertz → Define frecuencia de incremento
- **Visualización STOP**: mm/min → Velocidad lineal de referencia
- **Coordenadas**: mm → Unidad estándar de posición

#### Indicadores de Estado
- **🟢 Operativo**: Sistema listo para control manual
- **🔴 STOP**: Parada de emergencia activa (comandos bloqueados)
- **🟡 RESET**: Restablecimiento temporal en proceso
- **⚪ Normal**: Estado inicial listo para operar

---

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
