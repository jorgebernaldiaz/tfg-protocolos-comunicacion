#-------------------------------------------------------------------------------------
#                              CÓDIGO DEL SERVIDOR
#-------------------------------------------------------------------------------------

#Nota 1: este programa está diseñado para que, una vez ejecutado, permanezca a la escu-
    #cha de conexiones entrantes hasta que el usuario decida pararlo manualmente. La 
    #forma de uso recomendada es iniciar el servidor primero y después el cliente.

#Nota 2: para que el programa funcione correctamente, el archivo "protocolos_comunicacion.py"
    #tiene que estar en la misma carpeta, tanto del servidor como del cliente.

#Nota 3: este programa está diseñado para ejecutarse en GNU/Linux, sin embargo, hay al-
    #gunas distribuciones de linux que no soportan Bluetooth mediante la librería Socket.
    #Por lo tanto, existe la clase Bluetooth_Rasp (diseñada originalmente para Raspberry)
    #que utiliza la librería PyBluez y, en estos casos, al llamar a Bluetooth, usar esta
    #clase.



#!/usr/bin/env python3
from protocolos_comunicacion import *
import struct
import time
from time import sleep
import threading


def hilo_Wifi():    
    while True:
        try:
            #sleep(0.1)
            client_socket1 = Wifi.conectar_servidor('10.3.141.1', 65432)
            prueba = Wifi.recibir(client_socket1, 32)
            print("Ok recibido")
            print(len(prueba))
            Wifi.enviar(client_socket1, prueba)
            print(prueba)
            while(prueba[0:4] != b'1111'):
                prueba = Wifi.recibir(client_socket1, 32)
                print("Ok recibido")
                print(len(prueba))
                if not prueba:                   
                    Wifi.cerrar_conexion_servidor(client_socket1)
                    raise Exception("Paquete vacio")
                    
                if len(prueba) > 32:
                    Wifi.enviar(client_socket1, prueba[4:])
                else:
                    Wifi.enviar(client_socket1, prueba)
           
            protocolo = Wifi
            client_socket = client_socket1
            if prueba[4:8] == b'0000':
                bucle_principal_sc(client_socket, protocolo)
            elif prueba[4:8] == b'1111':                
                bucle_principal(client_socket, protocolo)
            print("Hilo wifi finalizado")
            global hilo1
            hilo1 = None
            break
        
        except Exception as e:
            print("WiFi no disponible")
            print(e)
            break            
            
def hilo_Bluetooth():    
    while True:
        try:            
            client_socket2 = None
            client_socket2 = Bluetooth_Rasp.conectar_servidor('-:-:-:-:-:-', 1)     #Se ha ocultado la dirección MAC por privacidad
            prueba = Bluetooth_Rasp.recibir(client_socket2, 32)
            print(prueba)
            if prueba == b'01010101':
                Bluetooth_Rasp.cerrar_conexion_servidor(client_socket2)
                print("Cerrado")
                break
            print(len(prueba))
            Bluetooth_Rasp.enviar(client_socket2, prueba)
            while(prueba[0:4] != b'1111'):
                prueba = Bluetooth_Rasp.recibir(client_socket2, 32)
                print("Ok recibido")
                print(prueba)
                if prueba == b'01010101': 
                    Bluetooth_Rasp.cerrar_conexion_servidor(client_socket2)                 
                    raise Exception("Paquete vacio")
                    
                print(len(prueba))
                if len(prueba) > 32:
                    Bluetooth_Rasp.enviar(client_socket2, prueba[4:])
                else:
                    Bluetooth_Rasp.enviar(client_socket2, prueba)
            protocolo = Bluetooth_Rasp
            client_socket = client_socket2
            if prueba[4:8] == b'0000':
                bucle_principal_sc(client_socket, protocolo)
            elif prueba[4:8] == b'1111':                
                bucle_principal(client_socket, protocolo)            
            print("Hilo bluetooth finalizado")
            global hilo2
            hilo2 = None
            break
        except Exception as e:
            print(f"Bluetooth no disponible {e}")
            if client_socket2:
                Bluetooth_Rasp.cerrar_conexion_servidor(client_socket2)
                print("Cerrado")
            sleep(1)
            
