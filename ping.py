# Jesus Mu%oz Mazuecos
# Maria Morales Nu%o

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Fuentes:
# Esencialmente informacion del moodle ya que toda es necesaria para llevar
# a cabo la realizacion correcta de dicha practica y los conocimientos previos de python de a%os pasados.
# https://campusvirtual.uclm.es
# http://mundogeek.net/tutorial-python/
# http://es.wikipedia.org/wiki/Ping
# http://crysol.org/node/796
# http://www.ietf.org/rfc/rfc792.txt

import sys, os, socket, array, time, struct, string, select, math, binascii, getopt

def checksum(ICMPpacket):
    
    if len(ICMPpacket) & 1:
        ICMPpacket = ICMPpacket +'\0'
        
    words = array.array('h' , ICMPpacket)
    suma = 0
    
    for word in words:
        suma += (word & 0xffff)
        
    PAlta = suma >> 16
    PBaja = suma & 0xffff
    suma = PAlta + PBaja
    suma = suma + (suma >> 16)

    return (~suma) & 0xffff
    

def ICMP(npacket):
 
    carga = "S" * 56
    # cabecera ICMP
    cab = struct.pack('bbHHh', 8, 0, 0, 0, npacket)
    # devuelve una cadena de acuerdo con el formato, en este caso va a ser la cabecera ICMP
    # tipo 8 = Echo Request
    # codigo = 0
    # checksum = 0
    # identificador = 0
    # Creamos el paquete, para calcular el checksum
    packet = cab + carga
    checks = checksum(packet)
    # Construimos la cabecera y el paquete (ya con el checksum correcto). Y lo devolvemos
    cab = struct.pack('bbHHh', 8, 0, checks, 0, npacket)
    packet = cab + carga
    return packet

def recibir(host, direccion, sock, timeInit, npkt):
    #Extraer la cabecera
    packetRet, sourceAddr = sock.recvfrom(56+48)

    tipo, codigoRet, checksumRet, IDRet, seqRet = struct.unpack("bbHHh", packetRet[20:28])
    #print "tipo: %s npkt %d seqRet %d" %(tipo,npkt,seqRet)
    print npkt
    print seqRet
    if tipo == 0 and seqRet == npkt: # tipo=0 Echo Reply tipo=8 echo (localhost)
        timeEnd = time.time() - timeInit
        print "%d bytes from %s (%s): icmp_seq=%d time=%.2f ms" %(56+8, host, direccion, seqRet, timeEnd * 1000)

    elif  tipo == 11:
        print "From "+host+" icmp_seq="+str(seqRet)+" Time to live exceeded"
        timeEnd = -1;

    elif  tipo == 3:
        print "From "+host+" icmp_seq="+str(seqRet)+" Destination Unreachable"
        timeEnd = -1;
        
    elif  tipo == 12:
        print "From "+host+" icmp_seq="+str(seqRet)+" Parameter Problem"
        timeEnd = -1;
        
    elif  tipo == 4:
        print "From "+host+" icmp_seq="+str(seqRet)+" Source Quench"
        timeEnd = -1;
        
    elif  tipo == 5:
        print "From "+host+" icmp_seq="+str(seqRet)+" Redirect Message"
        timeEnd = -1;
                 
    return timeEnd

def ping(host):

    npkt = 0
    failed = 0
    totaltime = 0
    nrecvs = 0.0
    nsends = 0.0
    #Ctrl-C
    try:
        try:
            direccion = socket.gethostbyname(host); # para obtener la direccion del host
        
        except:
            print "Error, Cannnot find host %s" %host
            sys.exit(1)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("ICMP")) # crear el socket para ICMP
        
        except socket.error , message:
            print "Cannot fill the socket with data %s" %(message)
            sys.exit(1)

        print "PING %s (%s) 56(84) bytes of data." %(host, direccion)
        # 84 = 20 cabecera IP + 8 cab ICMP + carga(56)
    
    
        while npkt < 3:

            npkt += 1;
            timeInit = 0
            timeEnd = 0
            packet = ICMP(npkt)

            # Enviar el paquete
            try:
                sock.sendto(packet, (host, 1))
                timeInit = time.time()
            
            except socket.error , message:
                print "Error,  %s " %(message)
                sock.close()
                sys.exit()
                
            nsends += 1
            entrada = []
            while 1:
                # esta a la escucha hasta que nuestro descriptor sufra cambios
                entrada, salida, cond_excep = select.select( [sock], [], [], 1.0)
                break

            if entrada: # si hemos recibido datos
                timeEnd = recibir(host, direccion, sock, timeInit, npkt)

                if timeEnd != -1:
                    totaltime += timeEnd
                    nrecvs += 1
                 
                else:
                    failed += 1
                
            else:
                print "Error: timeout has expired"

            time.sleep(1) #esperar un segundo
            
        sock.close()
        print "%d packets transmitted, %d packets received, time %.2f" %(nsends, nrecvs, totaltime * 1000)
        print "%d packets failed" %(failed)
        print "valid replies percentage: %.2f%%" %( (nrecvs / nsends) * 100)
        if nrecvs > 0:
            print "Average time of going and return: %.2f ms" %((totaltime / nrecvs) * 1000)
            print ""
            print "Jesus Manuel Mu%oz Mazuecos"
            print "Maria Morales Nu%o"
       
    except KeyboardInterrupt:
        print "%d packets transmitted, %d packets received, time %.2f" %(nsends, nrecvs, totaltime * 1000)
        print "%d packets failed" %(failed)
        print "valid replies percentage: %.2f%%" %( (nrecvs / nsends) * 100)
        if nrecvs > 0:
            print "Average time of going and return: %.2f ms" %((totaltime / nrecvs) * 1000)
            print "Jesus Manuel Mu%oz Mazuecos"
            print "Maria Morales Nu%o"
       
                
def main():
    if len(sys.argv) == 2:
        ping(sys.argv[1])
    else:
        print "Use: $python ping.py <host>"
main()
