from __future__ import print_function
import rticonnextdds_connector as rti
import parameters 
import argparse


servo_central_position = 0
servo_left_position = 0
servo_right_position = 0
mixer_mode = parameters.MODE_FULL  # default mode is full

# FUNCTIONS FOR CALCULATING THE PITCH TERMS FOR THE MIXING

def get_height_term(height_correction):
    if height_correction >= 0:      
         return (parameters.MAX_FOIL_ANGLE() * height_correction / parameters.PID_HEIGHT_MAX_CORRECTION(simulator_mode))
    elif height_correction < 0: 
        return (parameters.MIN_FOIL_ANGLE() * height_correction / parameters.PID_HEIGHT_MIN_CORRECTION(simulator_mode))

def get_pitch_term(pitch_correction):
    if pitch_correction >= 0:
        return (parameters.MAX_FOIL_ANGLE() * pitch_correction / parameters.PID_PITCH_MAX_CORRECTION())
    elif pitch_correction < 0:
        return (parameters.MIN_FOIL_ANGLE() * pitch_correction/parameters.PID_PITCH_MIN_CORRECTION())

def get_roll_term(roll_correction):
    if roll_correction >=0:
        return (parameters.MAX_FOIL_ANGLE() * roll_correction / parameters.PID_ROLL_MAX_CORRECTION())
    elif roll_correction < 0:
        return (parameters.MIN_FOIL_ANGLE() * roll_correction / parameters.PID_ROLL_MIN_CORRECTION())

# FUNCTIONS FOR CALCULATING THE FOIL POSITIONS BASED ON THE PREVIOUS TERMS


def get_central_position(height_correction):
    return (get_height_term(height_correction)*parameters.MIXER_HEIGHT_PONDERATION+get_pitch_term(pitch_correction)*parameters.MIXER_PITCH_PONDERATION)*parameters.MIXER_FACTOR


def get_left_foil_position(height_correction, pitch_correction, roll_correction):
    return (get_height_term(height_correction)*parameters.MIXER_HEIGHT_PONDERATION-get_pitch_term(pitch_correction)*parameters.MIXER_PITCH_PONDERATION-get_roll_term(roll_correction)*parameters.MIXER_ROLL_PONDERATION)*parameters.MIXER_FACTOR


def get_right_foil_position(height_correction, pitch_correction, roll_correction):
    return (get_height_term(height_correction)*parameters.MIXER_HEIGHT_PONDERATION-get_pitch_term(pitch_correction)*parameters.MIXER_PITCH_PONDERATION+get_roll_term(roll_correction)*parameters.MIXER_ROLL_PONDERATION)*parameters.MIXER_FACTOR


def read_data(source, inputName):
            print("\nWaiting for ", inputName.upper(), " data...")
            source.wait()
            source.take()

            for sample in source.samples.valid_data_iter:
                data = sample.get_dictionary()
                value = data[inputName]
                print("Received ", inputName.upper(), ": ", value)
                return value


with rti.open_connector(
        config_name="MyParticipantLibrary::PID_Mixer",
        url="DDS.xml") as connector:
        
        parser = argparse.ArgumentParser()
        parser.add_argument(
           "--simulated", help="System mode [Default: Mode simulator]", action="store_true", default=False, required=False)
        args = parser.parse_args()
        
        simulator_mode = args.simulated  # if false, the system is in "real world" mode



        roll_correction_input = connector.get_input("PID_Mixer_Sub::PIDRollReader")
        height_correction_input = connector.get_input("PID_Mixer_Sub::PIDHeightReader")
        pitch_correction_input = connector.get_input("PID_Mixer_Sub::PIDPitchReader")
        servo_correction_output = connector.get_output("PID_Mixer_Pub::PIDMixerWriter")
       
        print("Waiting for publications...")
       
        height_correction_input.wait_for_publications()
        pitch_correction_input.wait_for_publications()   
        roll_correction_input.wait_for_publications()
        servo_correction_output.wait_for_subscriptions()
    
            
        while True:
            
            height_correction = read_data(height_correction_input,"height_pid")
            roll_correction   = read_data(roll_correction_input,"roll_pid")
            pitch_correction  = read_data(pitch_correction_input,"pitch_pid")


            
            if simulator_mode == True:
                '''Testing mode is for the first test in water, where height and pitch of the boat
                are not taken into consideration for the first tries'''
                servo_central_position = get_central_position(height_correction)
                servo_left_position = get_left_foil_position(height_correction,pitch_correction,roll_correction)
                servo_right_position = get_right_foil_position(height_correction,pitch_correction,roll_correction)
                
            elif simulator_mode == False: #adds 90ª to the corrections for "real world" mode
                
                servo_central_position = get_central_position(height_correction) + 90
                servo_left_position = get_left_foil_position(height_correction,pitch_correction,roll_correction) + 90
                servo_right_position = get_right_foil_position(height_correction,pitch_correction,roll_correction) + 90
            
            
            servo_correction_output.instance.set_number("positionServoCentral",servo_central_position)
            servo_correction_output.instance.set_number("positionServoLeft",servo_left_position)
            servo_correction_output.instance.set_number("positionServoRight",servo_right_position)
            servo_correction_output.write()
            
            print("Sent position -> (CENTRAL : {}º || LEFT : {}º || RIGHT : {}º)".format(servo_central_position,servo_left_position,servo_right_position))
 
	