def hilo_RFD():    
    while True:
        try:           
            client_socket3 = RFD.conectar_servidor("/dev/ttyS0")
            prueba = RFD.recibir(client_socket3, 32)
            print("Ok recibido")
            print(len(prueba))
            RFD.enviar(client_socket3, prueba)
            print(prueba)
            contador = 0
            while(prueba[0:4] != b'1111'):
                prueba = RFD.recibir(client_socket3, 32)
                print("Ok recibido")
                print(len(prueba))
                if not prueba:
                    contador += 1
                    sleep(0.1)
                    if contador > 50:
                        RFD.cerrar_conexion_servidor(client_socket3)
                        raise Exception("Paquete vacio")
                        
                if len(prueba) > 32:
                    RFD.enviar(client_socket3, prueba[4:])
                else:
                    RFD.enviar(client_socket3, prueba)
           
            protocolo = RFD
            client_socket = client_socket3
            if prueba[4:8] == b'0000':
                bucle_principal_sc(client_socket, protocolo)
            elif prueba[4:8] == b'1111':                
                bucle_principal(client_socket, protocolo)
            print("Hilo RFD finalizado")
            global hilo3
            hilo3 = None
            break
        
        except Exception as e:
            print("RFD no disponible")
            print(e)
            break

def correccion_paquete(packet):         #busca el identificador de cada paquete, para identificar la cabecera del mismo
    for j in range(len(packet) - 1):
        if len(packet[j:j+4]) < 4:
            print("Longitud menor de 4")
            break
        if struct.unpack('i', packet[j:j+4])[0] == 2147483647:
            print("Se encontró el inicio del paquete")
            dolar = struct.unpack('i', packet[j:j+4])[0]
            print(f'El identificador encontrado es: {dolar}')
            identificador = 0
            return packet[j:], identificador
            break
        else:
            
            print(struct.unpack('i', packet[j:j+4])[0] , end='\r')
    packet = b''
    identificador = -1
    print("No se encontró, pedir siguiente paquete")
    return packet, identificador
            #sleep(0.1)
            
def analizador_paquete(response_packet):            #se busca la trama que manda el cliente indicando que finaliza la conexión
    for i in range(len(response_packet)-1):
        if len(response_packet[i:i+4]) < 4:            
            return None
        elif struct.unpack('i', response_packet[i:i+4])[0] == 1111111111:
            print("Recepción completada")            
            return True
        else:
            return None

def analizador_paquete_sc(response_packet):         #se busca la trama que manda el cliente indicando que finaliza la conexión
    for i in range(len(response_packet)-1):
        print("Aqui")
        if len(response_packet[i:i+4]) < 4:
            print("Devolviendo None")
            return None, None, None
        elif struct.unpack('i', response_packet[i:i+4])[0] == 1111111111:
            print("Recepción completada")
            ident = struct.unpack('i', response_packet[i+4:i+8])[0]
            fallos_recibidos = struct.unpack('i', response_packet[i+8:i+12])[0] #en este mensaje también se incluyen los fallos para llevar el conteo en el modo sin confirmacion
            return True, ident, fallos_recibidos
        else:
            return None, None, None

