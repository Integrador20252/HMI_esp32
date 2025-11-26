import network
import socket
import os
import gc
import machine
import time
from machine import Pin, Timer, UART, ADC, I2C
import struct

# ========== CONFIGURACIÓN RED Y SERVIDOR WEB OPTIMIZADA ==========
def iniciar_wifi():
    try:
        # Liberar memoria antes de iniciar WiFi
        gc.collect()
        
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(1)  # Pequeña pausa
        
        # Configuración mínima para ahorrar memoria
        ap.config(essid='ESP32_Master', password='12345678', max_clients=2)
        ap.active(True)
        
        # Esperar a que se active
        for _ in range(10):
            if ap.active():
                break
            time.sleep(0.5)
        
        if ap.active():
            print('AP listo')
            print('IP:', ap.ifconfig()[0])
            return ap
        else:
            print("Error: No se pudo activar el AP")
            return None
            
    except Exception as e:
        print(f"Error iniciando WiFi: {e}")
        return None

# Inicializar WiFi
ap = iniciar_wifi()

# ========== CONFIGURACIÓN I2C MASTER ==========
I2C_MASTER_SDA = 21
I2C_MASTER_SCL = 22
I2C_SLAVE_ADDRESS = 0x08
I2C_FREQ = 100000

# Variables para comunicación bidireccional I2C
i2c_comandos_recibidos = []
i2c_mensajes_esclavo = []
i2c_ultima_lectura = 0

i2c_comandos_pendientes = []
i2c_esperando_respuesta = False
i2c_tiempo_envio = 0
I2C_TIMEOUT_MS = 1000  # 1 segundo de timeout

i2c = None
slave_connected = False

def init_i2c_master():
    global i2c
    try:
        i2c = I2C(0, scl=Pin(I2C_MASTER_SCL), sda=Pin(I2C_MASTER_SDA), freq=I2C_FREQ)
        print("I2C Maestro inicializado")
        return True
    except Exception as e:
        print("Error inicializando I2C maestro:", e)
        return False

def scan_i2c():
    global i2c
    try:
        devices = i2c.scan()
        if devices:
            print("Dispositivos I2C encontrados:", [hex(device) for device in devices])
            return devices
        else:
            print("No se encontraron dispositivos I2C")
            return []
    except Exception as e:
        print("Error escaneando I2C:", e)
        return []

def check_slave():
    global slave_connected
    devices = scan_i2c()
    connected = I2C_SLAVE_ADDRESS in devices
    if connected != slave_connected:
        slave_connected = connected
        if connected:
            print("Esclavo I2C conectado en 0x{:02X}".format(I2C_SLAVE_ADDRESS))
        else:
            print("Esclavo I2C desconectado")
    return connected

def send_i2c_command(command):
    global i2c, i2c_mensajes_esclavo
    try:
        if not check_slave():
            return "ERROR:ESCLAVO_NO_CONECTADO"
        
        # Convertir comando a bytes
        cmd_bytes = command.encode('utf-8')
        
        # Enviar comando
        i2c.writeto(I2C_SLAVE_ADDRESS, cmd_bytes)
        print("Comando I2C enviado:", command)
        
        return "COMANDO_ENVIADO"
        
    except Exception as e:
        error_msg = "ERROR:I2C - " + str(e)
        print(error_msg)
        return error_msg
    
def leer_mensajes_esclavo():
    """Intenta leer mensajes no solicitados del esclavo I2C"""
    global i2c, i2c_mensajes_esclavo
    
    try:
        # Verificar si el esclavo está conectado
        if not check_slave():
            return None
            
        # Intentar leer cualquier mensaje pendiente (sin enviar comando primero)
        response = i2c.readfrom(I2C_SLAVE_ADDRESS, 256)
        
        # Convertir a string
        response_str = ""
        for byte in response:
            if byte == 0:
                break
            response_str += chr(byte)
        
        if response_str and response_str not in ["OK", ""]:
            timestamp = time.ticks_ms()
            i2c_mensajes_esclavo.append(f"[{timestamp}] {response_str}")
            print(f"Mensaje esclavo I2C: {response_str}")
            
            # Mantener solo los últimos 10 mensajes
            if len(i2c_mensajes_esclavo) > 10:
                i2c_mensajes_esclavo.pop(0)
                
            return response_str
            
    except Exception as e:
        # Error esperado si no hay datos
        pass
        
    return None

def enviar_comando_i2c_async(comando):
    """Envía un comando I2C y maneja la respuesta de forma asíncrona"""
    global i2c_esperando_respuesta, i2c_tiempo_envio, i2c_comandos_pendientes
    
    try:
        if not check_slave():
            return "ERROR:ESCLAVO_NO_CONECTADO"
        
        # Convertir comando a bytes
        cmd_bytes = comando.encode('utf-8')
        
        # Enviar comando
        i2c.writeto(I2C_SLAVE_ADDRESS, cmd_bytes)
        print("Comando I2C enviado (async):", comando)
        
        # Marcar que estamos esperando respuesta
        i2c_esperando_respuesta = True
        i2c_tiempo_envio = time.ticks_ms()
        
        # Guardar comando en cola de pendientes
        i2c_comandos_pendientes.append({
            'comando': comando,
            'timestamp': i2c_tiempo_envio,
            'intentos': 0
        })
        
        return "COMANDO_ENVIADO"
        
    except Exception as e:
        error_msg = "ERROR:I2C - " + str(e)
        print(error_msg)
        return error_msg

