import json
import random
import time
from datetime import datetime
import os
from flask import Flask, Response, render_template,request,redirect,url_for
import rticonnextdds_connector as rti
from .. import parameters

application = Flask(__name__)
random.seed()  # Initialize the random number generator

#HEIGHT

ctePIDHeightProp=parameters.CTE_HEIGHT_PROPORTIONALITY
ctePIDHeightInt=parameters.CTE_HEIGHT_INTEGRATION
ctePIDHeightDer=parameters.CTE_HEIGHT_DERIVATION

#PITCH
ctePIDPitchProp=parameters.CTE_PITCH_PROPORTIONALITY
ctePIDPitchInt=parameters.CTE_PITCH_INTEGRATION
ctePIDPitchDer=parameters.CTE_PITCH_DERIVATION

#ROLL
ctePIDRollProp=parameters.CTE_ROLL_PROPORTIONALITY
ctePIDRollInt=parameters.CTE_ROLL_INTEGRATION
ctePIDRollDer=parameters.CTE_ROLL_DERIVATION


@application.route('/')
def index():
    global ctePIDHeightProp,ctePIDHeightInt,ctePIDHeightDer,ctePIDPitchProp,ctePIDPitchInt,ctePIDPitchDer,ctePIDRollProp,ctePIDRollInt,ctePIDRollDer
    return render_template('index.html', ctePIDHeightProp=ctePIDHeightProp,ctePIDHeightInt=ctePIDHeightInt,
    ctePIDHeightDer=ctePIDHeightDer,ctePIDPitchProp=ctePIDPitchProp,ctePIDPitchInt=ctePIDPitchInt,ctePIDPitchDer=ctePIDPitchDer,
    ctePIDRollProp=ctePIDRollProp,ctePIDRollInt=ctePIDRollInt,ctePIDRollDer=ctePIDRollDer)


@application.route('/chart-data-GPS')
def chart_data_GPS():

    def read_data(source):
        source.wait()
        source.take()

        for sample in source.samples.valid_data_iter:
            data = sample.get_dictionary()
            valueLat = data["latitude"]
            valueLong = data["longitude"]
            valueSpeed = data["speed"]
            json_data = json.dumps(
                {'time': datetime.now().strftime('%H:%M:%S'),'latitude': valueLat, 'longitude': valueLong, 'speed':valueSpeed})
            return json_data

    def generate_data():
        global inputGPS
        with rti.open_connector(config_name="MyParticipantLibrary::Debug",  url="../DDS.xml") as connector:

            inputGPS = connector.get_input("Debug_Sub::DebugReaderGPS")
            inputGPS.wait_for_publications()

            while True:
                json_env = read_data(inputGPS)
                yield f"data:{json_env}\n\n"
                time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

@application.route("/", methods=["GET","POST"])
def show_submitctes_form():
    global ctePIDHeightProp,ctePIDHeightInt,ctePIDHeightDer,ctePIDPitchProp,ctePIDPitchInt,ctePIDPitchDer,ctePIDRollProp,ctePIDRollInt,ctePIDRollDer
    if request.method == 'POST':
        f= open("CtesChanges.txt","a+")
        ctePIDHeightProp = float(request.form['ctePIDheight1'])
        ctePIDHeightInt = float(request.form['ctePIDheight2'])
        ctePIDHeightDer = float(request.form['ctePIDheight3'])

        ctePIDPitchProp = float(request.form['ctePIDpitch1'])
        ctePIDPitchInt = float(request.form['ctePIDpitch2'])
        ctePIDPitchDer = float(request.form['ctePIDpitch3'])

        ctePIDRollProp = float(request.form['ctePIDroll1'])
        ctePIDRollInt = float(request.form['ctePIDroll2'])
        ctePIDRollDer = float(request.form['ctePIDroll3'])

        f.write("Ctes changed:\n")

        f.write("\t -> Height-P: %f  \n" % ctePIDHeightProp)
        f.write("\t -> Height-I: %f  \n" % ctePIDHeightInt)
        f.write("\t -> Height-D: %f  \n\n" % ctePIDHeightDer)
        
        f.write("\t -> Pitch-P: %f  \n" % ctePIDPitchProp)
        f.write("\t -> Pitch-I: %f  \n" % ctePIDPitchInt)
        f.write("\t -> Pitch-D: %f  \n\n" % ctePIDPitchDer)
        
        f.write("\t -> Roll-P: %f  \n" % ctePIDRollProp)
        f.write("\t -> Roll-I: %f  \n" % ctePIDRollInt)
        f.write("\t -> Roll-D: %f  \n\n" % ctePIDRollDer)
        
        f.close()
        generate_data()
    return render_template('index.html', ctePIDHeightProp=ctePIDHeightProp,ctePIDHeightInt=ctePIDHeightInt,
    ctePIDHeightDer=ctePIDHeightDer,ctePIDPitchProp=ctePIDPitchProp,ctePIDPitchInt=ctePIDPitchInt,ctePIDPitchDer=ctePIDPitchDer,
    ctePIDRollProp=ctePIDRollProp,ctePIDRollInt=ctePIDRollInt,ctePIDRollDer=ctePIDRollDer)

