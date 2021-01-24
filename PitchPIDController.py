import time
from simple_pid import PID
import rticonnextdds_connector as rti
import threading
import parameters
import argparse



class PitchPIDController:

    def thread_function(self):
        while True:
            try:
                self.inputPitchCtes.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
                print("Waiting for ctes...")
                self.inputPitchCtes.wait()
                print("NEW CTES")
                self.inputPitchCtes.take()
                print("CTES TAKEN")

                for sample in self.inputPitchCtes.samples.valid_data_iter:
                    data = sample.get_dictionary()
                    self.p = data["cte_PID_Pitch_prop"]
                    self.i = data["cte_PID_Pitch_der"]
                    self.d = data["cte_PID_Pitch_int"]
                    break
                     
            except:
                print("")
                continue


    def __init__(self):
        self.p=parameters.CTE_PITCH_PROPORTIONALITY
        self.i=parameters.CTE_PITCH_INTEGRATION
        self.d=parameters.CTE_PITCH_DERIVATION
        self.pitch = 0 # initial pitch 
        self.desired_pitch = parameters.DESIRED_PITCH() # ideally 0 degrees respect water (yet to be determined)
        self.connector_sub = rti.Connector(config_name="MyParticipantLibrary::PID_Pitch", url= "DDS.xml")
        self.inputPitch = self.connector_sub.get_input("PID_Pitch_Sub::PIDPitchReader")
        self.inputPitchCtes= self.connector_sub.get_input("PID_Pitch_Sub::PIDPitchReaderCtes")
        self.connector_pub = rti.Connector(config_name="MyParticipantLibrary::PID_Pitch",url="DDS.xml")
        self.output = self.connector_pub.get_output("PID_Pitch_Pub::PIDPitchWriter")


    def get_pitch_info(self): 

        print("\nWaiting for pitch data...")
        try:
            self.inputPitch.wait()

            self.inputPitch.take()

            for sample in self.inputPitch.samples.valid_data_iter:
                data = sample.get_dictionary()
                pitch = data["pitch"]
                return pitch
        except:
            print("")
            return 200   

    def send_pitch_corrections(self,change):
    
        self.output.instance.set_number("pitch_pid", change)
        self.output.write()
        print("Sent pitch correction= " + str(change))


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
           "--simulated", help="System mode [Default: Mode simulator]", action="store_true", default=False, required=False)
        args = parser.parse_args()
        
        simulator_mode = args.simulated  # if false, the system is in "real world" mode

        controller = PitchPIDController() #Instantiate the controller
        
        print("Waiting for pitch publications...")
        controller.inputPitch.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
        controller.output.wait_for_subscriptions()
        start_time = time.time() 
        last_time = start_time

        sub_thread = threading.Thread(target=controller.thread_function, daemon=True)
        sub_thread.start()
        
        pid = PID(controller.p, controller.i, controller.d, controller.desired_pitch) #create the pid according to boat desired pitch
        pid.sample_time=0.05
        pid.output_limits=(parameters.PID_PITCH_MIN_CORRECTION(),
                          parameters.PID_PITCH_MAX_CORRECTION()) #limit the range of action to aprox (-25,25) degrees

        
        while True:    #EXECUTE CONSTANTLY BUT PID ONLY ACTS IF pid.sample_time SECONDS HAVE PASSED

            try:
                pid.tunings = (controller.p, controller.i, controller.d)
                
                print("Current ctes: ",controller.p,"#",controller.i,"#",controller.d)
                
                controller.pitch = controller.get_pitch_info()    
            # if controller.pitch != controller.desired_pitch:
                print("Current pitch: ",controller.pitch)

                current_time = time.time()
                dt = current_time - last_time
                change = pid(controller.pitch) 
                pitch = controller.send_pitch_corrections(change)
                last_time = current_time
                    #plot_debugging_data(x,y,desired_value)

            except:
                print("Strange data. Continue...")
                continue
            