def verificar_respuesta_i2c():
    """Verifica si hay respuesta para comandos I2C pendientes (se llama desde timer)"""
    global i2c_esperando_respuesta, i2c_comandos_pendientes, i2c_mensajes_esclavo
    
    if not i2c_esperando_respuesta or not i2c_comandos_pendientes:
        return None
    
    # Verificar timeout
    if time.ticks_diff(time.ticks_ms(), i2c_tiempo_envio) > I2C_TIMEOUT_MS:
        print("Timeout en comando I2C")
        i2c_esperando_respuesta = False
        if i2c_comandos_pendientes:
            i2c_comandos_pendientes.pop(0)
        return "TIMEOUT"
    
    try:
        # Intentar leer respuesta
        response = i2c.readfrom(I2C_SLAVE_ADDRESS, 256)
        
        # Convertir a string
        response_str = ""
        for byte in response:
            if byte == 0:
                break
            response_str += chr(byte)
        
        if response_str and response_str != "":
            # Respuesta recibida
            i2c_esperando_respuesta = False
            comando = i2c_comandos_pendientes.pop(0) if i2c_comandos_pendientes else "Desconocido"
            
            # Guardar mensaje del esclavo
            timestamp = time.ticks_ms()
            i2c_mensajes_esclavo.append(f"[{timestamp}] Respuesta: {response_str}")
            
            print(f"Respuesta I2C recibida: {response_str}")
            
            # Actualizar Nextion si es necesario
            if i2c_comandos_recibidos and i2c_comandos_recibidos[-1].startswith(comando.get('comando', '').split()[0]):
                send_cmd(f't5.txt="R: {response_str[-20:]}"')
            
            return response_str
            
    except Exception as e:
        # No hay respuesta aún, incrementar intentos
        if i2c_comandos_pendientes:
            i2c_comandos_pendientes[0]['intentos'] += 1
            if i2c_comandos_pendientes[0]['intentos'] > 10:  # Máximo 10 intentos
                i2c_esperando_respuesta = False
                i2c_comandos_pendientes.pop(0)
                print("Máximo de intentos alcanzado para comando I2C")
    
    return None

# ========== COMANDOS CNC VÍA I2C ==========
def mover_eje(eje, pasos, hz, acc_ms, dec_ms, direccion):
    cmd = f"MOVE{eje.upper()} {pasos} {hz} {acc_ms} {dec_ms} {direccion}"
    return send_i2c_command(cmd)

def home_cnc():
    return send_i2c_command("HOME")

def stop_cnc():
    return send_i2c_command("STOP")

def reset_cnc():
    return send_i2c_command("RESET")

def get_position():
    return send_i2c_command("GET_POSITION")

def get_status_cnc():
    return send_i2c_command("STATUS")

def send_Rutina1_cnc():
    return send_i2c_command("RUTINA_1")

def send_Rutina2_cnc():
    return send_i2c_command("RUTINA_2")

def start_jog(eje, direccion, velocidad=5000):
    dir_code = 1 if direccion.upper() in ['+', 'POS', '1', 'FORWARD'] else 0
    cmd = f"START_JOG {eje.upper()} {dir_code} {velocidad}"
    return send_i2c_command(cmd)

def stop_jog():
    return send_i2c_command("STOP_JOG")

# ========== CONFIGURACIÓN NEXTION ==========
uart = UART(1, 9600, tx=Pin(17), rx=Pin(16))

# ========== CONFIGURACIÓN SENSORES PT100 ==========
adc_pt100_1 = ADC(Pin(32))
adc_pt100_2 = ADC(Pin(33))  
adc_pt100_3 = ADC(Pin(34))

# Configurar ADC para máximo rango (0-3.3V)
adc_pt100_1.atten(ADC.ATTN_11DB)  # Rango completo 0-3.3V
adc_pt100_2.atten(ADC.ATTN_11DB)
adc_pt100_3.atten(ADC.ATTN_11DB)
adc_pt100_1.width(ADC.WIDTH_12BIT)  # 12 bits (0-4095)
adc_pt100_2.width(ADC.WIDTH_12BIT)
adc_pt100_3.width(ADC.WIDTH_12BIT)

# Parámetros de conversión (TRANSMISOR 4-20mA)
RESISTOR_SHUNT = 165.0      # Resistor de 165Ω
RANGE_MIN_MA = 4.0          # 4mA = 0°C
RANGE_MAX_MA = 20.0         # 20mA = 200°C  
TEMP_MIN = 0.0              # Temperatura mínima
TEMP_MAX = 200.0            # Temperatura máxima

# ========== CONFIGURACIÓN INTERRUPTORES DIGITALES POR EJES ==========
# Eje X: XL0 (Límite inferior), XLF (Fallo límite inferior), XH0 (HOME), XHF (Fallo límite superior)
switches_x = [
    Pin(13, Pin.IN, Pin.PULL_DOWN),  # XL0 - Límite inferior X
    Pin(12, Pin.IN, Pin.PULL_DOWN),  # XLF - Fallo límite inferior X
    Pin(14, Pin.IN, Pin.PULL_DOWN),  # XH0 - HOME X
    Pin(27, Pin.IN, Pin.PULL_DOWN)   # XHF - Fallo límite superior X
]

# Eje Y: YL0 (Límite inferior), YLF (Fallo límite inferior), YH0 (HOME), YHF (Fallo límite superior)
switches_y = [
    Pin(26, Pin.IN, Pin.PULL_DOWN),  # YL0 - Límite inferior Y
    Pin(25, Pin.IN, Pin.PULL_DOWN),  # YLF - Fallo límite inferior Y
    Pin(15, Pin.IN, Pin.PULL_DOWN),  # YH0 - HOME Y
    Pin(2,  Pin.IN, Pin.PULL_DOWN)   # YHF - Fallo límite superior Y
]

# Eje Z: ZL0 (Límite inferior), ZLF (Fallo límite inferior), ZH0 (HOME), ZHF (Fallo límite superior)
switches_z = [
    Pin(4,  Pin.IN, Pin.PULL_DOWN),  # ZL0 - Límite inferior Z
    Pin(18,  Pin.IN, Pin.PULL_DOWN),  # ZLF - Fallo límite inferior Z
    Pin(16, Pin.IN, Pin.PULL_DOWN),  # ZH0 - HOME Z
    Pin(19, Pin.IN, Pin.PULL_DOWN)   # ZHF - Fallo límite superior Z
]

# Nombres de los sensores para display
nombres_sensores_x = ["XL0", "XLF", "XH0", "XHF"]
nombres_sensores_y = ["YL0", "YLF", "YH0", "YHF"] 
nombres_sensores_z = ["ZL0", "ZLF", "ZH0", "ZHF"]

# Estados de los switches por eje (usando bytearray para ahorrar memoria)
estados_switches_x = bytearray(4)
estados_switches_y = bytearray(4)
estados_switches_z = bytearray(4)

# Variables para estado de HOME
home_x_detectado = False
home_y_detectado = False
home_z_detectado = False
modo_home_activo = False

# ========== VARIABLES GLOBALES DEL SISTEMA ==========
sistema_activo = False
inicializacion_completada = False
reinicio_en_progreso = False
contador_tarea_principal = 0

