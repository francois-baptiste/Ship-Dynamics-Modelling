# Modeling Ship and variable data over maps.
# Python Version: 2.7.12

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import helper
import math
import data_analysis
from vast import models
'''
import django.middleware.csrf
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.forms.models import model_to_dict
'''
import json
from vast.scrappers import bunkerscrapping
from datetime import datetime
'''
from django.contrib import messages
from django.template import RequestContext
from django.core import serializers
from django.contrib.auth.models import User
'''

class Ship_Model:
	
	def __init__(self, voyage = None):
		if not voyage:
			self.foc_factors = {
				'rpm_power' : 3,
				'displacement_power'  : 0.2,
				'constant' : 0.000000538426455,
			}

			self.fw_speed_factors = {
				'rpm_power' : 0.8,
				'displacement_power'  : -0.2,
				'constant' : 0.03398,
			}

			# INCREASEING HW, HS DECREASES RETARDATION
			self.weather_factors = {
				'Hw' : 4.0,
				'Cr' : math.pow(10.0, -5),
				'Hs' : 2 * 4.0,
				'cp' : 0.04
			}
		else:
			self.voyage = voyage
			if voyage.constants:
				print voyage.constants
				voyage_constants = json.loads( voyage.constants )
				print voyage_constants['fw_speed_factors']
				self.foc_factors = voyage_constants['foc_factors']
				self.fw_speed_factors = voyage_constants['fw_speed_factors']
				self.weather_factors = voyage_constants['weather_factors']
			else:
				self.learn_ship_model()
				voyage=models.Voyage.objects.filter(id=self.voyage.id).first()
				constant={}
				constant['foc_factors']			=	self.foc_factors
				constant['fw_speed_factors']	=	self.fw_speed_factors
				constant['weather_factors']		=	self.weather_factors

				voyage.constants=json.dumps(constant)
				voyage.save()
				print constant

	def learn_ship_model(self):
		constants = data_analysis.get_constants(self.voyage)
		print constants
		self.foc_factors = constants['foc_factors']
		self.fw_speed_factors = constants['fw_speed_factors']
		self.weather_factors = constants['weather_factors']
		
	def find_foc(self, rpm, displacement, steaming_hours):
		rpm_power = self.foc_factors['rpm_power']
		displacement_power = self.foc_factors['displacement_power']
		constant = self.foc_factors['constant']
		
		return constant * np.power(displacement, displacement_power) * np.power(rpm, rpm_power ) * steaming_hours

	def find_fw_speed(self, rpm, displacement):
		rpm_power = self.fw_speed_factors['rpm_power']
		displacement_power = self.fw_speed_factors['displacement_power']
		constant = self.fw_speed_factors['constant']
		
		return constant * np.power(rpm, rpm_power) * np.power(displacement, displacement_power)
	
	def find_aw_speed(self, rpm, displacement, weather):
		fw_speed = self.find_fw_speed(rpm, displacement)
		aw_speed = self.find_aw_speed_from_fw_speed(fw_speed, weather)
		return aw_speed

	def find_rpm_from_aw_speed(self, aw_speed, displacement, weather):
		fw_speed = self.find_fw_speed_from_aw_speed(aw_speed, weather)
		rpm = self.find_rpm_from_fw_speed(fw_speed, displacement)
		return rpm

	def find_aw_speed_from_fw_speed(self, fw_speed, weather):
		factor1, factor2, factor3, factor4, current_factor = self.find_retardation_factors(weather)

		# print "FACTORS", factor1, factor2, factor3, factor4

		aw_speed = fw_speed * factor1 * factor2 * factor3 + factor4 + current_factor

		return aw_speed

	def find_fw_speed_from_aw_speed(self, aw_speed, weather):
		factor1, factor2, factor3, factor4, current_factor = self.find_retardation_factors(weather)
		fw_speed = (aw_speed - factor4 - current_factor) / (factor1 * factor2 * factor3)
		return fw_speed

	def find_rpm_from_fw_speed(self, fw_speed, displacement):
		fws = self.fw_speed_factors
		rpm_raised = fw_speed / (fws['constant'] * np.power( displacement, fws['displacement_power'] ))
		rpm = np.power( rpm_raised, (1 / fws['rpm_power']) )
		return rpm

	def find_retardation_factors(self, weather):
		wf = self.weather_factors

		theta_wave = weather['wave_direction']
		theta_wind = weather['wind_direction']
		theta_swell = weather['swell_direction']

		wave_height = weather['wave_height']
		wind_speed = weather['wind_speed_kts']
		swell_height = weather['swell_height']

		_, gw_theta, _ = helper.theta_funcs(theta_wave)
		factor1 = np.power(1 + gw_theta * np.power( (wave_height/wf['Hw']),2.0 ), -0.33 )

		_, _, sin_theta_r = helper.theta_funcs(theta_wind)
		factor2 = np.power( (1 + wf['Cr'] * np.power( (wind_speed * sin_theta_r), 3.0 ) ), -0.5 )

		gs_theta, _, _ = helper.theta_funcs(theta_swell)
		factor3 = np.power(1 + gs_theta * np.power( (swell_height/wf['Hs']),2.0 ), -0.33 )

		factor4 = wf['cp'] * wind_speed * np.cos( np.radians(theta_wind + 180.0 ))
		current_factor = weather['current_speed_kts'] * np.cos( np.radians (weather['current_direction']) )
		# print "current factor--------------",current_factor
		return [factor1, factor2, factor3, factor4, current_factor]
	
def do_it():
	print "nskdn"
	voyage=models.Voyage.objects.filter(id=242).first()
	sm = Ship_Model(voyage)
	
	weather = {
		'wave_height'  : 0,
		'wave_direction' : 0,
		'swell_height' : 0,
		'swell_direction' : 0,
		'wind_speed_kts' : 0,
		'wind_direction' : 0,
		'current_speed_kts' : 0,
		'current_direction' : 0
	}
	
	rpm = 83
	displacement = 330000
	steaming_hours = 24

	foc = sm.find_foc(rpm, displacement, steaming_hours)
	fw_speed = sm.find_fw_speed(rpm, displacement)
	aw_speed = sm.find_aw_speed(rpm, displacement, weather)
	new_fw_speed = sm.find_fw_speed_from_aw_speed(aw_speed, weather)
	new_rpm = sm.find_rpm_from_aw_speed(aw_speed, displacement, weather)
	print foc, fw_speed, aw_speed, new_fw_speed, new_rpm

	