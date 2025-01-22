#-------------------------------------------------------------------------------------
#                              LIBRERÍA DE PROTOCOLOS
#-------------------------------------------------------------------------------------

#Nota: este programa no tiene que ejecutarse, únicamente tiene que estar en la misma 
    #carpeta que los archivos "cliente.py" y "servidor.py"

#Los protocolos de comunicación que se usarán son WiFi, Bluetooth y RFD (Serial)

import socket
import bluetooth
import serial
import time
from time import sleep

class Wifi:
    def __init__(self, ip, puerto, buff_size, packet):
        self.ip = ip
        self.puerto = puerto
        self.buff_size = buff_size
        self.packet = packet

    def conectar_cliente(ip, puerto):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.settimeout(2)
        server_address = (ip, puerto)
        client_socket.connect(server_address)       
        print(f'Conexión establecida con {server_address}')
        return client_socket
    
    def conectar_servidor(ip, puerto):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(5)
        server_address = (ip, puerto)
        server_socket.bind(server_address)        
        server_socket.listen()
        print('Esperando una conexión...')
        client_socket, client_address = server_socket.accept()
        print(f'Conexión establecida con {client_address}')
        return client_socket

    def enviar(client_socket, packet):
        client_socket.send(packet)

    def recibir(client_socket, buff_size):
        BUFFER_SIZE = client_socket.recv(buff_size)
        return BUFFER_SIZE
    
        
    def cerrar_conexion_cliente(client_socket):
        client_socket.shutdown(socket.SHUT_WR)
        client_socket.close()

    def cerrar_conexion_servidor(client_socket):
        client_socket.close()
        socket.socket.close
    
    def ping(ip, puerto, iteraciones):
        valores = []
        client_socket = Wifi.conectar_cliente(ip, puerto)
        for i in range(iteraciones):
            t_init = time.time()            
            Wifi.enviar(client_socket, b'0'*32)     # manda un paquete de 32 bytes            
            prueba = Wifi.recibir(client_socket, 32)
            t_end = time.time()
            ping = (t_end-t_init)*1e3
            print(f"Ping con ({ip}): {ping} ms, {len(prueba)} bits")
            valores.append(ping)          
        
        Wifi.cerrar_conexion_cliente(client_socket)
        media = sum(valores) / len(valores)
        print(f"Media:  {media}")
        return media
    
class Bluetooth(Wifi):  
    def conectar_cliente(mac, puerto):
        client_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        client_socket.settimeout(2)
        client_socket.connect((mac, puerto))               
        print(f'Conexión establecida con {mac}')
        return client_socket
    
    def conectar_servidor(mac, puerto):
        server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        server_socket.bind((mac, puerto))
        server_socket.listen()        
        print('Esperando una conexión...')
        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(5)      
        print(f'Conexión establecida con {client_address}')
        return client_socket    

    
    def cerrar_conexion_cliente(client_socket):
        client_socket.close()

    def cerrar_conexion_servidor(client_socket):
        client_socket.close()
        socket.socket.close

    def ping(mac, puerto, iteraciones):
        valores = []
        client_socket = Bluetooth.conectar_cliente(mac, puerto)

        for i in range(iteraciones):
            t_init = time.time()            
            Bluetooth.enviar(client_socket, b'0'*32)     # manda un paquete de 32 bytes            
            prueba = Bluetooth.recibir(client_socket, 32)
            t_end = time.time()
            ping = (t_end-t_init)*1e3
            print(f"Ping con ({mac}): {ping} ms, {len(prueba)} bits")
            valores.append(ping)
        Bluetooth.cerrar_conexion_cliente(client_socket)
        media = sum(valores) / len(valores)
        print(f"Media: {media}")
        return media        
    pass

class Bluetooth_Rasp(Bluetooth):  
    def conectar_cliente(mac, puerto):
        client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        client_socket.settimeout(5)
        client_socket.connect((mac, puerto))               
        print(f'Conexión establecida con {mac}')
        return client_socket
    
    def conectar_servidor(mac, puerto):
        server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_socket.settimeout(5)
        server_socket.bind((mac, puerto))
        server_socket.listen(puerto)        
        print('Esperando una conexión...')
        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(5)
        print(f'Conexión establecida con {client_address}')
        return client_socket           
    pass

class RFD():
    def conectar_cliente(ruta_puerto):
        client_socket = serial.Serial(ruta_puerto, baudrate=57600, timeout = 1)
        print("Esperando una conexión...")
        client_socket.write(b'10')
        BUFFER_SIZE = client_socket.read(2)
        if len(BUFFER_SIZE) < 2:
            sleep(1)
            BUFFER_SIZE = client_socket.read(2)
            if len(BUFFER_SIZE) < 2:
                raise Exception("RFD Timeout de 5s")
        print("Conexión establecida con cliente RFD")
        return client_socket
    
    def conectar_servidor(ruta_puerto):
        client_socket = serial.Serial(ruta_puerto, baudrate=57600, timeout = 1)
        BUFFER_SIZE = client_socket.read(2)
        if len(BUFFER_SIZE) < 2:
            sleep(5)
            BUFFER_SIZE = client_socket.read(2)
            if len(BUFFER_SIZE) < 2:
                raise Exception("RFD Timeout de 5s")
        client_socket.write(BUFFER_SIZE)        
        return client_socket
        
    def enviar(client_socket, packet):
        client_socket.write(packet)

    def recibir(client_socket, buff_size):
        BUFFER_SIZE = client_socket.read(buff_size)
        return BUFFER_SIZE
    
    def cerrar_conexion_cliente(client_socket):
        client_socket.close()

    def cerrar_conexion_servidor(client_socket):
        sleep(0.1)

    def ping(ruta_puerto, iteraciones):
        valores = []
        client_socket = RFD.conectar_cliente(ruta_puerto)

        for i in range(iteraciones):
            t_init = time.time()            
            RFD.enviar(client_socket, b'0'*32)     # manda un paquete de 32 bytes            
            prueba = RFD.recibir(client_socket, 32)
            t_end = time.time()
            ping = (t_end-t_init)*1e3
            print(f"Ping con ({ruta_puerto}): {ping} ms, {len(prueba)} bits")
            valores.append(ping)
        RFD.cerrar_conexion_cliente(client_socket)
        media = sum(valores) / len(valores)
        print(f"Media: {media}")
        return media