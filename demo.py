import argparse
import parameters

parser = argparse.ArgumentParser()
parser.add_argument("--s", help="System mode [Default: Mode simulator]", action="store_true", default=False, required=False)

args = parser.parse_args()
simulator_mode = args.s #if fals, the system is in "real world" mode

if simulator_mode == True:
    print("Modo simulador")
elif simulator_mode == False:
    print("Modo real")

print(float(parameters.CTE_PITCH_PROPORTIONALITY))