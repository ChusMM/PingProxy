# -*- coding: utf-8 -*-
# Jesus Manuel Muñoz Mazuecos Ingeniería técnica en informática de sistemas
# Referencias
# La documentación de python para utlizar todo lo referente a sockets y expresiones regulares
# http://docs.python.org/library/re.html
# http://docs.python.org/library/socket.html
# En el siguiente enlace se muestra la estructura básica de un servidor proxy
# http://danigm.net/node/82
# Los dos enlaces restantes tienen información acerca de la gestión de procesos en python
# http://www.ibm.com/developerworks/aix/library/au-multiprocessing/
# https://arco.esi.uclm.es/svn/public/misc/python_networking/upper/TCP_fork_server.py

import sys
import socket
import select
import os
import re

def proxy(s1):
	
	httpReq = ''
	msg = 0
	
	while not msg or len(msg) == 1024:
		msg = s1.recv(1024) # recojo la petición que me llega al servidor proxy
		httpReq += msg
		
	#print len(msg)
	print httpReq
	
	# el host destino viene a continuación de la expresion: "Host: "
	# con split se parte la cadena en el número de partes que coincide con el número de
	# veces que aparece la expresión ya mencionada, cada vez que aparece la expresión "Host: "
	# se crea una nueva partición que contiene la cadena que sigue a la expresión hasta que se encuentra 
	# otra expresión. En este caso sólo aparece una vez.
	#regex = re.compile(r'Host: ')
	#splited = regex.split(httpReq)[1]
	#print splited
	#regex = re.compile(r'\r\n')
	# nuestro host va desde el principio de la cadena obtenida hasta la cadena \r\n 
	#host = regex.split(splited)[0]
	
	#Solución mejorada para extraer el host destino del http Reply
	regex = re.search("Host:\W(.+)\W\n", httpReq)
	print regex.group(1)
	
	host = regex.group(1)
		
	addr = socket.gethostbyname(host)
	s2 = socket.socket() #socket que se conecta con el servidor destino
	s2.connect((addr, 80))
	
	s2.send(httpReq) #y se la envio al servidor para que la procese
	
	inp = []
	httpRepl = ''
	
	while msg: # mientras haya un mensaje
		while 1:
			inp, outp, excons = select.select([s2], [], [], 1.0)
			break
			
		if(inp):
			msg = s2.recv(1024)
			httpRepl += msg
		else:
			print "Breeeeeeeeeeeeeeeeeeak"
			break
			
	s1.send(httpRepl) #la petición que recibo del servidor se la envio al cliente
	s1.close()
	s2.close()

def main():
	
	mserver = 'localhost'
	mport = 8080 #puerto del proxy
	
	s = socket.socket()
	s.bind((mserver, mport))
	s.listen(10)
	
	while(1):
		try:
			print "Esperando peticiones en: %s:%s" %(mserver, mport)
			client = s.accept()  # espera a la acepatación de conexiones
			s1 = client[0]       # socket esclavo que devuelve acceprt
			
			try:
				pid = os.fork(); # se crea un proceso hijo y se llama al procedimiento principal
				if pid == 0:
					s.close()
					proxy(s1)
					exit()
				else:
					os.waitpid(pid, 0) # esperar a que el hijo termine
					print "Soy el pater"
					
			except os.error:
				
				print "Error al lanzar el proceso hijo"
				sys.exit(-1)
				
		except KeyboardInterrupt:
			s.close()
			print "bye"
			break
	
main()