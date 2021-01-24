from time import sleep

# Updating the system path is not required if you have pip-installed
# rticonnextdds-connector
from sys import path as sys_path
from os import path as os_path
import rticonnextdds_connector as rti


with rti.open_connector(
        config_name="MyParticipantLibrary::Radio",
        url="DDS.xml") as connector:


	#OBTENER DATOS DE RADIO


        #writers for topics
	outputRadio = connector.get_output("Radio_Pub::RadioWriter")
	
	radio="Datos de RADIO"
	
	print("Waiting for subscriptions")
	outputRadio.wait_for_subscriptions()
		
	print("Writting...")
	print("\nReading serial bus")
	outputRadio.instance.set_string("radio", radio)

	outputRadio.write()
		
	print("Sended: Radio=" + radio) 			
	sleep(0.5)
			
	print("Finished!");
	outputRadio.wait()