# Temperaturas como tupla para ahorrar memoria
temperaturas_pt100 = (0.0, 0.0, 0.0)

# Variables adicionales para diagnóstico
adc_values = [0, 0, 0]
voltajes_pt100 = [0.0, 0.0, 0.0]

# Variables I2C
i2c_paquetes_enviados = 0
i2c_velocidad_mbps = 0.1  # I2C típicamente 100 kHz = 0.1 Mbps
i2c_estado = "Desconectado"
i2c_ultimo_envio = 0

# Timers
timer_nextion = Timer(0)
timer_principal = Timer(1)
timer_servidor = Timer(2)

# ========== FUNCIONES CONVERSIÓN PT100 ==========
def leer_pt100(adc_sensor, sensor_num):
    """Función para lectura PT100"""
    try:
        # Leer valor ADC (0-4095 para 12 bits)
        adc_value = adc_sensor.read()
        
        # Convertir a voltaje (0-3.3V)
        voltage = (adc_value / 4095.0) * 3.3
        
        # Calcular corriente a través del resistor shunt
        current_ma = (voltage / RESISTOR_SHUNT) * 1000.0  # Convertir a mA
        
        # Limitar al rango esperado 4-20mA
        current_ma = max(RANGE_MIN_MA, min(RANGE_MAX_MA, current_ma))
        
        # Convertir corriente (4-20mA) a temperatura (0-200°C)
        temperatura = TEMP_MIN + ((current_ma - RANGE_MIN_MA) * 
                                 (TEMP_MAX - TEMP_MIN) / 
                                 (RANGE_MAX_MA - RANGE_MIN_MA))
        
        return adc_value, voltage, temperatura
        
    except Exception as e:
        print(f"Error leyendo PT100-{sensor_num}: {e}")
        return 0, 0.0, 0.0

def leer_todos_pt100():
    """Lee todos los sensores PT100 y actualiza variables globales"""
    global temperaturas_pt100, adc_values, voltajes_pt100
    
    # Leer PT100-1 (GPIO32)
    adc1, volt1, temp1 = leer_pt100(adc_pt100_1, 1)
    adc_values[0] = adc1
    voltajes_pt100[0] = volt1
    # Actualizar tupla de temperaturas
    temperaturas_pt100 = (temp1, temperaturas_pt100[1], temperaturas_pt100[2])
    
    # Leer PT100-2 (GPIO33)
    adc2, volt2, temp2 = leer_pt100(adc_pt100_2, 2)
    adc_values[1] = adc2
    voltajes_pt100[1] = volt2
    temperaturas_pt100 = (temperaturas_pt100[0], temp2, temperaturas_pt100[2])
    
    # Leer PT100-3 (GPIO34)
    adc3, volt3, temp3 = leer_pt100(adc_pt100_3, 3)
    adc_values[2] = adc3
    voltajes_pt100[2] = volt3
    temperaturas_pt100 = (temperaturas_pt100[0], temperaturas_pt100[1], temp3)

def leer_switches():
    global estados_switches_x, estados_switches_y, estados_switches_z
    global home_x_detectado, home_y_detectado, home_z_detectado
    
    # Leer switches del eje X - usar 0/1 en bytearray
    for i, switch in enumerate(switches_x):
        estados_switches_x[i] = 1 if (switch.value() == 1) else 0
    
    # Leer switches del eje Y
    for i, switch in enumerate(switches_y):
        estados_switches_y[i] = 1 if (switch.value() == 1) else 0
    
    # Leer switches del eje Z
    for i, switch in enumerate(switches_z):
        estados_switches_z[i] = 1 if (switch.value() == 1) else 0
    
    # Verificar límites (cualquier límite activo detiene el movimiento)
    limite_x_activado = estados_switches_x[0] or estados_switches_x[3]  # XL0 o XHF
    limite_y_activado = estados_switches_y[0] or estados_switches_y[3]  # YL0 o YHF
    limite_z_activado = estados_switches_z[0] or estados_switches_z[3]  # ZL0 o ZHF
    
    # Si se activa cualquier límite, enviar comando STOP de emergencia
    if (limite_x_activado or limite_y_activado or limite_z_activado) and sistema_activo:
        print("¡LÍMITE ACTIVADO! Enviando STOP de emergencia")
        send_i2c_command("STOP")
        # También actualizar Nextion
        send_cmd('t14.txt="¡LÍMITE ACTIVADO!"')
    
    # Verificar sensores de HOME si estamos en modo HOME
    if modo_home_activo:
        verificar_sensores_home()

def verificar_sensores_home():
    """Verifica los sensores de HOME y notifica cuando se detectan"""
    global home_x_detectado, home_y_detectado, home_z_detectado
    
    # Verificar HOME X (XH0 - índice 2 en switches_x)
    if estados_switches_x[2] and not home_x_detectado:
        home_x_detectado = True
        print("HOME X detectado!")
        enviar_home_detectado('X')
        actualizar_indicador_home_nextion('X', True)
        send_cmd('t15.txt="HOME X: DETECTADO"')
    
    # Verificar HOME Y (YH0 - índice 2 en switches_y)
    if estados_switches_y[2] and not home_y_detectado:
        home_y_detectado = True
        print("HOME Y detectado!")
        enviar_home_detectado('Y')
        actualizar_indicador_home_nextion('Y', True)
        send_cmd('t16.txt="HOME Y: DETECTADO"')
    
    # Verificar HOME Z (ZH0 - índice 2 en switches_z)
    if estados_switches_z[2] and not home_z_detectado:
        home_z_detectado = True
        print("HOME Z detectado!")
        enviar_home_detectado('Z')
        actualizar_indicador_home_nextion('Z', True)
        send_cmd('t17.txt="HOME Z: DETECTADO"')

def enviar_home_detectado(eje):
    """Envía comando por I2C indicando que se detectó HOME"""
    comando = f"HOME_{eje}_DETECTED"
    send_i2c_command(comando)
    print(f"Comando I2C enviado: {comando}")

def actualizar_indicador_home_nextion(eje, detectado):
    """Actualiza los indicadores de HOME en la Nextion"""
    if eje == 'X':
        pic_num = 3
    elif eje == 'Y':
        pic_num = 4
    elif eje == 'Z':
        pic_num = 5
    else:
        return
    
    estado = 1 if detectado else 0
    send_cmd(f'pic{pic_num}.pic={estado}')

