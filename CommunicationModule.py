from time import sleep
import time
import sys
import serial
import rticonnextdds_connector as rti
import threading

# Updating the system path is not required if you have pip-installed
# rticonnextdds-connector
with rti.open_connector(
        config_name="MyParticipantLibrary::CommunicationModule",
        url="DDS.xml") as connector:

        inputServo = connector.get_input(
            "CommunicationModule_Sub::CommunicationModulerReader")
        #HILO DE SUBSCRIPCION EN LOS DATOS ENVIADOS POR EL MIXER
        def thread_function():
            global inputServo
            while True:
                
                try:
                    inputServo.wait()
                    inputServo.take()

                    for sample in inputServo.samples.valid_data_iter:
                        data = sample.get_dictionary()
                        positionServoCentral = data["positionServoCentral"]
                        positionServoLeft = data["positionServoLeft"]
                        positionServoRight = data["positionServoRight"]

                        print("positionServoCentral=" + str(positionServoCentral)+" positionServoLeft=" +
                                str(positionServoLeft)+" positionServoRight=" + str(positionServoRight))
                        #ser.write(str.encode(str(positionServoCentral)+"\n"))

                        ser.write(str.encode(str(positionServoCentral)+"#"+str(positionServoLeft)+"#"+str(positionServoRight)+"\n"))
                        ser.flush()
                        
                        f= open("ServosCorrections.txt","a+")
                        f.write("Position S-Central= %f \n" % positionServoCentral)
                        f.write("Position S-Left= %f \n" % positionServoLeft)
                        f.write("Position S-Right= %f \n" % positionServoRight)
                        f.close()
                except Exception as e:
                    print("") 
                    continue


        # ABRIR ENLACE SERIAL Y PARSEAR INFO PARA PUBLICARLA EN DDS
        if __name__ == '__main__':

            #ser = serial.Serial('/dev/ttyACM4', 57600)
            ser = serial.Serial('/dev/ttyACM1', 57600)
            # writers for topics
            outputHeight = connector.get_output(
                "CommunicationModule_Pub::CommunicationModuleWriterHeight")
            outputPitch = connector.get_output(
                "CommunicationModule_Pub::CommunicationModuleWriterPitch")
            outputRoll = connector.get_output(
                "CommunicationModule_Pub::CommunicationModuleWriterRoll")
            outputGPS = connector.get_output(
                "CommunicationModule_Pub::CommunicationModuleWriterGPS")
            #inputServo.wait_for_publications()
            outputHeight.wait_for_subscriptions()
            outputPitch.wait_for_subscriptions()
            outputRoll.wait_for_subscriptions()
            sub_thread = threading.Thread(target=thread_function, daemon=True)
            sub_thread.start()
            ser.flush()
            while True:
                try:

                    line = ser.readline().decode().rstrip().replace('\n', ' ')
                    #print(line)
                    f= open("ArduinoData.txt","a+")
                    f.write(line)
                    f.write("\n")
                    f.close()

                    if line.startswith('Pitch= '):
                        pitch = line.split(' ')[1]
                        print("Pitch received= "+pitch)
                        outputPitch.instance.set_number("pitch", float(pitch))
                        outputPitch.write()
                    elif line.startswith('Roll= '):
                        roll = line.split(' ')[1]
                        print("Roll received= "+roll)
                        outputRoll.instance.set_number("roll", float(roll))
                        outputRoll.write()
                    elif line.startswith('Altura= '):
                        height = line.split(' ')[1]
                        print("Altura received= "+height)
                        outputHeight.instance.set_number(
                            "height", float(height))
                        outputHeight.write()
                    elif line.startswith('LAT= '):
                        latitude = line.split(' ')[1]
                        print("Latitud received= "+latitude)
                        outputGPS.instance.set_number(
                            "latitude", float(latitude))
                        outputGPS.write()
                    elif line.startswith('LONG= '):
                        longitude = line.split(' ')[1]
                        print("Longitud received= "+longitude)
                        outputGPS.instance.set_number(
                            "longitude", float(longitude))
                        outputGPS.write()
                    elif line.startswith('ALT= '):
                        altitude = line.split(' ')[1]
                        print("Altitud received= "+altitude)
                        outputGPS.instance.set_number(
                            "altitude", float(altitude))
                        outputGPS.write()
                    elif line.startswith('SPEED= '):
                        speed = line.split(' ')[1]
                        print("Speed received= "+speed)
                        outputGPS.instance.set_number("speed", float(speed))
                        outputGPS.write()

                        """
                    elif line.startswith('ServoCentral= '):
                        servoCentral = line.split(' ')[1]
                        print("ServoCentral= "+servoCentral)
                    elif line.startswith('ServoLeft= '):
                        servoLeft = line.split(' ')[1]
                        print("ServoLeft= "+servoLeft)
                    elif line.startswith('ServoRight= '):
                        servoRight = line.split(' ')[1]
                        print("ServoRight= "+servoRight)
                        """
                    else:
                        print(line)

                except KeyboardInterrupt:
                    outputPitch.wait()
                    outputRoll.wait()
                    outputHeight.wait()
                    outputGPS.wait()
                    ser.close()
                    try:
                        sys.exit()  # this always raises SystemExit

                    except SystemExit:

                        print("sys.exit() worked as expected")
                except Exception as e:
                    print(e)
                    continue

