#-------------------------------------------------------------------------------------
#                              CÓDIGO DEL CLIENTE
#-------------------------------------------------------------------------------------

#Nota 1: este programa está diseñado para interactuar con el usuario, ya que una vez eje-
    #cutado, se mostrará por pantalla el protocolo con el que se quiera transmitir y, a
    #continuación, habrá que elegir el modo de transmisión (con o sin confirmación).
#Debido a que este programa no interactúa directamente con el hardware, sino que es con-
    #trolado por el sistema operativo, hay que asegurarse de que las conexiones de WiFi,
    #Bluetooth y puerto serie estén establecidas antes de ejecutar el programa.

#Nota 2: para que el programa funcione correctamente, el archivo "protocolos_comunicacion.py"
    #tiene que estar en la misma carpeta, tanto del servidor como del cliente.

#Nota 3: este programa está diseñado para ejecutarse en GNU/Linux, sin embargo, hay al-
    #gunas distribuciones de linux que no soportan Bluetooth mediante la librería Socket.
    #Por lo tanto, existe la clase Bluetooth_Rasp (diseñada originalmente para Raspberry)
    #que utiliza la librería PyBluez y, en estos casos, al llamar a Bluetooth, usar esta
    #clase.



#!/usr/bin/env python3
from protocolos_comunicacion import *
import time
from time import sleep
from datetime import datetime
import threading
import struct
import pandas as pd

class PausaContador(Exception):
    pass
class ConexionLenta(Exception):
    pass
class PaquetesFaltantes(Exception):
    pass
class ConexionInestable(Exception):
    pass
class MejorarConexion(Exception):
    pass

def ping(preferido):
    global protocolo
    global BUFFER_SIZE
    global client_socket
    contar_Wifi = 0
    contar_Bt = 0
    contar_Rfd = 0
    global cerrar_conexion
    cerrar_conexion = False
    while True:        
        if preferido == Wifi:
            try:                   
                ping = Wifi.ping('10.3.141.1', 65432, 4)
                if ping > 500:
                    raise ConexionLenta ("Conexión lenta")
                sleep(1)
                #protocolo = Wifi
                #BUFFER_SIZE = 100000        #con 200000 da error de paquete
                BUFFER_SIZE = 400
                print("Wifi disponible") 
                client_socket = Wifi.conectar_cliente('10.3.141.1', 65432)                 
                return Wifi
            except ConexionLenta:
                print("Conexion lenta")
                contar_Wifi += 1
            except:
                print("Wifi no disponible")
                contar_Wifi += 1                
                sleep(0.5)
                if (contar_Wifi > 3) and (contar_Bt > 3) and (contar_Rfd > 3):
                    cerrar_conexion = True
                    return Wifi
                
                if contar_Wifi > 3 and contar_Bt < 3:
                    preferido = Bluetooth
                elif contar_Wifi > 3:
                    preferido = RFD                    
                    

        elif preferido == Bluetooth:
            try:                
                ping = Bluetooth.ping('DC:A6:32:DB:05:6E', 1, 4)
                if ping > 500:
                    raise ConexionLenta ("Conexión lenta")
                sleep(1)
                #protocolo = Bluetooth
                BUFFER_SIZE = 400
                #BUFFER_SIZE = 400 
                print("Bluetooth disponible")
                try:
                    client_socket = Bluetooth.conectar_cliente('DC:A6:32:DB:05:6E', 1)
                except:
                    sleep(1)
                    client_socket = Bluetooth.conectar_cliente('DC:A6:32:DB:05:6E', 1)            
                return Bluetooth
            except ConexionLenta:
                contar_Bt += 1
                print("Conexion lenta")
            except Exception as a:
                print(f"Bluetooth no disponible, {a}")
                contar_Bt += 1                
                sleep(0.5)
                if (contar_Wifi > 3) and (contar_Bt > 3) and (contar_Rfd > 3):
                    cerrar_conexion = True
                    return Bluetooth
                
                if contar_Bt > 3 and contar_Wifi < 3:
                    preferido = Wifi
                elif contar_Bt > 3:
                    preferido = RFD
    
        elif preferido == RFD:    
            try:
                ping = RFD.ping("/dev/ttyUSB0", 4)
                if ping > 1000:
                    raise ConexionLenta ("Conexión lenta")
                #sleep(1)
                BUFFER_SIZE = 400 
                print("RFD disponible")
                client_socket = RFD.conectar_cliente("/dev/ttyUSB0")
                return RFD
            except ConexionLenta:
                preferido = Wifi
                print("Conexion lenta")
            except:
                print('RFD no disponible')
                contar_Rfd += 1                
                sleep(0.5)
                if (contar_Wifi > 3) and (contar_Bt > 3) and (contar_Rfd > 3):
                    cerrar_conexion = True
                    return RFD
                
                if contar_Rfd > 3 and contar_Wifi < 3:
                    preferido = Wifi
                elif contar_Rfd > 3:
                    preferido = Bluetooth

        else:
            try:                
                Bluetooth.ping('DC:A6:-:-:-:-', 1, 4)                           #se ha ocultado la dirección MAC por privacidad
                sleep(1)
                #protocolo = Bluetooth
                #BUFFER_SIZE = 5000
                BUFFER_SIZE = 400 
                print("Bluetooth disponible")
                client_socket = Bluetooth.conectar_cliente('DC:A6:-:-:-:-', 1)  #se ha ocultado la dirección MAC por privacidad
                return Bluetooth
            except:
                print("Bluetooth no disponible")
                sleep(0.5)
            
            try:                   
                ping = Wifi.ping('10.3.141.1', 65432, 4)
                if ping > 200:
                    raise Exception ("Conexión lenta")
                sleep(1)
                #protocolo = Wifi
                #BUFFER_SIZE = 100000        #con 200000 da error de paquete
                BUFFER_SIZE = 400
                print("Wifi disponible") 
                client_socket = Wifi.conectar_cliente('10.3.141.1', 65432)                 
                return Wifi
            except:
                print("Wifi no disponible")
                sleep(0.5)
            

            try:
                RFD.ping("/dev/ttyUSB0", 4)
                sleep(1)
                BUFFER_SIZE = 400 
                print("RFD disponible")
                client_socket = RFD.conectar_cliente("/dev/ttyUSB0")
                return RFD
            except:
                print('RFD no disponible')
                sleep(0.5)              
            
        sleep(0.2)
        