def iniciar_home():
    """Inicia la secuencia de HOME para todos los ejes"""
    global modo_home_activo, home_x_detectado, home_y_detectado, home_z_detectado
    
    print("Iniciando secuencia HOME...")
    modo_home_activo = True
    home_x_detectado = False
    home_y_detectado = False
    home_z_detectado = False
    
    # Resetear indicadores en Nextion
    actualizar_indicador_home_nextion('X', False)
    actualizar_indicador_home_nextion('Y', False)
    actualizar_indicador_home_nextion('Z', False)
    
    # Resetear textos de HOME
    send_cmd('t15.txt="HOME X: BUSCANDO"')
    send_cmd('t16.txt="HOME Y: BUSCANDO"')
    send_cmd('t17.txt="HOME Z: BUSCANDO"')
    
    # Enviar comando HOME al esclavo
    return home_cnc()

def finalizar_home():
    """Finaliza la secuencia de HOME"""
    global modo_home_activo
    modo_home_activo = False
    print("Secuencia HOME finalizada")

def contar_switches_activos():
    """Cuenta switches activos por eje y total"""
    activos_x = sum(1 for estado in estados_switches_x if estado)
    activos_y = sum(1 for estado in estados_switches_y if estado)
    activos_z = sum(1 for estado in estados_switches_z if estado)
    total = activos_x + activos_y + activos_z
    return total, activos_x, activos_y, activos_z

# ========== FUNCIONES NEXTION ==========
def send_cmd(cmd):
    uart.write(cmd.encode('utf-8'))
    uart.write(b'\xFF\xFF\xFF')

def inicializar_nextion():
    global reinicio_en_progreso
    print("Inicializando Nextion...")
    send_cmd("rest")
    reinicio_en_progreso = True
    timer_nextion.init(period=2000, mode=Timer.ONE_SHOT, callback=post_reinicio)

def post_reinicio(timer):
    global reinicio_en_progreso, inicializacion_completada
    timer_nextion.deinit()
    reinicio_en_progreso = False
    print("Nextion reiniciada, configurando página inicial...")
    timer_nextion.init(period=500, mode=Timer.ONE_SHOT, callback=configurar_textos_iniciales)

def configurar_textos_iniciales(timer):
    send_cmd('DistX.txt="0000"')
    send_cmd('DistY.txt="0000"')
    send_cmd('DistZ.txt="0000"')
    send_cmd('Debounce.txt="0000"')
    send_cmd('Separacion.txt="0000"')
    
    global inicializacion_completada
    inicializacion_completada = True
    print("Nextion inicializada completamente")

def actualizar_pantalla():
    if sistema_activo:
        # Actualizar temperaturas
        send_cmd(f't0.txt="PT100-1: {temperaturas_pt100[0]:.1f}°C"')
        send_cmd(f't1.txt="PT100-2: {temperaturas_pt100[1]:.1f}°C"')
        send_cmd(f't2.txt="PT100-3: {temperaturas_pt100[2]:.1f}°C"')
        
        # Actualizar estado de sensores del eje X
        estado_x = obtener_estado_sensores_texto('X')
        send_cmd(f't10.txt="Eje X: {estado_x}"')
        
        # Actualizar estado de sensores del eje Y
        estado_y = obtener_estado_sensores_texto('Y')
        send_cmd(f't11.txt="Eje Y: {estado_y}"')
        
        # Actualizar estado de sensores del eje Z
        estado_z = obtener_estado_sensores_texto('Z')
        send_cmd(f't12.txt="Eje Z: {estado_z}"')
        
        # Estado general del sistema
        send_cmd('t4.txt="Sistema ACTIVO - I2C Activo"')
        
        # Mostrar estado I2C
        estado_i2c = "Esperando" if i2c_esperando_respuesta else i2c_estado
        send_cmd(f't7.txt="I2C: {estado_i2c}"')
        send_cmd(f't8.txt="Paquetes: {i2c_paquetes_enviados}"')
        
        # Mostrar estado HOME
        estado_home = "ACTIVO" if modo_home_activo else "INACTIVO"
        send_cmd(f't13.txt="HOME: {estado_home}"')
        
        # Mostrar estado de límites
        limite_activado = (estados_switches_x[0] or estados_switches_x[3] or 
                          estados_switches_y[0] or estados_switches_y[3] or 
                          estados_switches_z[0] or estados_switches_z[3])
        if limite_activado:
            send_cmd('t14.txt="¡LÍMITE ACTIVADO!"')
        else:
            send_cmd('t14.txt="Límites: OK"')
        
        # Mostrar últimos mensajes
        if i2c_mensajes_esclavo:
            ultimo_msg = i2c_mensajes_esclavo[-1][-20:]
            send_cmd(f't6.txt="Esclavo: {ultimo_msg}"')
    else:
        send_cmd('t0.txt="Sistema PAUSADO"')
        send_cmd('t1.txt="Presione START"')
        send_cmd('t2.txt="para activar"')
        send_cmd('t10.txt="Eje X: ---"')
        send_cmd('t11.txt="Eje Y: ---"')
        send_cmd('t12.txt="Eje Z: ---"')
        send_cmd('t4.txt="SISTEMA PAUSADO"')
        send_cmd('t7.txt="I2C: Desconectado"')
        send_cmd('t13.txt="HOME: INACTIVO"')
        send_cmd('t14.txt="Límites: ---"')

def obtener_estado_sensores_texto(eje):
    """Obtiene el texto del estado de los sensores de un eje específico"""
    if eje == 'X':
        estados = estados_switches_x
        nombres = nombres_sensores_x
    elif eje == 'Y':
        estados = estados_switches_y
        nombres = nombres_sensores_y
    elif eje == 'Z':
        estados = estados_switches_z
        nombres = nombres_sensores_z
    else:
        return "Eje desconocido"
    
    sensores_activos = []
    for i, estado in enumerate(estados):
        if estado:
            sensores_activos.append(nombres[i])
    
    if sensores_activos:
        return ", ".join(sensores_activos)
    else:
        return "Todos INACTIVOS"

def procesar_comando_start():
    global sistema_activo
    timer_nextion.deinit()
        
    print(">>> Home recibido - Activando sistema")
    sistema_activo = True
    send_cmd('X0="0"')
    send_cmd('Y0="0"')
    send_cmd('Z0="0"')
    timer_nextion.init(period=500, mode=Timer.ONE_SHOT, callback=post_cambio_pagina)

