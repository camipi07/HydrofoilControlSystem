from time import sleep

# Updating the system path is not required if you have pip-installed
# rticonnextdds-connector
from sys import path as sys_path
from os import path as os_path
import rticonnextdds_connector as rti
import sys, time
import navio.rcinput
import navio.util


with rti.open_connector(config_name="MyParticipantLibrary::Radio_Participant", url="DDS.xml") as connector:

	outputRadio = connector.get_output("Radio_Pub::RadioWriter")

	#OBTENER DATOS DE RADIO

	navio.util.check_apm()
	rcin = navio.rcinput.RCInput()
	rcin2= navio.rcinput.RCInput()
	print("Waiting for subscriptions...")
	outputRadio.wait_for_subscriptions()
		
	while (True):
		period = rcin.read(2)
		period2 = rcin2.read(1)
		print (period+"+"+period2)
		time.sleep(1)


	        #writers for topics
	
		radio="Datos de RADIO"
	
		
		print("Writting...")
		print("\nReading serial bus")
		outputRadio.instance.set_number("motor_Power", float(period))
		outputRadio.instance.set_number("motor_direction", float(period2))
	
		outputRadio.write()
		
		print("Sended: Radio=" + period+"+" +period2) 			
		sleep(0.5)
			
		print("Finished!");
		outputRadio.wait()






