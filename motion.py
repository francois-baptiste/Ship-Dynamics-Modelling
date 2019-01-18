# Module - Calculate roll and pitch of a vessel.
# Project approach: 1.0
# Master Project: ship_model.py
# Base Project: motion.py
# Python Version: 2.7.12

from math import sin, tan, cos, exp
import motion_module as module
import matplotlib.pyplot as plt
import sys, os, csv

'''
Index of Variables/Terms/Constants used throughout the module and base project:
------------------------------------------------------------------------------------------------------------------------------
# GZ 								| The Righting arm. 													
# BM 								| Buoyant Force.
# GM 								| Metacentric height.
------------------------------------------------------------------------------------------------------------------------------
# const_roll 						| Constant value of proportionality in the theta calculation for roll   
# const_pitch 						| Constant value of proportionality in the theta calculation for pitch  
# const_density 					| Density of the saline sea water. 										           | 1.025
# const_pi 							| Value of geometric constant 'PI'. 		 							           | 22/7
------------------------------------------------------------------------------------------------------------------------------
# wind_force, wf 					| Force of the Wind in beaufort Scale value.
# w_dir 							| Direction of te wind.
# wind_direction, wind_angle 		| Angle of inclination of the w_dir vector w.r.t. ship in degree.
------------------------------------------------------------------------------------------------------------------------------
# wv_direction, wv_dir, wvd 		| Direction of wave.
# wave_direction, wave_angle 		| Direction of wave w.r.t. ship in degree.
# wave_height						| Amplitude of the wave.
# per 								| Duration of the wave in units 'seconds'.
------------------------------------------------------------------------------------------------------------------------------
# Displacement 						| Displacement of the water due to ship's weight in cubic meter.
# mass 								| Mass of the ship based on volumetric density displaced and saline water density.
# ship_course, sc 					| Calculated ship course depending on the longitude and latitude.
# area 								| Ship's estimated surface area.
------------------------------------------------------------------------------------------------------------------------------
# kneel_angle 						| angle of deviation of the buoyent force from the metacentric height.
------------------------------------------------------------------------------------------------------------------------------
'''

# Hard-code of variables per ship dimensions inclusive of universal constants.
GM = 1.5
area = 10213.29
displacement =  127355
const_pi = 22/7
const_density = 1.025

# Constants geberated by module file.
const_pi = 22/7
mass = module.Mass(const_density, displacement)
const_roll, const_pitch = module.regression()

# Function to calculate Kneel angle for pitch.
def theta_pitch(wind_speed, w_dir, sc, wave_height, wv_dir, per):
	wind_direction = module.calc_windangle(w_dir, sc)*(const_pi/180)  
	wave_direction = module.calc_waveangle(wv_dir, sc)*(const_pi/180)
	spectrum = module.jonswap(wave_height, per)
	kneel_angle = (const_pitch*cos(spectrum)*cos(wave_direction)/mass*module.beaufort(wind_speed)*cos(wind_direction))
	return kneel_angle

# Function to calculate Kneel angle for roll.
def theta_roll(wind_speed, w_dir, sc, wave_height, wv_dir, per):
	wind_direction = module.calc_windangle(w_dir, sc)*(const_pi/180)  
	wave_direction = module.calc_waveangle(wv_dir, sc)*(const_pi/180)
	spectrum = module.jonswap(wave_height, per)
	kneel_angle = (const_roll*cos(spectrum)*cos(wave_direction)/mass*module.beaufort(wind_speed)*cos(wind_direction))
	return kneel_angle

# Function to calculate pitch.
def calc_pitch(wind_speed, w_dir, sc, wave_height, wv_dir, per):
	angle = theta_pitch(wind_speed, w_dir, sc, wave_height, wv_dir, per)
	if(angle < 10.0):
		GZ = GM * sin(angle)
	else:
		GZ = sin(GM + 0.5*module.BM(area, displacement)*(tan(angle)**2))
	return abs(GZ)

# Function to calculate roll.
def calc_roll(wind_speed, w_dir, sc, wave_height, wv_dir, per):
	angle = theta_roll(wind_speed, w_dir, sc, wave_height, wv_dir, per)
	if(angle < 10.0):
		GZ = GM * sin(angle)
	else:
		GZ = sin(GM + 0.5*module.BM(area, displacement)*(tan(angle)**2))
	return abs(GZ)

# Function to call specific roll/pitch function based on wind and wave direction.
def calc_value(wind_speed, w_dir, sc, wave_height, wv_dir, per):
	wind_angle = module.calc_windangle(w_dir, sc)
	wave_angle = module.calc_waveangle(wv_dir, sc)
	wind_force = module.beaufort(wind_speed)
	
	if wind_angle < 0 or wave_angle < 0:
		wind_angle = wind_angle + 180
		wave_angle = wave_angle + 180
	elif wind_angle > 180 or wave_angle > 180:
		wind_angle = wind_angle - 180
		wave_angle = wave_angle - 180

	pitch = 0.0
	roll = 0.0

	if per == 0:
		return pitch , roll
	else: 
		pitch = calc_pitch(wind_force, w_dir, sc, wave_height, wv_dir, per)
		roll = calc_roll(wind_force, w_dir, sc, wave_height, wv_dir, per)
	# Swap for cross verification of roll always bigger than pitch.
		if (pitch>roll):
			temp = roll
			roll = pitch
			pitch = temp
	
	if (wind_angle >= 0) and (wind_angle < 60) or (wind_angle >= 120) and (wind_angle < 180) or (wind_angle >= 60) and (wind_angle < 120):
		return pitch , roll
	else:
		return pitch , roll

'''---------------------------------------------------------END OF MODULE--------------------------------------------------'''

# Module Tester Function.
'''
--------------------------------------------------------
 Input Value Order:   
 				1. 	Wind Speed
 				2. 	Wind Direction 
 				3. 	Ship Course (cog)
 				4. 	Wave Height
 				5.	Wave Direction
 				6. 	Tidal Time (per)
---------------------------------------------------------	
'''
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__file__ = 'Data/Seavoyager.csv'
result = []
def read():
	with open (os.path.join( __location__ , __file__), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			value = []
		#Fixing white spacing error in CSV Extracted Data.
			row[0] =row[0].replace('\xa0',' ')
			row[2] =row[2].replace('\xa0',' ')
			row[6] =row[6].replace('\xa0',' ')
			row[5] =row[5].replace('\xa0',' ')
			
			result.append(calc_value(float(row[0].strip()),  float(row[1].strip()), float(row[7].strip()), float(row[2].strip()), float(row[4].strip()), float(row[3].strip())))
			
read()
pitch = []
roll = []
for elem in result:
	print(elem)
	pitch.append(elem[0])
	roll.append(elem[1])

plt.plot(pitch)
plt.plot(roll)
plt.show()