def post_cambio_pagina(timer):
    print("Post cambio de página ejecutado")
    send_cmd('t4.txt="Sistema ACTIVO - I2C Activo"')
    actualizar_pantalla()

def procesar_comando_stop():
    global sistema_activo
    print(">>> STOP recibido - Pausando sistema")
    sistema_activo = False
    actualizar_pantalla()

def procesar_comandos_nextion():
    global sistema_activo, i2c_comandos_recibidos
    
    try:
        if uart.any():
            datos = uart.read()
            if datos:
                mensaje = datos.decode('utf-8').strip()
                print(f"Nextion dice: {mensaje}")
                
                if "ON" in mensaje.lower():
                    procesar_comando_start()
                elif "OFF" in mensaje.lower():
                    procesar_comando_stop()
                elif mensaje.startswith("I2C:"):
                    # Comando I2C desde Nextion
                    comando = mensaje[4:].strip()  # Remover "I2C:"
                    print(f"Comando I2C desde Nextion: {comando}")
                    
                    # Guardar en historial
                    i2c_comandos_recibidos.append(comando)
                    if len(i2c_comandos_recibidos) > 10:
                        i2c_comandos_recibidos.pop(0)
                    
                    # Ejecutar comando I2C
                    respuesta = ejecutar_comando_i2c_desde_nextion(comando)
                    
                    # Enviar respuesta a Nextion
                    send_cmd(f't5.txt="I2C: {respuesta}"')
                    
    except Exception as e:
        print(f"Error procesando Nextion: {e}")

def ejecutar_comando_i2c_desde_nextion(comando):
    """Ejecuta comandos I2C específicos desde la Nextion de forma asíncrona"""
    comando = comando.upper().strip()
    
    try:
        # Comando HOME especial
        if comando == "HOME":
            return iniciar_home()
            
        elif comando == "STOP_HOME":
            finalizar_home()
            return "HOME_DETENIDO"
        
        # Comandos que necesitan respuesta inmediata
        comandos_con_respuesta = ["STOP", "RESET", "GET_POSITION", "STATUS", "READ_MESSAGES", "RUTINA_1", "RUTINA_2"]
        
        if any(cmd in comando for cmd in comandos_con_respuesta):
            # Usar sistema asíncrono para comandos que esperan respuesta
            resultado = enviar_comando_i2c_async(comando)
            if resultado == "COMANDO_ENVIADO":
                return "COMANDO_ENVIADO_ESPERANDO_RESPUESTA"
            else:
                return resultado
        else:
            # Comandos que no necesitan respuesta inmediata
            return send_i2c_command(comando)
            
    except Exception as e:
        return f"ERROR: {str(e)}"

def enviar_datos_i2c():
    global i2c_paquetes_enviados, i2c_estado, i2c_ultimo_envio
    
    if not sistema_activo or i2c_esperando_respuesta:
        return
    
    try:
        # Preparar datos detallados de switches
        cmd = (f"SENSOR_DATA {temperaturas_pt100[0]:.2f},{temperaturas_pt100[1]:.2f},{temperaturas_pt100[2]:.2f},"
               f"{int(estados_switches_x[0])},{int(estados_switches_x[1])},{int(estados_switches_x[2])},{int(estados_switches_x[3])},"
               f"{int(estados_switches_y[0])},{int(estados_switches_y[1])},{int(estados_switches_y[2])},{int(estados_switches_y[3])},"
               f"{int(estados_switches_z[0])},{int(estados_switches_z[1])},{int(estados_switches_z[2])},{int(estados_switches_z[3])},"
               f"{1 if sistema_activo else 0},{1 if modo_home_activo else 0}")
        
        # Enviar comando por I2C (sin esperar respuesta)
        response = send_i2c_command(cmd)
        
        i2c_paquetes_enviados += 1
        i2c_estado = "Conectado"
        i2c_ultimo_envio = time.ticks_ms()
        
        return response
        
    except Exception as e:
        i2c_estado = f"Error: {str(e)}"
        print(f"Error I2C: {e}")
        return None

def verificar_conexion_i2c():
    global i2c_estado
    if time.ticks_diff(time.ticks_ms(), i2c_ultimo_envio) > 5000:
        i2c_estado = "Desconectado"

# ========== TAREA PRINCIPAL COMBINADA ==========
def tarea_principal_combinada(timer):
    """Tarea principal que combina múltiples funciones"""
    global contador_tarea_principal

    if inicializacion_completada and not reinicio_en_progreso:
        procesar_comandos_nextion()
    
    leer_switches()
    verificar_conexion_i2c()
    
    # Leer temperaturas cada 5 iteraciones (0.5 segundos)
    if contador_tarea_principal % 5 == 0:
        leer_todos_pt100()
    
    # Verificar respuestas I2C pendientes cada iteración
    respuesta = verificar_respuesta_i2c()
    if respuesta and respuesta != "TIMEOUT":
        # Procesar respuesta si es necesario
        if "HOME" in respuesta and "DETECTED" in respuesta:
            print(f"Esclavo confirmó: {respuesta}")
    
    # Leer mensajes espontáneos del esclavo cada 2 segundos
    if contador_tarea_principal % 20 == 0:
        mensaje = leer_mensajes_esclavo()
        if mensaje:
            send_cmd(f't6.txt="Esclavo: {mensaje[-30:]}"')
    
    # Enviar datos de sensores por I2C si el sistema está activo
    if sistema_activo and contador_tarea_principal % 10 == 0:
        if not i2c_esperando_respuesta:
            enviar_datos_i2c()
    
    if sistema_activo:
        contador_tarea_principal += 1
        if contador_tarea_principal >= 40:
            contador_tarea_principal = 0
            actualizar_pantalla()
            
            # Mostrar diagnóstico detallado en consola
            print("=== Sistema Activo ===")
            print(f"PT100-1: {temperaturas_pt100[0]:.2f}°C")
            print(f"PT100-2: {temperaturas_pt100[1]:.2f}°C") 
            print(f"PT100-3: {temperaturas_pt100[2]:.2f}°C")
            
            print("Eje X:", obtener_estado_sensores_texto('X'))
            print("Eje Y:", obtener_estado_sensores_texto('Y'))
            print("Eje Z:", obtener_estado_sensores_texto('Z'))
            
            print(f"HOME X: {'DETECTADO' if home_x_detectado else 'NO'}")
            print(f"HOME Y: {'DETECTADO' if home_y_detectado else 'NO'}")
            print(f"HOME Z: {'DETECTADO' if home_z_detectado else 'NO'}")
            
            print(f"I2C: {i2c_estado} - Paquetes: {i2c_paquetes_enviados}")
            print(f"Modo HOME: {'ACTIVO' if modo_home_activo else 'INACTIVO'}")
            print("======================")

