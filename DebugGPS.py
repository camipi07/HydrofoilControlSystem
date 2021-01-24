from __future__ import print_function

from sys import path as sys_path
from os import path as os_path
import rticonnextdds_connector as rti

with rti.open_connector(
        config_name="MyParticipantLibrary::Debug",
        url="DDS.xml") as connector:

	inputGPS = connector.get_input("Debug_Sub::DebugReaderGPS")

	print("Waiting for publications...")
	inputGPS.wait_for_publications()

	print("\nWaiting for data...")
	inputGPS.wait()

	inputGPS.take()
		
	for sample in inputGPS.samples.valid_data_iter:
		data = sample.get_dictionary()
		latitude = data["latitude"]
		longitude = data["longitude"]
		altitude = data["altitude"]
		speed = data["speed"]

		print("Received: Latitud=" + str(latitude)+" Longitud=" + str(longitude)+" Altitud=" + str(altitude)+" Velocidad=" + str(speed)) 			
			

	print("Finished!")