def bucle_principal_sc(client_socket, protocolo):
    global identificador
    paquete_final = None
    contador_fallos = 0
    print("Iniciando bucle principal sc")
    #Recibimos el tamaño del buffer
    BUFFER_SIZE = protocolo.recibir(client_socket, 4)
    while not BUFFER_SIZE:
        BUFFER_SIZE = protocolo.recibir(client_socket, 4)
        print(f'Esperando una conexión...', end='\r')
    BUFFER_SIZE1 = struct.unpack('i', BUFFER_SIZE[0:4]) #i indica entero de 4 bytes
    BUFFER_SIZE = int(BUFFER_SIZE1[0])
    BUFFER_SIZE += 16
    print(f'\nBuffer = {BUFFER_SIZE}')    

    #Recibimos los paquetes del cliente
    data = b''
    i = 0
    start_time = None
    packet_end = None
    hilo = None
    v_estimado = []
    identificador1 = []
    no_paq = 0
    paquete_final = None
    confirmacion = None
    while True: 
        t_ini = time.time()
        packet = protocolo.recibir(client_socket, BUFFER_SIZE)
        t_end = time.time()
        if not packet:
            no_paq += 1
            sleep(0.1)
            if no_paq > 10:
                print("Finalizado por not packet")
                no_paq = 0
                break
        elif analizador_paquete(packet):
            print("Recibido final paquete 1")
            paquete_final = True
            break
        if not start_time:
            start_time = time.time()
        if packet == b'0':
            print("\nPacket = 0")
            break
        
        #Completamos el tamaño del paquete para que todos sean iguales.
        t_ini2 = time.time()
        while len(packet) < BUFFER_SIZE:
            p=len(packet)
            remaining_bytes = BUFFER_SIZE - len(packet)
            additional_packet = protocolo.recibir(client_socket, remaining_bytes)
            s=len(additional_packet)
            #Si no hay paquetes adicionales, significa que se ha terminado de recibir
            if not additional_packet:
                no_paq += 1
                sleep(0.1)
                additional_packet = protocolo.recibir(client_socket, remaining_bytes)
                if no_paq > 3:
                    print("Finalizado por not additional_packet - Error de paquete (conexion no finalizada)")                
                    break            
            elif analizador_paquete(additional_packet):
                print("Recibido final paquete 2")
                packet += additional_packet[:-4]
                confirmacion = True
                break
            
            packet += additional_packet   
        t_end2 = time.time()

        dolar = struct.unpack('i', packet[0:4])[0]
        print(f'Dolar = {dolar}')
        if dolar != 2147483647:
            print("\nError de paquete")
            
        tiempo = struct.unpack('d', packet[4:12])[0]
        identificador = struct.unpack('i', packet[12:16])[0]        
        identificador1.append(identificador)
        if identificador != i:
            if len(identificador1) > 1:
                hola = (identificador1[i] - identificador1[i-1])
                diferencia = int(hola)
                contador_fallos += diferencia - 1
            else:
                contador_fallos += 1 
        v_estimado.append(len(packet)/((t_end2-t_ini)))                 #almacena el tiempo estimado en una lista
        v_estimado1 = sum(v_estimado)/len(v_estimado)                   #hacemos el promedio de velocidad para obtener una estimación precisa
        
        print(f'Paquete recibido: I: {identificador} , Len: {len(packet)}, V: {v_estimado1*8/1000: .2f} kb/s, Fallos: {contador_fallos}', '  ', end='\r')
        
        #Quitamos el encabezado de cada paquete para reconstruir el archivo original
        if not packet:
            continue
        packet = packet[16:]
        data += packet        
        i += 1
        
        if confirmacion:
            dolar = 1111111111
            print("Recibido paquete final")
            confirmacion = None
            paquete_final = True
            break
                
        if packet_end == b'0':
            break

    end_time = time.time()
    #Calculamos el tiempo que tarda en recibirse
    time_elapsed = end_time - start_time
    paq_recibidos = len(identificador1)
    if paquete_final:
        print("Paquete final enviado")
        dolar1 = struct.pack('i', dolar)
        ident = struct.pack('i', len(identificador1))
        contador_fallos1 = struct.pack('i', contador_fallos)
        paquete_final = dolar1 + ident + contador_fallos1
        protocolo.enviar(client_socket, paquete_final)
    #Calculamos la velocidad de transferencia
    transfer_speed = len(data) / time_elapsed
    print(f'\nTamaño archivo: {len(data)}')
    #Guardamos los datos recibidos en un archivo
    with open(f'/home/jorge/Desktop/PruebaRFD/Recibidos/sc_{protocolo}{time}.txt', 'wb') as file:
        file.write(data)

    #Imprimimos los resultados
    print(f'Tiempo que tarda en recibirse: {time_elapsed:.2f} segundos')
    print(f'Velocidad de transferencia: {transfer_speed:.2f} bytes/segundo')

    #Cerramos la conexión
    sleep(1)
    protocolo.cerrar_conexion_servidor(client_socket)     