# ========== HTML SIMPLIFICADO - CORREGIDO ==========
HTML = """<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="2"> 
<title>Sistema ESP32 Master</title>
<style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .container { max-width: 800px; margin: 0 auto; }
    .panel { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .sensor-data { background: #e8f4fd; border-left: 4px solid #2196F3; }
    .limit-data { background: #fff3e0; border-left: 4px solid #ff9800; }
    .i2c-data { background: #e8f5e8; border-left: 4px solid #4CAF50; }
    .status-on { color: #4CAF50; font-weight: bold; }
    .status-off { color: #f44336; font-weight: bold; }
    .cnc-btn { 
        background: #2196F3; 
        color: white; 
        padding: 8px 16px; 
        margin: 4px; 
        border: none; 
        border-radius: 4px; 
        cursor: pointer;
        font-size: 14px;
    }
    .cnc-btn:hover { background: #0b7dda; }
    .emergency-btn { background: #f44336; }
    .emergency-btn:hover { background: #d32f2f; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="container">
    <h2>🏭 Sistema CNC ESP32 Master</h2>

    <div class="panel">
        <h3>🎛️ Control CNC</h3>
        <button class="cnc-btn" onclick="sendCommand('HOME')">🏠 HOME</button>
        <button class="cnc-btn" onclick="sendCommand('RESET')">🔄 RESET</button>
        <button class="cnc-btn emergency-btn" onclick="sendCommand('STOP')">🛑 STOP Emergencia</button>
        <button class="cnc-btn" onclick="sendCommand('GET_POSITION')">📍 Posición</button>
        <button class="cnc-btn" onclick="sendCommand('STATUS')">📊 Estado CNC</button>
    </div>

    <div class="grid">
        <div class="panel sensor-data">
            <h3>🌡️ Sensores PT100</h3>
            <p><strong>PT100-1:</strong> %.1f °C</p>
            <p><strong>PT100-2:</strong> %.1f °C</p>
            <p><strong>PT100-3:</strong> %.1f °C</p>
        </div>

        <div class="panel">
            <h3>📊 Estado del Sistema</h3>
            <p><strong>Nextion:</strong> <span class="%s">%s</span></p>
            <p><strong>Sistema:</strong> <span class="%s">%s</span></p>
            <p><strong>I2C:</strong> <span class="%s">%s</span></p>
            <p><strong>Memoria libre:</strong> %d bytes</p>
            <p><strong>Paquetes I2C:</strong> %d</p>
        </div>
    </div>

    <div class="panel limit-data">
        <h3>⚡ Finales de Carrera</h3>
        <div class="grid">
            <div>
                <h4>Eje X</h4>
                <p>XL0: <span class="%s">%s</span></p>
                <p>XLF: <span class="%s">%s</span></p>
                <p>XH0: <span class="%s">%s</span></p>
                <p>XHF: <span class="%s">%s</span></p>
                <p><strong>HOME X:</strong> <span class="%s">%s</span></p>
            </div>
            <div>
                <h4>Eje Y</h4>
                <p>YL0: <span class="%s">%s</span></p>
                <p>YLF: <span class="%s">%s</span></p>
                <p>YH0: <span class="%s">%s</span></p>
                <p>YHF: <span class="%s">%s</span></p>
                <p><strong>HOME Y:</strong> <span class="%s">%s</span></p>
            </div>
            <div>
                <h4>Eje Z</h4>
                <p>ZL0: <span class="%s">%s</span></p>
                <p>ZLF: <span class="%s">%s</span></p>
                <p>ZH0: <span class="%s">%s</span></p>
                <p>ZHF: <span class="%s">%s</span></p>
                <p><strong>HOME Z:</strong> <span class="%s">%s</span></p>
            </div>
        </div>
    </div>

    <div class="panel i2c-data">
        <h3>📡 Comunicación I2C</h3>
        <p><strong>Estado:</strong> %s</p>
        <p><strong>Comandos pendientes:</strong> %d</p>
        <p><strong>Esperando respuesta:</strong> %s</p>
        <p><strong>Últimos mensajes esclavo:</strong></p>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 100px; overflow-y: auto;">
            %s
        </div>
    </div>

    <div class="panel">
        <h3>🔍 Diagnóstico PT100</h3>
        <div class="grid">
            <div>
                <p><strong>PT100-1:</strong> ADC=%d, Voltaje=%.3fV</p>
                <p><strong>PT100-2:</strong> ADC=%d, Voltaje=%.3fV</p>
                <p><strong>PT100-3:</strong> ADC=%d, Voltaje=%.3fV</p>
            </div>
        </div>
    </div>
</div>

<script>
function sendCommand(cmd) {
    fetch('/i2c?command=' + encodeURIComponent(cmd))
        .then(response => response.text())
        .then(data => {
            alert('Respuesta: ' + data);
        })
        .catch(error => {
            alert('Error: ' + error);
        });
}
</script>
</body>
</html>"""

# ========== FUNCIONES SERVIDOR WEB CORREGIDAS ==========
def get_estado_sistema():
    """Versión simplificada para ahorrar memoria"""
    estado_nextion = "OK" if inicializacion_completada else "INIT"
    estado_sistema = "ACTIVO" if sistema_activo else "PAUSADO"
    return estado_nextion, estado_sistema

