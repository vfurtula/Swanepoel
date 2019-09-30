#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""



from matplotlib import pyplot as plt
from help_dialogs import Message_dialog

import os, sys, time, numpy, configparser
from methods import get_raw
from scipy import interpolate
from scipy.ndimage import filters as fi
from scipy.signal import argrelextrema



'''
## For Matplotlib fonts
from matplotlib import rc
## for LaTeX style use:
rc("text", usetex=True)
rc("font", family="serif")
'''

class Get_Tmax_Tmin:
	
	def __init__(self, cwd):
		print('method __init__ in Get_Tmax_Tmin runs...')
		self.gw = get_raw.Get_raw(cwd)
		
		
	def extremas(self,x_all,y_all):
		print('method extremas runs...')
		# Find the correct indicies for the gaussian filter
		GaussFilt=numpy.array([])
		x_all_=numpy.array([])
		y_all_=numpy.array([])
		
		for tal in range(len(self.gw.gaussian_borders)-1):
			
			idx = numpy.where((self.gw.gaussian_borders[tal]<=x_all)&(self.gw.gaussian_borders[tal+1]>x_all))[0]
			# Perform gaussian filtering in order to remove noise
			GaussFilt=numpy.append(GaussFilt, fi.gaussian_filter1d(y_all[idx], self.gw.gaussian_factors[tal], mode='nearest'))
			
			# Redefine x_all and y_all since we have cut out some of the original data
			x_all_ = numpy.append(x_all_, x_all[idx])
			y_all_ = numpy.append(y_all_, y_all[idx])
			
		# Find the locations (indicies) of min and max
		# for local maxima
		max_loc=argrelextrema(GaussFilt, numpy.greater)[0]
		
		# and for local minima
		min_loc=argrelextrema(GaussFilt, numpy.less)[0]
			
		x_max=x_all_[max_loc]
		y_max=y_all_[max_loc]
		x_min=x_all_[min_loc]
		y_min=y_all_[min_loc]
		
		return x_min, y_min, x_max, y_max
		
		
	def interp_T(self, x_min, y_min, x_max, y_max, *argv):
		print('method interp_T runs...')
		
		if len(argv)==1:
			corr_slit=argv[0]
		else:
			corr_slit=0
		
		# convert all to nm
		x_min=1239.84187/x_min
		idx = numpy.argsort(x_min)
		x_min = x_min[idx]
		y_min = y_min[idx]
		
		x_max = 1239.84187/x_max
		idx = numpy.argsort(x_max)
		x_max = x_max[idx]
		y_max = y_max[idx]
		
		print(len(x_min))
		print(len(y_min))
		print(len(x_max))
		print(len(y_max))
		
		if len(x_min)==0 or len(x_max)==0 or len(y_min)==0 or len(y_max)==0:
			raise Exception("No extrema found in the local method interp_T!\n\nTry following steps:\n1. Change the Gaussian factors or borders.\n2. Include wider data range.\n3. Try a different data set.")
		
		if (min(x_min)<min(x_max)) and (max(x_min)>max(x_max)):
			y_max = y_max+(y_max*corr_slit/numpy.diff(x_min))**2
			y_min = numpy.array([y_min[0]]+list(y_min[1:-1]-(y_min[1:-1]*corr_slit/numpy.diff(x_max))**2)+[y_min[-1]])
			x_max_ = x_max
			x_min_ = x_min[1:-1]
			
		elif (min(x_min)<min(x_max)) and (max(x_min)<max(x_max)):
			y_max = numpy.array(list(y_max[:-1]+(y_max[:-1]*corr_slit/numpy.diff(x_min))**2)+[y_max[-1]])
			y_min = numpy.array([y_min[0]]+list(y_min[1:]-(y_min[1:]*corr_slit/numpy.diff(x_max))**2))
			x_max_ = x_max[:-1]
			x_min_ = x_min[1:]
			
		elif (min(x_min)>min(x_max)) and (max(x_min)<max(x_max)):
			y_max = numpy.array([y_max[0]]+list(y_max[1:-1]+(y_max[1:-1]*corr_slit/numpy.diff(x_min))**2)+[y_max[-1]])
			y_min = y_min-(y_min*corr_slit/numpy.diff(x_max))**2
			x_max_ = x_max[1:-1]
			x_min_ = x_min
			
		elif (min(x_min)>min(x_max)) and (max(x_min)>max(x_max)):
			y_max = numpy.array([y_max[0]]+list(y_max[1:]+(y_max[1:]*corr_slit/numpy.diff(x_min))**2))
			y_min = numpy.array(list(y_min[:-1]-(y_min[:-1]*corr_slit/numpy.diff(x_max))**2)+[y_min[-1]])
			x_max_ = x_max[1:]
			x_min_ = x_min[:-1]
		
		# convert back to eV
		x_min = 1239.84187/x_min
		idx = numpy.argsort(x_min)
		x_min = x_min[idx]
		y_min = y_min[idx]
		
		x_max = 1239.84187/x_max
		idx = numpy.argsort(x_max)
		x_max = x_max[idx]
		y_max = y_max[idx]
		
		common_xaxis=numpy.sort(numpy.append(1239.84187/x_min_,1239.84187/x_max_))
		
		if self.gw.fit_linear_spline=='spline':
			fmax = interpolate.splrep(x_max, y_max, k=3, s=0)
			fmin = interpolate.splrep(x_min, y_min, k=3, s=0)
			
		elif self.gw.fit_linear_spline=='linear':
			fmax = interpolate.splrep(x_max, y_max, k=1, s=0)
			fmin = interpolate.splrep(x_min, y_min, k=1, s=0)
		
		Tmax = interpolate.splev(common_xaxis, fmax, der=0)
		Tmin = interpolate.splev(common_xaxis, fmin, der=0)
		
		return common_xaxis, Tmin, Tmax
		
		
	def get_T_alpha(self):
		print('method get_T_alpha runs...')
		
		if self.gw.loadSubFilmFTIR_check or self.gw.loadSubFilmOlis_check:
			
			x_min, y_min, x_max, y_max = self.extremas(self.gw.x_Tsubfilm, self.gw.y_Tsubfilm)
			
			# Find the extrema points and create a common x-axis
			common_xaxis, Tmin, Tmax = self.interp_T(x_min, y_min, x_max, y_max)
			extremas_first = [x_min, y_min, x_max, y_max]
			com_axisTminTmax_first=[common_xaxis, Tmin, Tmax]

			indx = numpy.where((self.gw.x_Tsubfilm<=self.gw.gaussian_borders[-1])&(self.gw.x_Tsubfilm>=self.gw.gaussian_borders[0]))[0]
			
			# Create T_alpha x-axis and ADD interference-free points 
			common_xaxis_fit = self.gw.x_Tsubfilm[indx]
			T_all_minmax = self.gw.y_Tsubfilm[indx]
			T_alpha_flatten = self.gw.y_Tsubfilm[indx]

			# 2 iterationer plejer at vaere nok at flade ud transmissions kurven
			for tal in range(2):
				print( ''.join(["Iteration number (from the method get_T_alpha): ",str(tal)]) )
				# Calculate T_alpha for the previously determined extrema points
				T_al=(Tmax+Tmin)/2.0
				
				# Perform spline to determine T_alpha in the newly found x-axis range
				if self.gw.fit_linear_spline=='spline':
					f=interpolate.splrep(common_xaxis, T_al, k=3, s=0)
				  
				elif self.gw.fit_linear_spline=='linear':
					f=interpolate.splrep(common_xaxis, T_al, k=1, s=0)
				  
				T_alpha = interpolate.splev(common_xaxis_fit, f, der=0)
				
				if tal==0:
					T_alpha_first=T_alpha
				
				# Substract T_alpha from the T_r in order to flatten out raw transmission data
				# and only to leave periodic oscillations 
				T_alpha_flatten=T_alpha_flatten-T_alpha
				
				# Calculate NEW extrema points from the flatten curve
				x_min, y_min, x_max, y_max = self.extremas(common_xaxis_fit, T_alpha_flatten)

				# Find the extrema points and create a common x-axis
				common_xaxis, Tmin, Tmax = self.interp_T(x_min, y_min, x_max, y_max)
			extremas_flatten = [x_min, y_min, x_max, y_max]
			
			# Find correct indicies of NEW extrema points relative to the original T_r data 
			idx=numpy.array([],dtype=int)
			for tal in x_min:
				idx=numpy.append(idx,numpy.where(common_xaxis_fit==tal)[0])
			y_min=T_all_minmax[idx]
			
			idx=numpy.array([],dtype=int)
			for tal in x_max:
				idx=numpy.append(idx,numpy.where(common_xaxis_fit==tal)[0])
			y_max=T_all_minmax[idx]
			
			extremas_final = [x_min, y_min, x_max, y_max]
			
			common_xaxis, Tmin, Tmax = self.interp_T(x_min, y_min, x_max, y_max, self.gw.corr_slit)
			# Calculate T_alpha for the previously determined extrema points
			T_al=(Tmax+Tmin)/2.0
			# Perform spline to determine T_alpha in the newly found x-axis range
			if self.gw.fit_linear_spline=='spline':
				f=interpolate.splrep(common_xaxis, T_al, k=3, s=0)
			elif self.gw.fit_linear_spline=='linear':
				f=interpolate.splrep(common_xaxis, T_al, k=1, s=0)
			T_alpha_final = interpolate.splev(common_xaxis_fit, f, der=0)
				
			# Save the required data in new lists and make a return
			comax_alph_TalTalflat = [common_xaxis_fit, T_alpha_first, T_alpha_final, T_alpha_flatten]
			com_axisTminTmax_final=[common_xaxis, Tmin, Tmax]
			all_extremas = [extremas_first, extremas_final, extremas_flatten]
	        
			return indx, comax_alph_TalTalflat, com_axisTminTmax_final, all_extremas
		
		
	def fit_Ts_to_data(self,common_xaxis):
		print('method fit_Ts_to_data runs...')

		if self.gw.fit_linear_spline=='linear':
			f = interpolate.splrep(self.gw.x_Tsub, self.gw.y_Tsub, k=1, s=0)
			
		elif self.gw.fit_linear_spline=='spline':
			f = interpolate.splrep(self.gw.x_Tsub, self.gw.y_Tsub, k=3, s=0)
			
		try:
			fit_yaxis = interpolate.splev(common_xaxis, f, der=0)
		except Exception:
			raise Exception('interpolate.splev fails in the local method fit_Ts_to_data')

		return common_xaxis, fit_yaxis
		
		
	def make_plots(self):
		print('method make_plots in Get_Tmax_Tmin runs...')
		
		indx, comax_alph_TalTalflat, com_axisTminTmax_final, all_extremas = self.get_T_alpha()
		
		extremas_first, extremas_final, extremas_flatten = all_extremas
		common_xaxis, Tmin, Tmax = com_axisTminTmax_final
		common_xaxis_alpha, T_alpha_first, T_alpha_final, T_alpha_flatten = comax_alph_TalTalflat
		
		x_min, y_min, x_max, y_max=[extremas_first[:][0],extremas_first[:][1],extremas_first[:][2],extremas_first[:][3]]
		x_min_, y_min_, x_max_, y_max_=[extremas_final[:][0],extremas_final[:][1],extremas_final[:][2],extremas_final[:][3]]
		x_min__, y_min__, x_max__, y_max__=[extremas_flatten[:][0],extremas_flatten[:][1],extremas_flatten[:][2],extremas_flatten[:][3]]
		
		########################################################################
		pass_plots=[]
	
		plt.figure(figsize=(15,10))
		
		if self.gw.plot_X=='eV':
			plt.plot(x_min, y_min, 'r-', label = "T_min first")
			plt.plot(x_max, y_max, 'b-', label = "T_max first")
			plt.plot(x_min_, y_min_, 'r--', label = "T_min final")
			plt.plot(x_max_, y_max_, 'b--', label = "T_max final")
			plt.plot(self.gw.x_Tsubfilm,self.gw.y_Tsubfilm,'k-', label = "T_raw data")
			plt.plot(common_xaxis_alpha,T_alpha_first,'m-', label = "T_alpha_first")
			plt.plot(common_xaxis_alpha,T_alpha_final,'g-', label = "T_alpha_final")
			plt.plot(self.gw.x_Tsubfilm[indx[-1]+1:], self.gw.y_Tsubfilm[indx[-1]+1:], 'co', label = ''.join(['fringes-free region']))
			string_lab1 = ''.join(['T_min interp (', self.gw.fit_linear_spline , ')'])
			plt.plot(common_xaxis, Tmin, 'ro--', label = string_lab1)
			string_lab2 = ''.join(['T_max interp (', self.gw.fit_linear_spline , ')'])
			plt.plot(common_xaxis, Tmax, 'bo--', label = string_lab2)
			plt.xlabel("E, eV", fontsize=20)
			
		elif self.gw.plot_X=='nm':
			plt.plot(1239.84187/numpy.array(x_min), y_min, 'r-', label = "T_min first")
			plt.plot(1239.84187/numpy.array(x_max), y_max, 'b-', label = "T_max first")
			plt.plot(1239.84187/numpy.array(x_min_), y_min_, 'r--', label = "T_min final")
			plt.plot(1239.84187/numpy.array(x_max_), y_max_, 'b--', label = "T_max final")
			plt.plot(1239.84187/self.gw.x_Tsubfilm,self.gw.y_Tsubfilm,'k-', label = "T_raw data")
			plt.plot(1239.84187/common_xaxis_alpha,T_alpha_first,'m-', label = "T_alpha_first")
			plt.plot(1239.84187/common_xaxis_alpha,T_alpha_final,'g-', label = "T_alpha_final")
			plt.plot(1239.84187/self.gw.x_Tsubfilm[indx[-1]+1:], self.gw.y_Tsubfilm[indx[-1]+1:], 'co', label = ''.join(['fringes-free region']))
			string_lab1 = ''.join(['T_min interp (', self.gw.fit_linear_spline , ')'])
			plt.plot(1239.84187/numpy.array(common_xaxis), Tmin, 'ro--', label = string_lab1)
			string_lab2 = ''.join(['T_max interp (', self.gw.fit_linear_spline , ')'])
			plt.plot(1239.84187/numpy.array(common_xaxis), Tmax, 'bo--', label = string_lab2)
			plt.xlabel("Wavelength, nm", fontsize=20)
			
		plt.ylabel("Tr", fontsize=20)
		plt.tick_params(axis="both", labelsize=20)
		#plt.ylim([0,1])
		#plt.xlim([0,4])
		l=plt.legend(loc=1, fontsize=15)
		l.draw_frame(False)

		if self.gw.save_figs:
			string_2 = ''.join([self.gw.filename,'_Tr_subfilm (', self.gw.fit_linear_spline , ')_',self.gw.timetrace, '.png'])
			plt.savefig(string_2)
			pass_plots.extend([string_2])

		########################################################################
		
		x_Ts, y_Ts = self.fit_Ts_to_data(common_xaxis)
		
		plt.figure(figsize=(15,10))
		
		if self.gw.plot_X=='eV':
			plt.plot(x_Ts,y_Ts,'k-')
			plt.xlabel("E, eV", fontsize=20)
			
		elif self.gw.plot_X=='nm':
			plt.plot(1239.84187/numpy.array(x_Ts),y_Ts,'k-')
			plt.xlabel("Wavelength, nm", fontsize=20)
			
		plt.ylabel("Tr", fontsize=20)
		plt.tick_params(axis="both", labelsize=20)
		#plt.ylim([0,1])
		#plt.xlim([0,11000])
		plt.title("Tr (SUBSTRATE) for selected [Tmin, Tmax] region")
		#l=plt.legend(loc=1, fontsize=15)
		#l.draw_frame(False)
		
		if self.gw.save_figs:
			string_3 = ''.join([self.gw.filename, '_Tr_sub (', self.gw.fit_linear_spline , ')_',self.gw.timetrace, '.png'])
			plt.savefig(string_3)
			pass_plots.extend([string_2])
		
		########################################################################
		
		plt.figure(figsize=(15,10))
		if self.gw.plot_X=='eV':
			plt.plot(common_xaxis_alpha,T_alpha_flatten,'k-', label = "T_alpha flatten")
			plt.plot(x_min__, y_min__, 'ro', label = "T_min flatten")
			plt.plot(x_max__, y_max__, 'bo', label = "T_max flatten")
			plt.xlabel("E, eV", fontsize=20)
			
		elif self.gw.plot_X=='nm':
			plt.plot(1239.84187/numpy.array(common_xaxis_alpha),T_alpha_flatten,'k-', label = "T_alpha flatten")
			plt.plot(1239.84187/numpy.array(x_min__), y_min__, 'ro', label = "T_min flatten")
			plt.plot(1239.84187/numpy.array(x_max__), y_max__, 'bo', label = "T_max flatten")
			plt.xlabel("Wavelength, nm", fontsize=20)
			
		plt.ylabel("Tr", fontsize=20)
		plt.tick_params(axis="both", labelsize=20)
		#plt.yticks( numpy.linspace(0,1,11) )
		#plt.xticks( numpy.linspace(0,11000,12) )
		#plt.ylim([0,1])
		#plt.xlim([0,4])
		l=plt.legend(loc=1, fontsize=15)
		l.draw_frame(False)
		
		if self.gw.save_figs:
			string_4 = ''.join([self.gw.filename, '_Tr_flatten (', self.gw.fit_linear_spline , ')_',self.gw.timetrace, '.png'])
			plt.savefig(string_4)
			pass_plots.extend([string_4])
		
		return pass_plots
	
	
	def show_plots(self):
		
		plt.show()
		
		
	def close_plots(self):
		
		plt.close()
		
		
		
		
if __name__ == "__main__":
	
	get_class=Get_Tmax_Tmin()
	get_class.make_plots()
	get_class.show_plots()
	
	
	
