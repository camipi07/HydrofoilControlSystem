from time import sleep
import random


import rticonnextdds_connector as rti


with rti.open_connector(
        config_name="MyParticipantLibrary::CommunicationModule",
        url="../DDS.xml") as connector:

    # writers for topics
    outputHeight = connector.get_output(
        "CommunicationModule_Pub::CommunicationModuleWriterHeight")
    outputPitch = connector.get_output(
        "CommunicationModule_Pub::CommunicationModuleWriterPitch")
    outputRoll = connector.get_output(
        "CommunicationModule_Pub::CommunicationModuleWriterRoll")
    outputGps = connector.get_output("CommunicationModule_Pub::CommunicationModuleWriterGPS")

    print("Waiting for subscriptions")
    outputHeight.wait_for_subscriptions()
    outputPitch.wait_for_subscriptions()
    outputRoll.wait_for_subscriptions()
    outputGps.wait_for_subscriptions()
    speed = 0

    while True:
        print("Writting...")
        height = random.uniform(-1, 1)  # 35 to 45 cm
        pitch = random.uniform(-0.05, 0.05)  # -35º to 35º
        roll = random.uniform(0.490865, 0.610865)  # -35º to 35º
        latitude = random.uniform(42.2263946, 42.2263946+0.03)
        longitude = random.uniform(-8.7345389, -8.7345389+0.01)

        if speed < 100:
            speed = speed+1
        else:
            speed = 0

        outputHeight.instance.set_number("height", height)
        outputPitch.instance.set_number("pitch", pitch)
        outputRoll.instance.set_number("roll", roll)
        outputGps.instance.set_number("speed", speed)
        outputGps.instance.set_number("latitude", latitude)
        outputGps.instance.set_number("longitude", longitude)

        outputHeight.write()
        outputPitch.write()
        outputRoll.write()
        outputGps.write()
        line="Height ="+str(height)+"\nPitch = "+str(pitch)+"\nRoll ="+str(roll)+"\nSpeed ="+str(speed)+"\nLatitude ="+str(latitude)+"\nLongitude ="+str(longitude)
        print(line)
        
        f= open("ArduinoData.txt","a+")
        f.write(line)
        f.write("\n")
        f.close()
        outputHeight.wait()
        outputPitch.wait()
        outputRoll.wait()
        outputGps.wait()
        sleep(3)