def generar_pagina_principal():
    """Genera la página HTML principal - VERSIÓN CORREGIDA"""
    free_mem = gc.mem_free()
    estado_nextion, estado_sistema = get_estado_sistema()
    
    # Determinar clases CSS para estados
    nextion_class = "status-on" if inicializacion_completada else "status-off"
    sistema_class = "status-on" if sistema_activo else "status-off" 
    i2c_class = "status-on" if i2c_estado == "Conectado" else "status-off"
    
    # Generar estados de sensores individualmente (SIN OPERADOR *)
    # Eje X
    xl0_cls = "status-on" if estados_switches_x[0] else "status-off"
    xl0_txt = "ACTIVO" if estados_switches_x[0] else "INACTIVO"
    xlf_cls = "status-on" if estados_switches_x[1] else "status-off"
    xlf_txt = "ACTIVO" if estados_switches_x[1] else "INACTIVO"
    xh0_cls = "status-on" if estados_switches_x[2] else "status-off"
    xh0_txt = "ACTIVO" if estados_switches_x[2] else "INACTIVO"
    xhf_cls = "status-on" if estados_switches_x[3] else "status-off"
    xhf_txt = "ACTIVO" if estados_switches_x[3] else "INACTIVO"
    home_x_cls = "status-on" if home_x_detectado else "status-off"
    home_x_txt = "DETECTADO" if home_x_detectado else "NO"
    
    # Eje Y
    yl0_cls = "status-on" if estados_switches_y[0] else "status-off"
    yl0_txt = "ACTIVO" if estados_switches_y[0] else "INACTIVO"
    ylf_cls = "status-on" if estados_switches_y[1] else "status-off"
    ylf_txt = "ACTIVO" if estados_switches_y[1] else "INACTIVO"
    yh0_cls = "status-on" if estados_switches_y[2] else "status-off"
    yh0_txt = "ACTIVO" if estados_switches_y[2] else "INACTIVO"
    yhf_cls = "status-on" if estados_switches_y[3] else "status-off"
    yhf_txt = "ACTIVO" if estados_switches_y[3] else "INACTIVO"
    home_y_cls = "status-on" if home_y_detectado else "status-off"
    home_y_txt = "DETECTADO" if home_y_detectado else "NO"
    
    # Eje Z
    zl0_cls = "status-on" if estados_switches_z[0] else "status-off"
    zl0_txt = "ACTIVO" if estados_switches_z[0] else "INACTIVO"
    zlf_cls = "status-on" if estados_switches_z[1] else "status-off"
    zlf_txt = "ACTIVO" if estados_switches_z[1] else "INACTIVO"
    zh0_cls = "status-on" if estados_switches_z[2] else "status-off"
    zh0_txt = "ACTIVO" if estados_switches_z[2] else "INACTIVO"
    zhf_cls = "status-on" if estados_switches_z[3] else "status-off"
    zhf_txt = "ACTIVO" if estados_switches_z[3] else "INACTIVO"
    home_z_cls = "status-on" if home_z_detectado else "status-off"
    home_z_txt = "DETECTADO" if home_z_detectado else "NO"
    
    # Mensajes I2C
    mensajes_esclavo = "<br>".join(i2c_mensajes_esclavo[-3:]) if i2c_mensajes_esclavo else "No hay mensajes"
    esperando_respuesta = "SÍ" if i2c_esperando_respuesta else "NO"
    
    # Formatear HTML - LISTA COMPLETA DE PARÁMETROS
    html = HTML % (
        # Temperaturas PT100 (3 parámetros)
        temperaturas_pt100[0], temperaturas_pt100[1], temperaturas_pt100[2],
        
        # Estado del sistema (6 parámetros)
        nextion_class, estado_nextion,
        sistema_class, estado_sistema,
        i2c_class, i2c_estado,
        
        # Memoria y paquetes (2 parámetros)
        free_mem, i2c_paquetes_enviados,
        
        # Eje X (10 parámetros)
        xl0_cls, xl0_txt,
        xlf_cls, xlf_txt,
        xh0_cls, xh0_txt,
        xhf_cls, xhf_txt,
        home_x_cls, home_x_txt,
        
        # Eje Y (10 parámetros)
        yl0_cls, yl0_txt,
        ylf_cls, ylf_txt,
        yh0_cls, yh0_txt,
        yhf_cls, yhf_txt,
        home_y_cls, home_y_txt,
        
        # Eje Z (10 parámetros)
        zl0_cls, zl0_txt,
        zlf_cls, zlf_txt,
        zh0_cls, zh0_txt,
        zhf_cls, zhf_txt,
        home_z_cls, home_z_txt,
        
        # Comunicación I2C (4 parámetros)
        i2c_estado, len(i2c_comandos_pendientes), esperando_respuesta, mensajes_esclavo,
        
        # Diagnóstico PT100 (6 parámetros)
        adc_values[0], voltajes_pt100[0],
        adc_values[1], voltajes_pt100[1],
        adc_values[2], voltajes_pt100[2]
    )
    
    return "HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + html

def handle_request(conn):
    """Manejador de solicitudes HTTP solo visualización"""
    try:
        # Leer solicitud de forma mínima
        request = conn.recv(1024).decode('latin-1')
        first_line = request.split('\r\n')[0]
        parts = first_line.split()
        
        if len(parts) < 2:
            conn.close()
            return
        
        method, path = parts[0], parts[1]
        
        # Solo manejar GET requests
        if method == 'GET':
            if path == '/':
                # Generar página principal de visualización
                response = generar_pagina_principal()
                conn.send(response.encode('utf-8'))
                
            elif path.startswith('/i2c'):
                # Manejar comandos I2C
                if 'command=' in path:
                    command = path.split('command=')[1].split('&')[0]
                    response_text = send_i2c_command(command)
                    response = "HTTP/1.0 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n" + response_text
                    conn.send(response.encode('utf-8'))
                else:
                    conn.send("HTTP/1.0 400 Bad Request\r\n\r\nNo command specified".encode('utf-8'))
                    
            else:
                # Página no encontrada
                conn.send("HTTP/1.0 404 Not Found\r\n\r\nPage not found".encode('utf-8'))
        else:
            # Método no permitido
            conn.send("HTTP/1.0 405 Method Not Allowed\r\n\r\nMethod not allowed".encode('utf-8'))
            
    except Exception as e:
        print(f"Error en handle_request: {e}")
        try:
            conn.send("HTTP/1.0 500 Internal Server Error\r\n\r\nServer error".encode('utf-8'))
        except:
            pass
    finally:
        try:
            conn.close()
        except:
            pass
        gc.collect()

def manejar_servidor_web(timer):
    """Manejador del servidor web más robusto"""
    try:
        conn, addr = sock.accept()
        print(f"Conexión aceptada de {addr}")
        handle_request(conn)
    except OSError as e:
        # Errores normales cuando no hay conexiones pendientes
        if e.args[0] not in [11, 110]:  # EAGAIN, ETIMEDOUT
            print(f"Error aceptando conexión: {e}")
    except Exception as e:
        print(f"Error inesperado en manejar_servidor_web: {e}")
    finally:
        gc.collect()