print("Elige el modo de transmisión: ")
print("1: Sin confirmación\n2: Con confirmación")
transmision = input()
print("Elige el protocolo preferido: ")
print("1: WiFi\n2: Bluetooth\n3: RFD\n4: Todos" )
elegir = input()
if elegir == "1":
    protocolo = ping(Wifi)
elif elegir == "2":
    protocolo = ping(Bluetooth)
elif elegir == "3":
    protocolo = ping(RFD)
else:
    protocolo = ping(any)
    print("Any")

print(f"Conectando a {protocolo}")

excepcion_ping = False
def contador():                 #función contador para comprobar conexión cada 20" en el modo "sin confirmación"         
    global excepcion_ping
    sleep(20)
    excepcion_ping = True

protocolo_conectar = None
def mejorar_conexion():         #función que busca mejores conexiones en el modo "con confirmación"
    global protocolo_conectar
    while not protocolo_conectar:
        sleep(10)
        if protocolo == RFD:
            try:
                comprobar_ping = Wifi.ping('10.3.141.1', 65432, 4)
                if comprobar_ping < 200:
                    protocolo_conectar = Wifi
                else:
                    protocolo_conectar = None
                if not protocolo_conectar:
                    comprobar_ping = Bluetooth.ping('DC:A6:32:DB:05:6E', 1, 4)                    
                    if comprobar_ping < 200:
                        protocolo_conectar = Bluetooth
                    else:
                        protocolo_conectar = None
            except:
                print("Mejorar conexión: RFD no puede mejorarse")
        else:
            pass
                
def convert_timestamp(ts):          #Stack overflow
    dt_object = datetime.fromtimestamp(ts) 
    return dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


global t_total
global start_time
global total_data
t_total = 1500
start_time = None
global t_packet
t_packet = 0
err_pack = None
fallos = 0
global señal
señal = None
global tasa_fallos_calculados
tasa_fallos_calculados = 0
paquete_inicial = 0


def analizador_paquete(packet):             #analiza cada paquete para buscar la trama que finaliza la conexión
    for i in range(len(packet) - 1):
        if len(packet[i:i+4]) < 4:
            return None
        elif struct.unpack('i', packet[i:i+4])[0] == 1111111111:
            print("Recepción completada")
            return True
        else:
            return None
        