def bucle_principal(client_socket, protocolo):
    global identificador
    contador_fallos = 0
    print("Iniciando bucle principal cc")
    #Recibimos el tamaño del buffer
    BUFFER_SIZE = protocolo.recibir(client_socket, 4)               #el cliente manda el tamaño de paquetes
    while not BUFFER_SIZE:
        BUFFER_SIZE = protocolo.recibir(client_socket, 4)
        print(f'Esperando una conexión...', end='\r')
    BUFFER_SIZE1 = struct.unpack('i', BUFFER_SIZE[0:4])             #i indica entero de 4 bytes
    BUFFER_SIZE = int(BUFFER_SIZE1[0])
    BUFFER_SIZE += 16
    print(f'\nBuffer = {BUFFER_SIZE}')

    #Nº de paquetes que se van a recibir
    n_paquetes = protocolo.recibir(client_socket, 2)                #el cliente manda el número de paquetes a recibir
    n_paquetes = struct.unpack('h', n_paquetes[0:2])[0]
    print(f'Se van a recibir {n_paquetes} paquetes')

    #Tamaño total del archivo a recibir
    t_archivo = protocolo.recibir(client_socket, 4)                 #el cliente manda el tamaño del archivo a recibir
    t_archivo = struct.unpack('i', t_archivo[0:4])[0]
    print(f'Tamaño archivo: {t_archivo} bytes')

    #Nº caracteres
    long_archivo = protocolo.recibir(client_socket, 1)
    long_archivo = struct.unpack('B', long_archivo[0:1])[0]
    #Nombre del archivo
    n_archivo = protocolo.recibir(client_socket, long_archivo)      #el cliente manda el nombre del archivo
    n_archivo = n_archivo.decode()
    print(f'Nombre del archivo: {n_archivo}')

    #Recibimos los paquetes del cliente
    data = b''
    i = 0
    start_time = None
    #total = 0
    packet_end = None
    hilo = None
    v_estimado = []
    identificador1 = []
    no_paq = 0
    confirmacion = None
    while True: 
        t_ini = time.time()
        packet = protocolo.recibir(client_socket, BUFFER_SIZE)
        t_end = time.time()
        if not packet:
            no_paq += 1
            sleep(0.1)
            if no_paq > 10:
                print("Finalizado por not packet")
                break
        elif analizador_paquete(packet):
            print("Recibido final paquete 1")
            paquete_final = struct.pack('i', 1111111111)
            sleep(1)
            protocolo.enviar(client_socket, paquete_final)
            break
        if not start_time:
            start_time = time.time()
        if packet == b'0':
            print("\nPacket = 0")
            break
        
        #Completamos el tamaño del paquete para que todos sean iguales.
        t_ini2 = time.time()
        while len(packet) < BUFFER_SIZE:
            p=len(packet)
            remaining_bytes = BUFFER_SIZE - len(packet)
            additional_packet = protocolo.recibir(client_socket, remaining_bytes)
            s=len(additional_packet)
            #Si no hay paquetes adicionales, significa que se ha terminado de recibir
            if not additional_packet:
                print("Finalizado por not additional_packet - Error de paquete (conexion no finalizada)")
                break
            elif analizador_paquete(additional_packet):
                print("Recibido final paquete 2")
                packet += additional_packet[:-4]
                confirmacion = True
                break
            packet += additional_packet
        

        t_end2 = time.time()

        
        #Reenviamos el paquete al cliente con el encabezado modificado
        if not packet:
            packet = protocolo.recibir(client_socket, BUFFER_SIZE)
            if not packet:
                break            
        
        dolar = struct.unpack('i', packet[0:4])[0]
        print(f'Dolar = {dolar}')
        if dolar != 2147483647:
            print("\nError de paquete")
            packet, identificador = correccion_paquete(packet) 
            k = 0           
            while identificador == -1:
                packet = protocolo.recibir(client_socket, BUFFER_SIZE)
                packet, identificador = correccion_paquete(packet)
                k += 1
                if k > 10:
                    print("10 fallos seguidos")
                    packet = None
                    break
            if not packet:
                break
        tiempo = struct.unpack('d', packet[4:12])[0]
        identificador = struct.unpack('i', packet[12:16])[0]        
        identificador1.append(identificador)
        if identificador != i:
            if len(identificador1) > 1:
                hola = (identificador1[i] - identificador1[i-1])
                diferencia = int(hola)
                contador_fallos += diferencia - 1
            else:
                contador_fallos += 1 
        v_estimado.append(len(packet)/((t_end2-t_ini)))                 #almacena el tiempo estimado en una lista
        v_estimado1 = sum(v_estimado)/len(v_estimado)                   #hacemos el promedio de velocidad para obtener una estimación precisa
        t_estimado = (t_archivo - len(data))/v_estimado1
        print(f'Paquete recibido: I: ({identificador} de {n_paquetes-1}), Len: {len(packet)}, Tiempo restante: {t_estimado: .0f} s, V: {v_estimado1*8/1000: .2f} kb/s', '  ', end='\r')
        fallos = struct.pack('i', contador_fallos)
        identificador2 = struct.pack('i', identificador)
        tiempo = struct.pack('d', tiempo)
        packet_cabecera = tiempo + identificador2 + fallos
        protocolo.enviar(client_socket, packet_cabecera)
        #Quitamos el encabezado de cada paquete para reconstruir el archivo original
        if not packet:
            continue
        packet = packet[16:]
        data += packet
        
        
        i += 1
        
        if confirmacion:
            dolar = 1111111111
            print(f"Recibido paquete final {dolar}")
            paquete_final = struct.pack('i', dolar)
            sleep(1)
            protocolo.enviar(client_socket, paquete_final)
            confirmacion = None
            break
            
        if packet_end == b'0':
            break

    end_time = time.time()
    #Calculamos el tiempo que tarda en recibirse
    time_elapsed = end_time - start_time

    #Calculamos la velocidad de transferencia
    transfer_speed = len(data) / time_elapsed
    print(f'\nTamaño archivo: {len(data)}')
    #Guardamos los datos recibidos en un archivo
    with open(f'/home/jorge/Desktop/PruebaRFD/Recibidos/{n_archivo}', 'wb') as file:
        file.write(data)

    #Imprimimos los resultados
    print(f'Tiempo que tarda en recibirse: {time_elapsed:.2f} segundos')
    print(f'Velocidad de transferencia: {transfer_speed:.2f} bytes/segundo')

    #Cerramos la conexión
    sleep(1)
    protocolo.cerrar_conexion_servidor(client_socket)

hilo1 = None
hilo2 = None
hilo3 = None

while True:                 #bucle para permanecer en escucha en los tres protocolos
    if not hilo1:    
        hilo1 = threading.Thread(target = hilo_Wifi)
        print("Hilo wifi iniciado")
        hilo1.start()
    if hilo1.is_alive() == False:
        print("Hilo dormido")        
        hilo1 = threading.Thread(target = hilo_Wifi)
        print("Hilo wifi iniciado")
        hilo1.start()
    if not hilo2:
        hilo2 = threading.Thread(target = hilo_Bluetooth)
        print("Hilo Bluetooth iniciado")
        hilo2.start()
    if hilo2.is_alive() == False:
        print("Hilo dormido") 
        hilo2 = threading.Thread(target = hilo_Bluetooth)
        print("Hilo Bluetooth iniciado")
        hilo2.start()
    if not hilo3:
        hilo3 = threading.Thread(target = hilo_RFD)
        print("Hilo RFD iniciado")    
        hilo3.start()
    if hilo3.is_alive() == False:
        print("Hilo dormido") 
        hilo3 = threading.Thread(target = hilo_RFD)
        print("Hilo RFD iniciado")
        hilo3.start()
    sleep(1)