# ========== CONFIGURACIÓN SERVIDOR WEB ROBUSTA ==========
sock = None
servidor_activo = False

def liberar_puerto_80():
    """Intenta liberar el puerto 80 que pueda estar en uso"""
    global sock
    try:
        # Intentar cerrar cualquier socket existente
        if sock:
            sock.close()
            sock = None
            print("Socket anterior cerrado")
        
        # Crear un socket temporal para liberar el puerto
        temp_sock = socket.socket()
        temp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        temp_sock.bind(('0.0.0.0', 80))
        temp_sock.close()
        print("Puerto 80 liberado temporalmente")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"No se pudo liberar puerto 80: {e}")
        return False

def iniciar_servidor_web_con_reintentos(max_intentos=3):
    """Inicia el servidor web con múltiples intentos y manejo de errores"""
    global sock, servidor_activo
    
    for intento in range(max_intentos):
        try:
            print(f"Intento {intento + 1} de iniciar servidor web...")
            
            # Liberar puerto en cada intento
            liberar_puerto_80()
            
            # Crear nuevo socket
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(addr)
            sock.listen(3)
            sock.setblocking(False)
            
            servidor_activo = True
            print("✅ Servidor web iniciado correctamente en puerto 80")
            return True
            
        except OSError as e:
            if e.args[0] == 112:  # EADDRINUSE
                print(f"❌ Puerto 80 en uso, intento {intento + 1} fallido")
                if intento < max_intentos - 1:
                    print("Esperando 3 segundos antes de reintentar...")
                    time.sleep(3)
                    continue
                else:
                    print("❌ No se pudo iniciar servidor después de varios intentos")
                    return False
            else:
                print(f"❌ Error OSError iniciando servidor: {e}")
                return False
        except Exception as e:
            print(f"❌ Error inesperado iniciando servidor: {e}")
            return False
    
    return False

def manejar_servidor_web(timer):
    """Manejador del servidor web con mejor manejo de errores"""
    global sock, servidor_activo
    
    if not servidor_activo or sock is None:
        return
    
    try:
        conn, addr = sock.accept()
        print(f"📡 Conexión aceptada de {addr}")
        handle_request(conn)
    except OSError as e:
        # Errores normales cuando no hay conexiones pendientes
        if e.args[0] not in [11, 110, 112]:  # EAGAIN, ETIMEDOUT, EADDRINUSE
            print(f"⚠️  Error aceptando conexión: {e}")
            # Si hay error crítico, marcar servidor como inactivo
            if e.args[0] == 112:  # EADDRINUSE
                servidor_activo = False
                print("🔴 Servidor marcado como inactivo por EADDRINUSE")
    except Exception as e:
        print(f"⚠️  Error inesperado en manejar_servidor_web: {e}")
    finally:
        gc.collect()

def cerrar_servidor_web():
    """Cierra el servidor web de forma segura"""
    global sock, servidor_activo
    try:
        servidor_activo = False
        if sock:
            sock.close()
            sock = None
            print("🔴 Servidor web cerrado correctamente")
    except Exception as e:
        print(f"Error cerrando servidor: {e}")

# ========== FUNCIÓN PRINCIPAL MEJORADA ==========
def main():
    print("=== SISTEMA ESP32 MASTER - SOLO VISUALIZACIÓN ===")
    print("Servidor Web (solo visualización) + Nextion + Sensores + I2C")
    print(f"Memoria inicial: {gc.mem_free()} bytes")
    
    # Inicializar I2C
    print("Inicializando I2C Master...")
    if not init_i2c_master():
        print("Error: No se pudo inicializar I2C")
        return
    
    # Escanear dispositivos I2C
    scan_i2c()
    
    # Inicializar Nextion
    print("Inicializando Nextion...")
    inicializar_nextion()
    
    # Inicializar servidor web SOLO VISUALIZACIÓN
    servidor_iniciado = False
    if ap and ap.active():
        print("🌐 Intentando iniciar servidor web...")
        servidor_iniciado = iniciar_servidor_web_con_reintentos(3)
        
        if servidor_iniciado:
            timer_servidor.init(period=200, mode=Timer.PERIODIC, callback=manejar_servidor_web)
            print("✅ Servidor web de visualización iniciado y configurado")
        else:
            print("❌ Servidor web no disponible - Continuando sin interfaz web")
    else:
        print("⚠️  WiFi no disponible - Continuando sin interfaz web")
    
    # Configurar timer principal
    timer_principal.init(period=100, mode=Timer.PERIODIC, callback=tarea_principal_combinada)
    
    # Limpiar memoria
    gc.collect()
    print(f"📊 Memoria libre: {gc.mem_free()} bytes")
    
    print("\n🎯 Sistema listo!")
    if servidor_iniciado:
        print("🌐 Interfaz web: http://" + ap.ifconfig()[0])
    print("📟 Nextion operativa")
    print("🔗 I2C Master activo")
    print("📊 Monitoreo de sensores activo")
    
    # Bucle principal optimizado con monitoreo del servidor
    try:
        contador_memoria = 0
        contador_verificacion_servidor = 0
        
        while True:
            time.sleep(0.1)
            contador_memoria += 1
            contador_verificacion_servidor += 1
            
            # Liberar memoria cada 2 segundos
            if contador_memoria % 20 == 0:
                gc.collect()
            
            # Verificar estado del servidor cada 10 segundos
            if contador_verificacion_servidor >= 100:  # 10 segundos
                contador_verificacion_servidor = 0
                if servidor_iniciado and not servidor_activo:
                    print("🔄 Reintentando iniciar servidor web...")
                    servidor_iniciado = iniciar_servidor_web_con_reintentos(1)
                    if servidor_iniciado:
                        print("✅ Servidor web recuperado")
                
    except KeyboardInterrupt:
        print("\n🔄 Apagando sistema...")
        timer_principal.deinit()
        timer_servidor.deinit()
        timer_nextion.deinit()
        cerrar_servidor_web()
        if ap:
            ap.active(False)
        send_cmd('t4.txt="Sistema APAGADO"')
        print("✅ Sistema apagado correctamente")

if __name__ == "__main__":
    main()