def analizador_paquete_sc(packet):
    for i in range(len(packet) - 1):
        if len(packet[i:i+4]) < 4:
            return None, None, None
        elif struct.unpack('i', packet[i:i+4])[0] == 1111111111:
            print("Recepción completada")
            ident = struct.unpack('i', packet[i+4:i+8])[0]
            fallos_recibidos = struct.unpack('i', packet[i+8:i+12])[0]
            return True, ident, fallos_recibidos
        else:
            return None, None, None

def buscador_error(lista, rango):
    ultimos_paquetes = lista[-rango:]                   #cogemos los últimos 5 paquetes recibidos
    pequeño = min(ultimos_paquetes)
    grande = max(ultimos_paquetes)    
    todos_numeros = set(range(pequeño, grande + 1))     #creamos un conjunto de todos los paquetes que deberían haber llegado en el rango
    if reenvio_paq:
        nuevos_numeros = [num for num in reenvio_paq if num <= grande]
        nuevos_numeros = nuevos_numeros[-rango:]
        todos_numeros = set(nuevos_numeros)
    conjunto_lista = set(ultimos_paquetes)              #creamos un conjunto de los paquetes que han llegado
    errores = list(todos_numeros - conjunto_lista)      #creamos una lista con los paquetes que faltan
    tasa_error = len(errores) / (grande - pequeño + 1)  #calculamos tasa de error
    if len(ultimos_paquetes) < rango:
        tasa_error = 0
    print(f"Tasa de error hilo: {tasa_error}")
    return tasa_error
    
def hiloRecepcion():
    #Como el paquete recibido de vuelta tiene 8 bytes mas, aumentamos el buffer de recepcion
    BUFFER_SIZE_RX = 16
    global lista_tiempos
    lista_tiempos = []
    global tiempo_actual
    tiempo_actual = []
    global lista_identificador
    lista_identificador = []
    tiempo_total = []
    packet_end = None
    identificador1 = []
    p = 0
    fallos_calculados = 0
    fallos_totales = []
    tasa_fallos_calculados2 = []
    global err_pack
    global identificador
    global fallos
    global tasa_fallos_calculados
    global tasa_fallos
    tasa_fallos = 0
    global lista_tasa_fallos
    lista_tasa_fallos = []
    hilo1 = None
    timeout_errors = 0
    try:
        while True:
            no_paq = 0
            if err_pack:
                break
            response_packet = protocolo.recibir(client_socket, BUFFER_SIZE_RX)
            while not response_packet:
                sleep(0.1)
                no_paq += 1
                print(f"No_paq = {no_paq}")
                response_packet = protocolo.recibir(client_socket, BUFFER_SIZE_RX)
                if no_paq > 5:        
                    print(f"Fallo de recepción, tam paq: {len(response_packet)}")
                    break
            if analizador_paquete(response_packet):
                break

            #Completamos el tamaño del paquete para que todos sean iguales
            while len(response_packet) < (BUFFER_SIZE_RX):
                print("Paquete pequeño")
                remaining_bytes = BUFFER_SIZE_RX - len(response_packet)
                additional_packet = protocolo.recibir(client_socket, remaining_bytes)
                #Si no hay paquetes adicionales, siginifica que se ha terminado de recibir
                if not additional_packet:
                    print("Se ha terminado de recibir")
                    break
                if additional_packet == b'0':
                    print("Se ha terminado de recibir")
                    packet_end = b'0'
                    break
                response_packet += additional_packet
            if err_pack:
                break
            #Imprimimos los paquetes recibidos del servidor
            tiempo_fin = time.time()
            check_sum = sum(struct.unpack_from("6H", response_packet))
            print(f'Checksum: {check_sum}')
            tiempo = struct.unpack('d', response_packet[0:8])            
            tiempo = float(tiempo[0])               #Se pone para quitar la coma que aparece al hacer print
            global t_total
            t_total  = (tiempo_fin-tiempo)*1000     #Pasamos a ms
            
            v_transfer = len(response_packet) / t_total *1000
            identificador = struct.unpack('i', response_packet[8:12])[0]
            identificador1.append(identificador)
            fallos = struct.unpack('i', response_packet[12:16])[0]
            if err_pack:
                break
            
            print(f'Paquete recibido. T: {t_total} ms, I: {identificador} Len: {len(response_packet)}, Vel: {v_transfer/1000000} MB/s, Fallos: {fallos}')
            tiempo_actual.append(tiempo_fin)
            lista_tiempos.append(t_total)
            lista_identificador.append(identificador)
            tasa_fallos = buscador_error(lista_identificador, 5)
            lista_tasa_fallos.append(tasa_fallos)
            fallos_calculados = identificador - p
            fallos_totales.append(fallos_calculados)
            if identificador == 0:
                identificador = 1            
            tasa_fallos_calculados = fallos / (identificador)             
            tasa_fallos_calculados2.append(tasa_fallos_calculados)
            p += 1
            if packet_end == b'0': 
                print("Packet = 0")
                break 
    except TimeoutError:
        timeout_errors += 1
        print(f'Timeout errors: {timeout_errors}')

    end_time = time.time()
    tiempo_total.append(end_time - start_time)
    global tiemp_total
    tiemp_total = end_time - start_time
    return


