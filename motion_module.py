# Module - Calculate the Theta Constant of Proportionality based on historic voyage data.
# Module version: 1.0
# Python Version: 2.7.12

from math import asin, exp, cos
import numpy as np
import sys, os, csv
import matplotlib.pyplot as plt

'''
	Data File Name (__file__)		: 	Seavoyager Kozmino -Dickson_Recommended_2016-08-01-0930Z_2016-08-01-0930.csv
	Extension						: 	Comma Seprated Value (CSV)
	Data Version Type 				: 	Extracted data. 
		
					  					FILE INDEX	|		  VALUE NAME 		|	VALUE TYPE
									-------------------------------------------------------------
										Row[0] 		| 		wind_speed			| 		str 
										Row[1] 		| 		wind direction 		| 		str
										Row[2] 		| 		Wave height 		| 		str
										Row[3] 		| 		per 				| 		str
										Row[4] 		| 		wave direction 		| 		str
										Row[5] 		| 		roll 				| 		str
										Row[6] 		| 		pitch 				| 		str
										Row[7] 		| 		COG 				| 		str
									-------------------------------------------------------------


	*Note: for Variables/Terms/Constants Index refer main frame file.
	
'''

# Hard-coding of variables per ship dimensions and universal constants.
GM = 1.5
area = 10213.29
displacement = 127355
const_pi = 22/7
const_density = 1.025

# Declaration of current and data file path within the module.
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
__file__ = 'Data/Seavoyager.csv'

# Global Array varibales to store all the roll and pitch constants as a list.
roll_constant = []
pitch_constant = []

# Function to calculate Ship's Mass.
def Mass(const_density,displacement):
	return const_density*displacement

#Function to calculate Buoyant force.
def BM(area, displacement):
	return area/displacement

# Function to calculate the wave force based on wave spectrum.
def jonswap(wave_height, per):
	cir_freq = 2*const_pi/per
	Y = 3.3
	spectrum = ((320*(wave_height**2))/(per**4))*(cir_freq**(-5))*(exp((-1950/(per**4))*(cir_freq**(-4))))*(Y**4)
	return spectrum

# Function to calculate wind angle w.r.t Ship's course.
def calc_windangle(w_dir, ship_course):
	if (w_dir - ship_course > 180):
		wd = w_dir - ship_course - 360
	if (w_dir - ship_course < -180):
		wd = w_dir - ship_course + 360
	else:
		wd = w_dir - ship_course
	return wd

# Function to calculate wave angle w.r.t Ship's course.
def calc_waveangle(wv_direction, ship_course):
	if (wv_direction - ship_course > 180):
		wvd  = wv_direction - ship_course - 360
	if (wv_direction - ship_course < -180):
		wvd = wv_direction - ship_course + 360
	else:
		wvd = wv_direction - ship_course
	return wvd

# Function to convert wind speed in Wind Force.
def beaufort(wind_speed):
	if wind_speed<1.0:
		force = 0.0
		return force
	elif wind_speed>=1.0 and wind_speed<=3.0:
		force = 1.0
		return force
	elif wind_speed>=4.0 and wind_speed<=6.0:
		force = 2.0
		return force
	elif wind_speed>=7.0 and wind_speed<=10.0:
		force =  3.0
		return force
	elif wind_speed>=11.0 and wind_speed<=16.0:
		force =  4.0
		return force
	elif wind_speed>=17.0 and wind_speed<=21.0:
		force =  5.0
		return force
	elif wind_speed>=22.0 and wind_speed<=27.0:
		force =  6.0
		return force
	elif wind_speed>=28.0 and wind_speed<=33.0:
		force =  7.0
		return force
	elif wind_speed>=34.0 and wind_speed<=40.0:
		force =  8.0
		return force
	elif wind_speed>=41.0 and wind_speed<=47.0:
		force =  9.0
		return force
	elif wind_speed>=48.0 and wind_speed<=55.0:
		force = 10.0
		return force
	elif wind_speed>=56.0 and wind_speed<=63.0:
		force = 11.0
		return force
	else:
		force = 12.0
		return force

# Function to calculate the roll proportionality constant.
def rollc(GZ_roll, GM, M, wind_speed, wd, cog, wvd, spectrum):
	return (asin(GZ_roll/GM)*M)*beaufort(wind_speed)*cos(calc_windangle(wd, cog))/cos(spectrum)*cos(calc_waveangle(wvd, cog))

# Function to calculate the pitch proportionality constant.
def pitchc(GZ_pitch, GM, M, wind_speed, wd, cog, wvd, spectrum):
	return (asin(GZ_pitch/GM)*M)*beaufort(wind_speed)*cos(calc_windangle(wd, cog))/cos(spectrum)*cos(calc_waveangle(wvd, cog))

# Function to assign values to respective variables and call functions rollc(...) and pitchc(...).
def calc_assign_values(GZ_roll, GZ_pitch, height, per, wd, wvd, cog, wind_speed):
	M = Mass(const_density,displacement)
	if per==0:
		return roll_constant.append(0.0), pitch_constant.append(0.0)
	spectrum = jonswap(height, per)
	
	roll_constant.append(rollc(GZ_roll, GM, M, wind_speed, wd, cog, wvd, spectrum))
	pitch_constant.append(pitchc(GZ_pitch, GM, M, wind_speed, wd, cog, wvd, spectrum))

# Function to read the data file and pass it on to function calc_assign_values(...).
def read_csv():
	result = []
	with open (os.path.join( __location__ , __file__), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
		#Fixing white spacing error in CSV Extracted Data.
			row[0] =row[0].replace('\xa0',' ')
			row[1] =row[1].replace('\xa0',' ')
			row[2] =row[2].replace('\xa0',' ')
			row[3] =row[3].replace('\xa0',' ')
			row[4] =row[4].replace('\xa0',' ')
			row[5] =row[5].replace('\xa0',' ')
			row[6] =row[6].replace('\xa0',' ')
			row[7] =row[7].replace('\xa0',' ')
			result.append(calc_assign_values(float(row[5].strip()), float(row[6].strip()), float(row[2].strip()),float(row[3].strip()), float(row[4].strip()), float(row[1].strip()), float(row[7].strip()), float(row[0].strip())))
			

# Function to calculate and return the regression value of both pitch and roll's constant values.
def regression():
	read_csv()
	constant_roll = np.mean(roll_constant)
	constant_pitch = np.mean(pitch_constant)
	return constant_roll, constant_pitch

'''---------------------------------------------------------END OF MODULE--------------------------------------------------'''