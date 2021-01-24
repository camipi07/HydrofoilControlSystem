import time
from simple_pid import PID
import rticonnextdds_connector as rti
import threading
import parameters
import argparse


class HeightPIDController:

    def thread_function(self):
        while True:
            try:
                self.inputHeightCtes.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
                print("Waiting for ctes...")
                self.inputHeightCtes.wait()
                print("NEW CTES")
                self.inputHeightCtes.take()
                print("CTES TAKEN")

                for sample in self.inputHeightCtes.samples.valid_data_iter:
                    data = sample.get_dictionary()
                    self.p = data["cte_PID_Height_prop"]
                    self.i = data["cte_PID_Height_der"]
                    self.d = data["cte_PID_Height_int"]
                    break
                     
            except:
                print("")
                continue

    def __init__(self,simulated):
        self.p=parameters.CTE_HEIGHT_PROPORTIONALITY
        self.i=parameters.CTE_HEIGHT_INTEGRATION
        self.d=parameters.CTE_HEIGHT_DERIVATION
        self.height = 0 # initial height 
        self.desired_height = parameters.DESIRED_HEIGHT(simulated) # arbitrary point in cm (to be determined!)
        self.connector_sub = rti.Connector(config_name="MyParticipantLibrary::PID_Height", url= "DDS.xml")
        self.input = self.connector_sub.get_input("PID_Height_Sub::PIDHeightReader")
        self.inputHeightCtes= self.connector_sub.get_input("PID_Height_Sub::PIDHeightReaderCtes")
        self.connector_pub = rti.Connector(config_name="MyParticipantLibrary::PID_Height",url="DDS.xml")
        self.output = self.connector_pub.get_output("PID_Height_Pub::PIDHeightWriter")


    def get_height_info(self): 
        '''Listens for height info from DDS bus and returns it'''

        print("\nWaiting for height data...")
        try:
            self.input.wait()
            self.input.take()

            for sample in self.input.samples.valid_data_iter:
                data = sample.get_dictionary()
                height = data["height"]
                print("HEIGHT RECEIVED:",height)
                return height

        except:
            print("")
            return 200


    def send_height_corrections(self,change):
    
        self.output.instance.set_number("height_pid", change)
        self.output.write()
        print("Sent height correction= " + str(change))


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
           "--simulated", help="System mode [Default: Mode simulator]", action="store_true", default=False, required=False)
        args = parser.parse_args()
        
        simulator_mode = args.simulated  # if false, the system is in "real world" mode

        controller = HeightPIDController(simulator_mode) #Instantiate the controller

        print("Waiting for height publications...")
        controller.input.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
        controller.output.wait_for_subscriptions()


        sub_thread = threading.Thread(target=controller.thread_function, daemon=True)
        sub_thread.start()
        
        pid = PID(controller.p, controller.i, controller.d, controller.desired_height) #create the pid according to boat desired pitch
        pid.sample_time=0.05
        pid.output_limits=(parameters.PID_HEIGHT_MIN_CORRECTION(simulator_mode),parameters.PID_HEIGHT_MAX_CORRECTION(simulator_mode)) #limit the range of action to (-40,40) centimeters

        while True:    
            try:
                pid.tunings = (controller.p, controller.i, controller.d)
                
                
                #print("Current ctes: ",controller.p,"#",controller.i,"#",controller.d)
                controller.height = controller.get_height_info()    
                
                print("Current HEIGHT = ",controller.height)

    #            if controller.height != controller.desired_height:
                    #print("Current height: ",controller.height)

                change = pid(controller.height) 
                height = controller.send_height_corrections(change)
                
                    #plot_debugging_data(x,y,desired_value)
    #            else:
                    #print("Value not accepted")
            except:
                print("Strange data. Continue...")
                continue
        
        