#Función para agregar encabezado a cada paquete
def agregar_encabezado(packet, num_paquete):
    #Agregamos el time_stamp y número de paquete al encabezado
    time_stamp = time.time()
    print(time_stamp)
    header_t = struct.pack('d', time_stamp)
    header_i = struct.pack('i', num_paquete)
    header_d = struct.pack('i', 2147483647)     #4 bytes de solo 1. Indica que inmediatamente después está el ident.
    # if num_paquete % 2 != 0 and num_paquete < 6:  #cuando llegue un paquete erróneo, que lo descarte el servidor y lo vuelva a pedir al cliente
    #     header_d = b'\xff\xff\xff\x3a'
    #     print("Error provocado")
    #print(f'T: {header_t}, I: {header_i}')
    header = header_d + header_t + header_i
    print(f'Len: {len(header)}')
    return header + packet	
    
def comprobar_velocidad(delay):
    global t_packet
    if t_packet > delay:
        t_packet = 0
    t_packet = (delay-t_packet)*0.0012
    return t_packet

def buscar_paquetes(lista, valor_max):
    todos_numeros = set(range(1, valor_max + 1))
    conjunto_lista = set(lista)
    faltantes = list(todos_numeros - conjunto_lista)
    return faltantes

def bucle_principal_sc(initial_packet):
    global packets  
    global start_time
    global total_data
    global identificador
    global excepcion_ping
    
    #Enviamos el tamaño del buffer al servidor
    send_buffer = struct.pack('i', BUFFER_SIZE) #la i indica entero de 4 bytes
    print(len(send_buffer))
    protocolo.enviar(client_socket, send_buffer)
    print("\n")

    #Leemos los bytes del archivo
    #nombre_archivo = 'nasa2.jpg'
    nombre_archivo = '4k.mp4'
    with open(nombre_archivo, 'rb') as file:
        data = file.read()
    print(f'Tamaño archivo: {len(data)} bytes')
    tam_data = struct.pack('i', len(data))
    total_data = data

    #Dividimos los bytes en paquetes de tamaño del buffer
    packets = [data[i:i+BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
    print(f'Enviar: {len(packets) - initial_packet} paquetes')

    #Enviamos los paquetes al servidor
    for i, packet in enumerate(packets, start = initial_packet):
        #Agregamos el time_stamp y el número de paquete al encabezado            
        packet_with_header = agregar_encabezado(packet, i)        
        print(f'Paquete enviado nº: {i}, len: {len(packet_with_header)}')
        protocolo.enviar(client_socket, packet_with_header)
        if not start_time:
            start_time = time.time()
        t_packet = 0.001
        sleep(t_packet)
        print(f'Delay apropiado: {t_packet}')
        print(f"i: {i}, initial packet: {initial_packet}")
        
        if i >= len(packets)-1:
            print("Argumento compartido true")
            header_d = struct.pack('i', 1111111111)
            sleep(1)
            protocolo.enviar(client_socket, header_d)
            print("Enviado")
            packet = protocolo.recibir(client_socket, 12)
            no_paq = 0
            while not packet:
                no_paq += 1
                print("Paquete confirmacion vacio")
                sleep(0.1)
                protocolo.enviar(client_socket, header_d)
                sleep(0.1)
                packet = protocolo.recibir(client_socket, 12)
                if no_paq > 10:
                    print("Confirmación no recibida")
                    break

            print(f"Longitud paquete: {len(packet)}")
            confirmacion, ident, fallos_recibidos = analizador_paquete_sc(packet)
            
            no_paq = 0
            while not confirmacion:
                no_paq += 1
                print("No confirmación")
                sleep(0.1)
                packet = protocolo.recibir(client_socket, 12)
                confirmacion, ident, fallos_recibidos = analizador_paquete_sc(packet)
                if no_paq > 10:
                    print("Confirmación no recibida")
                    break
                
            if confirmacion:
                print(f"Nº paquetes recibidos por el servidor: {ident}\nErrores: {fallos_recibidos}")

        print(f'Identificador: {i}')
        identificador = i
        if excepcion_ping:
            excepcion_ping = False
            protocolo.cerrar_conexion_cliente(client_socket)
            sleep(1)
            raise PausaContador ("Comprobar conexión")
    
def bucle_principal(initial_packet, reenvio_paq, iteracion):
    global packets
    global hilo    
    global start_time
    global total_data
    global identificador
    hilo1 = None
    k = None

    #Enviamos el tamaño del buffer al servidor
    send_buffer = struct.pack('i', BUFFER_SIZE) #la i indica entero de 4 bytes
    print(len(send_buffer))
    protocolo.enviar(client_socket, send_buffer)
    print("\n")

    #Leemos los bytes del archivo
    nombre_archivo = 'paisaje.jpg'
    with open(nombre_archivo, 'rb') as file:
        data = file.read()
    print(f'Tamaño archivo: {len(data)} bytes')
    tam_data = struct.pack('i', len(data))
    total_data = data

    #Dividimos los bytes en paquetes de tamaño del buffer
    packets = [data[i:i+BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
    print(f'Enviar: {len(packets) - initial_packet} paquetes')
    n_paquetes = struct.pack('h', len(packets) - initial_packet)
    protocolo.enviar(client_socket, n_paquetes)
    protocolo.enviar(client_socket, tam_data)
    long_archivo = struct.pack('B', len(nombre_archivo))
    protocolo.enviar(client_socket, long_archivo)       #Enviamos el nº de caracteres del archivo
    nombre_archivo = nombre_archivo.encode()
    protocolo.enviar(client_socket, nombre_archivo)

    #Iniciamos el hilo de recepción
    hilo = threading.Thread(target=hiloRecepcion, args=())  
    hilo.start()    
    #Enviamos los paquetes al servidor
    if not reenvio_paq:
        for i, packet in enumerate(packets, start = initial_packet):    
            #Agregamos el time_stamp y el número de paquete al encabezado
            if err_pack:
                print("Fin bucle principal")
                break        
            packet_with_header = agregar_encabezado(packet, i)
            print(f'Paquete enviado nº: {i}, len: {len(packet_with_header)}, {protocolo}')
            protocolo.enviar(client_socket, packet_with_header)
            if not start_time:
                start_time = time.time()
            t_packet = comprobar_velocidad(t_total)
            sleep(t_packet)
            print(f'Delay apropiado: {t_packet}')
            print(f"i: {i}, initial packet: {initial_packet}")
            tasa_fallos_recibidos = fallos/(i+1)
            print(f"Tasa de fallos: {tasa_fallos_recibidos}")
            if not k:
                k = 0
            if señal:
                identificador = i
                protocolo.cerrar_conexion_cliente(client_socket)
                print("Protocolo conexion cerrado")
            
            if i >= len(packets)-1:  
                print("Argumento compartido true")
                header_d = struct.pack('i', 1111111111)
                sleep(1)
                protocolo.enviar(client_socket, header_d)
                sleep(1)
                confirmacion = protocolo.recibir(client_socket, 4)
                no_paq = 0
                while not analizador_paquete(confirmacion):
                    no_paq += 1
                    sleep(0.1)
                    confirmacion = protocolo.recibir(client_socket, 4)
                    if no_paq > 10:
                        print("Confirmación no recibida")
                        break
                print("Confirmación recibida")
                break
            print(f'Identificador: {i}')
            identificador = i
            
            if not lista_tasa_fallos:       #evita el error max() arg empty
                if max(lista_tasa_fallos) > 0.4 and iteracion == 0:
                    break
            if not hilo.is_alive():
                break
            if protocolo_conectar:
                    print("PArando bucle")
                    break
    else:
        for i, packet in enumerate(packets, start = min(reenvio_paq)):
            if i in reenvio_paq:
                #Agregamos el time_stamp y el número de paquete al encabezado
                if err_pack:
                    print("Fin bucle principal")
                    break        
                packet_with_header = agregar_encabezado(packet, i)
                print(f'Paquete enviado nº: {i}, len: {len(packet_with_header)}, {protocolo}')
                protocolo.enviar(client_socket, packet_with_header)
                if not start_time:
                    start_time = time.time()
                t_packet = comprobar_velocidad(t_total)
                sleep(t_packet)
                print(f'Delay apropiado: {t_packet}')
                print(f"i: {i}, initial packet: {initial_packet}")
                tasa_fallos_recibidos = fallos/(i+1)
                print(f"Tasa de fallos: {tasa_fallos_recibidos}")
                if not k:
                    k = 0
                if señal:
                    identificador = i
                    protocolo.cerrar_conexion_cliente(client_socket)
                    print("Protocolo conexion cerrado")
                
                if i >= len(packets)-1:  
                    print("Argumento compartido true")
                    header_d = struct.pack('i', 1111111111)
                    sleep(1)
                    protocolo.enviar(client_socket, header_d)
                    sleep(1)
                    confirmacion = protocolo.recibir(client_socket, 4)
                    no_paq = 0
                    while not analizador_paquete(confirmacion):
                        no_paq += 1
                        sleep(0.1)
                        confirmacion = protocolo.recibir(client_socket, 4)
                        if no_paq > 10:
                            print("Confirmación no recibida")
                            break
                        
                    
                    print("Confirmación recibida")
                    break
                print(f'Identificador: {i}')
                identificador = i                
                if lista_tasa_fallos:                           #evita el error max() arg empty
                    if max(lista_tasa_fallos) > 0.4 and iteracion == 0:
                        break
                
                if not hilo.is_alive():
                    break

                if protocolo_conectar:
                    print("PArando bucle")
                    break

iteracion = 0
reenvio_paq = []
identificador_total = []
lista_tiempo_actual = []
delay = []
lista_iteracion = []
tasa_fallos_total = []
lista_protocolos = []
tiempo_inicial = None
while True:     
    try:
        if transmision == "1":
            if cerrar_conexion:
                if start_time:
                    end_time = time.time()
                    tiempo_total = []
                    tiempo_total.append(end_time - start_time)
                    tiempo_inicial = []
                    tiempo_inicial.append(start_time)
                    lista_iteracion.append(identificador)
                    tam_paquetes = []
                    tam_paquetes.append(identificador*BUFFER_SIZE/8000)
                    data = {
                        "Tiempo inicial" : start_time,
                        "Tiempo total:" : tiempo_total,                        
                        "Último paquete enviado": lista_iteracion,
                        "Tamaño enviado (KB)" : tam_paquetes
                    }
                # Exportamos los datos a un archivo CSV
                archivo = pd.DataFrame(data)
                titulo = f"Paquetes de {BUFFER_SIZE} bytes"
                hora_actual = time.time()
                archivo.to_csv(f"Sin confirmacion,{protocolo},{titulo},{hora_actual}.csv", index=False, header=True)
                break
            paquete = b'1'*4
            protocolo.enviar(client_socket, paquete + b'0'*28)
            prueba = protocolo.recibir(client_socket, 32)            
            hilo_contador = threading.Thread(target=contador)
            hilo_contador.daemon = True
            hilo_contador.start()
            bucle_principal_sc(paquete_inicial)
            protocolo.cerrar_conexion_cliente(client_socket)
            print("Protocolo conexion cerrado")
            break
        else:
            if not cerrar_conexion:
                paquete = b'1'*8
                protocolo.enviar(client_socket, paquete + b'0'*24)
                prueba = protocolo.recibir(client_socket, 32)
                if not tiempo_inicial:
                    tiempo_inicial = time.time()
                hilo_mejorar = threading.Thread(target=mejorar_conexion)
                hilo_mejorar.daemon = True
                hilo_mejorar.start()
                bucle_principal(paquete_inicial, reenvio_paq, iteracion)                
                hilo.join()                                                     #Esperamos a que el hilo termine                
                identificador_total.extend(lista_identificador)
            lista_tiempo_actual.extend(tiempo_actual)
            delay.extend(lista_tiempos)            
            lista_iteracion.extend([iteracion+1] * len(lista_identificador))    #ponemos iteración + 1 para que empiece a contar en 1
            lista_protocolos.extend([protocolo] * len(lista_identificador))
            print(f"Paquetes almacenados: {identificador_total}")
            tasa_fallos_total.extend(lista_tasa_fallos)
            reenvio_paq = buscar_paquetes(identificador_total, len(packets) - 1)
            if protocolo_conectar:
                    raise MejorarConexion
            if lista_tasa_fallos:           #evita el error max() arg empty
                if max(lista_tasa_fallos[-5:]) > 0.4:
                    raise ConexionInestable
            if not cerrar_conexion:
                if reenvio_paq:
                    raise PaquetesFaltantes
            try:
                protocolo.cerrar_conexion_cliente(client_socket)
            except OSError as e:            #Evita error que daba a veces al desconectarse el protocolo antes de tiempo
                print(f"Manejando la excepcion: {e}")

            tiempo_final = time.time()
            if tiempo_inicial:
                tiempo_total = tiempo_final - tiempo_inicial
                velocidad_media = len(packets) / tiempo_total / 1000
            else:
                tiempo_total = 0
                velocidad_media = 0
            if not lista_tasa_fallos:
                tasa_fallos_total = 0
            print("Protocolo conexion cerrado")
            lista_tiempo_actual1 = [convert_timestamp(ts) for ts in lista_tiempo_actual]
            print(f"Lista iteracion: {lista_iteracion}")
            print(f"Lista tasa fallos: {tasa_fallos_total}")
            data = {
                "Ping (ms)": delay,
                "Identificador": identificador_total,
                "Iteración" : lista_iteracion,
                "Marca de tiempo" : lista_tiempo_actual1,
                "Tasa de fallos": tasa_fallos_total,
                "Tiempo total (s)": tiempo_total,
                "Velocidad de transferencia media (kb/s)": velocidad_media,
                "Protocolo": lista_protocolos
            }
            # Exportamos los datos a un archivo CSV
            archivo = pd.DataFrame(data)
            titulo = f"Paquetes de {BUFFER_SIZE} bytes"
            hora_actual = time.time()
            hora_actual = convert_timestamp(hora_actual)
            archivo.to_csv(f"{lista_protocolos[0]},{titulo},{hora_actual}.csv", index=False, header=True)
            break
    except PaquetesFaltantes:
        print("Paquetes faltantes")
        iteracion += 1
        paquete_inicial = min(reenvio_paq)
        protocolo.cerrar_conexion_cliente(client_socket)
        sleep(1)
        protocolo = ping(protocolo)

    except PausaContador:                   #ping en modo sin confirmación para comprobar conexión
        print("Ping para comprobar conexión")
        paquete_inicial = identificador
        protocolo = ping(protocolo)

    except ConexionInestable:               #supera la tasa de fallos establecida 
        print("Superado límite de tasa de fallos")
        iteracion += 1
        paquete_inicial = identificador
        protocolo = ping(protocolo)         #pongo ping a protocolo para que no cambie al hacer las pruebas
        print(f"Conectando a {protocolo}")
        lista_tasa_fallos = []
        #print(f"Reenvio paq: {reenvio_paq}")

    except MejorarConexion:        
        paquete_inicial = identificador
        protocolo = protocolo_conectar
        protocolo_conectar = None
        iteracion += 1
        print(f"Mejorando la conexión a: {protocolo}")
        lista_tasa_fallos = []

    except Exception as a:                  #normalmente cuando se produce un error en el hilo recepción u otro error no contemplado
        print("Fallo de conexión. Reintentando...")
        print(f"Error: {a}")        
        print(f"Último paquete enviado: {identificador}")
        paquete_inicial = identificador
        protocolo = ping(protocolo)         #pongo ping a protocolo para que no cambie al hacer las pruebas
        print(f"Conectando a {protocolo}")
        lista_tasa_fallos = []
        