def generate_data():
        with rti.open_connector(config_name="MyParticipantLibrary::Debug",  url= "../DDS.xml") as connector:
            global ctePIDHeightProp,ctePIDHeightInt,ctePIDHeightDer,ctePIDPitchProp,ctePIDPitchInt,ctePIDPitchDer,ctePIDRollProp,ctePIDRollInt,ctePIDRollDer
            outputHeight = connector.get_output("Debug_Pub::DebugWriterCtesHeight")
            outputPitch = connector.get_output("Debug_Pub::DebugWriterCtesPitch")
            outputRoll = connector.get_output("Debug_Pub::DebugWriterCtesRoll")
            
            outputHeight.instance.set_number("cte_PID_Height_prop", ctePIDHeightProp)
            outputHeight.instance.set_number("cte_PID_Height_der", ctePIDHeightDer)
            outputHeight.instance.set_number("cte_PID_Height_int", ctePIDHeightInt)
            outputHeight.write()
            outputPitch.instance.set_number("cte_PID_Pitch_prop", ctePIDPitchProp)
            outputPitch.instance.set_number("cte_PID_Pitch_der", ctePIDPitchDer)
            outputPitch.instance.set_number("cte_PID_Pitch_int", ctePIDPitchInt)
            outputPitch.write()
            outputRoll.instance.set_number("cte_PID_Roll_prop", ctePIDRollProp)
            outputRoll.instance.set_number("cte_PID_Roll_der", ctePIDRollDer)
            outputRoll.instance.set_number("cte_PID_Roll_int", ctePIDRollInt)
            outputRoll.write()

            




@application.route('/chart-data-height')
def chart_data_height():
    def read_data(source, inputName):
        #print("\nWaiting for ",inputName.upper()," data...")
        source.wait()
        source.take()	

        for sample in source.samples.valid_data_iter:

            data = sample.get_dictionary()
            value = data[inputName]
            #print("Received ",inputName.upper(), ": " ,value) 
            return value	
            
    def generate_data():
        with rti.open_connector(config_name="MyParticipantLibrary::Debug",  url= "../DDS.xml") as connector:


            inputHeight = connector.get_input("Debug_Sub::DebugReaderHeight")
            #print("Waiting for publications...")
            inputHeight.wait_for_publications()

            while True:
                json_data = json.dumps({'time': datetime.now().strftime('%H:%M:%S'), 'value':read_data(inputHeight,"height") })
                yield f"data:{json_data}\n\n"
                time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

@application.route('/chart-data-pitch')
def chart_data_pitch():
    def read_data(source, inputName):
        #print("\nWaiting for ",inputName.upper()," data...")
        source.wait()
        source.take()	

        for sample in source.samples.valid_data_iter:
            data = sample.get_dictionary()
            value = data[inputName]
            #print("Received ",inputName.upper(), ": " ,value) 
            return value	
            
    def generate_data():
        with rti.open_connector(config_name="MyParticipantLibrary::Debug",  url= "../DDS.xml") as connector:


            inputPitch = connector.get_input("Debug_Sub::DebugReaderPitch")
            #print("Waiting for publications...")
            inputPitch.wait_for_publications()

            while True:
                json_data = json.dumps({'time': datetime.now().strftime('%H:%M:%S'), 'value':read_data(inputPitch,"pitch") })
                yield f"data:{json_data}\n\n"
                time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

@application.route('/chart-data-roll')
def chart_data_roll():
    def read_data(source, inputName):
        #print("\nWaiting for ",inputName.upper()," data...")
        source.wait()
        source.take()	

        for sample in source.samples.valid_data_iter:
            data = sample.get_dictionary()
            value = data[inputName]
            #print("Received ",inputName.upper(), ": " ,value) 
            return value	
            
    def generate_data():
        with rti.open_connector(config_name="MyParticipantLibrary::Debug",  url= "../DDS.xml") as connector:


            inputRoll = connector.get_input("Debug_Sub::DebugReaderRoll")
            #print("Waiting for publications...")
            inputRoll.wait_for_publications()

            while True:
                json_data = json.dumps({'time': datetime.now().strftime('%H:%M:%S'), 'value':read_data(inputRoll,"roll") })
                yield f"data:{json_data}\n\n"
                time.sleep(1)

    return Response(generate_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    application.run(host=os.getenv('IP', '0.0.0.0'),  port=int(os.getenv('PORT',3333)), debug=True, threaded=True)
