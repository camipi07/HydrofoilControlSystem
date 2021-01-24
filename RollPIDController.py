import time
from simple_pid import PID
import rticonnextdds_connector as rti
import threading
import parameters
import argparse


class RollPIDController:

    def thread_function(self):
        while True:
            try:
                self.inputRollCtes.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
                print("Waiting for ctes...")
                self.inputRollCtes.wait()
                print("NEW CTES")
                self.inputRollCtes.take()
                print("CTES TAKEN")

                for sample in self.inputRollCtes.samples.valid_data_iter:
                    data = sample.get_dictionary()
                    self.p = data["cte_PID_Roll_prop"]
                    self.i = data["cte_PID_Roll_der"]
                    self.d = data["cte_PID_Roll_int"]
                    break
                     
            except:
                print("")
                continue

    def __init__(self):
        self.p=parameters.CTE_ROLL_PROPORTIONALITY
        self.i=parameters.CTE_ROLL_INTEGRATION
        self.d=parameters.CTE_ROLL_DERIVATION
        self.roll = 0 # initial roll 
        self.desired_roll = parameters.DESIRED_ROLL() # arbitrary point in mm (to be determined!)
        self.connector_sub = rti.Connector(config_name="MyParticipantLibrary::PID_Roll", url= "DDS.xml")
        self.inputRollCtes= self.connector_sub.get_input("PID_Roll_Sub::PIDRollReaderCtes")
        self.input = self.connector_sub.get_input("PID_Roll_Sub::PIDRollReader")
        self.connector_pub = rti.Connector(config_name="MyParticipantLibrary::PID_Roll",url="DDS.xml")
        self.output = self.connector_pub.get_output("PID_Roll_Pub::PIDRollWriter")


    def get_roll_info(self): 
        '''Listens for roll info from DDS bus and returns it'''

        print("\nWaiting for roll data...")
        try:
            self.input.wait()
            self.input.take()

            for sample in self.input.samples.valid_data_iter:
                data = sample.get_dictionary()
                roll = data["roll"]
                print("ROLL RECEIVED:",roll)
                return roll

        except:
            print("")
            return 200 


    def send_roll_corrections(self,change):
    
        self.output.instance.set_number("roll_pid", change)
        self.output.write()
        print("Sent roll correction = " + str(change))


if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
           "--simulated", help="System mode [Default: Mode simulator]", action="store_true", default=False, required=False)
        args = parser.parse_args()
        
        simulator_mode = args.simulated  # if false, the system is in "real world" mode
        
        controller = RollPIDController() #Instantiate the controller

        
        print("Waiting for roll publications...")
        controller.input.wait_for_publications() #SUBSCRIBE TO THE DDS TOPIC
        controller.output.wait_for_subscriptions()

        start_time = time.time() 
        last_time = start_time

        sub_thread = threading.Thread(target=controller.thread_function, daemon=True)
        sub_thread.start()
        pid = PID(controller.p, controller.i, controller.d, controller.desired_roll) # create the pid according to boat desired roll
        pid.sample_time=0.05
        pid.output_limits=(parameters.PID_ROLL_MIN_CORRECTION(),
                          parameters.PID_ROLL_MAX_CORRECTION())
        
        while True:    #EXECUTE CONSTANTLY BUT PID ONLY ACTS IF pid.sample_time SECONDS HAVE PASSED

            try:
                pid.tunings = (controller.p, controller.i, controller.d)

                print("Current ctes: ",controller.p,"#",controller.i,"#",controller.d)
                controller.roll = controller.get_roll_info()    


    #            if controller.roll != controller.desired_roll:
                print("Current roll: ",controller.roll)

                current_time = time.time()
                dt = current_time - last_time
                change = pid(controller.roll) 
                roll = controller.send_roll_corrections(change)
                
                last_time = current_time

            except:
                print("Strange data. Continue...")
                continue
    
