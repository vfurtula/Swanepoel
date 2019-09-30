#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

import matplotlib.pyplot as plt
import os, sys, time, numpy, configparser

from itertools import groupby

from PyQt5.QtWidgets import QMessageBox

'''
## For Matplotlib fonts
from matplotlib import rc
## for LaTeX style use:
rc("text", usetex=True)
rc("font", family="serif")
'''

class Get_raw:
	
	def __init__(self,cwd):
		print('method __init__ in Get_raw runs...')
		
		# Initial read of the config file
		self.config = configparser.ConfigParser()
		self.cwd = cwd
		
		try:
			self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
			self.last_used_scan = self.config.get('LastScan','last_used_scan')
			
			self.loadSubOlis_str = self.config.get(self.last_used_scan,"loadsubolis").strip().split(':')[0]
			self.loadSubOlis_check = self.bool_(self.config.get(self.last_used_scan,'loadsubolis').strip().split(':')[1])
			self.loadSubFilmOlis_str = self.config.get(self.last_used_scan,'loadsubfilmolis').strip().split(':')[0]
			self.loadSubFilmOlis_check = self.bool_(self.config.get(self.last_used_scan,'loadsubfilmolis').strip().split(':')[1])
			self.loadSubFTIR_str = self.config.get(self.last_used_scan,'loadsubftir').strip().split(':')[0]
			self.loadSubFTIR_check = self.bool_(self.config.get(self.last_used_scan,'loadsubftir').strip().split(':')[1])
			self.loadSubFilmFTIR_str = self.config.get(self.last_used_scan,'loadsubfilmftir').strip().split(':')[0]
			self.loadSubFilmFTIR_check = self.bool_(self.config.get(self.last_used_scan,'loadsubfilmftir').strip().split(':')[1])
			self.fit_linear_spline = self.config.get(self.last_used_scan,'fit_linear_spline')
			self.gaussian_factors = [float(i) for i in self.config.get(self.last_used_scan,'gaussian_factors').strip().split(',')]
			self.gaussian_borders = [float(i) for i in self.config.get(self.last_used_scan,'gaussian_borders').strip().split(',')]
			self.ignore_data_pts = int(self.config.get(self.last_used_scan,'ignore_data_pts'))
			self.corr_slit = int(self.config.get(self.last_used_scan,'corr_slit'))
			self.fit_poly_order = int(self.config.get(self.last_used_scan,'fit_poly_order'))
			self.fit_poly_ranges = [float(i) for i in self.config.get(self.last_used_scan,'fit_poly_ranges').strip().split(':')[0].split(',')]
			self.fit_poly_ranges_check = self.bool_(self.config.get(self.last_used_scan,'fit_poly_ranges').strip().split(':')[1])
			self.filename = self.config.get(self.last_used_scan,'filename')
			self.timetrace = self.config.get(self.last_used_scan,'timetrace')
			self.save_figs = self.bool_(self.config.get(self.last_used_scan,'save_figs'))
			self.plot_X = self.config.get(self.last_used_scan,'plot_x')
		except configparser.NoOptionError as nov:
			QMessageBox.critical(self, 'Message',''.join(["Main FAULT while reading the config.ini file\n",str(nov)]))
			raise
		
		self.x_Tsub, self.y_Tsub = self.combined_Ts()
		self.x_Tsubfilm, self.y_Tsubfilm = self.combined_Tr()
		
		
	def bool_(self,txt):
		print('method bool_ runs...')
		
		if txt=="True":
			return True
		elif txt=="False":
			return False
		
		
	def combined_Tr(self):
		print('method combined_Tr runs...')
		
		if self.loadSubFilmFTIR_check and self.loadSubFilmOlis_check:
			x_all_ftir, y_all_ftir = self.get_ftir_data(self.loadSubFilmFTIR_str)
			x_all_olis, y_all_olis = self.get_olis_data(self.loadSubFilmOlis_str)
			
			indx=numpy.where(x_all_olis[0]>x_all_ftir)[0]
			
			x_all_ftir = x_all_ftir[indx]
			y_all_ftir = y_all_ftir[indx]
			
			return numpy.append(x_all_ftir, x_all_olis), numpy.append(y_all_ftir, y_all_olis)
		
		elif self.loadSubFilmFTIR_check:
			return self.get_ftir_data(self.loadSubFilmFTIR_str)
			
		elif self.loadSubFilmOlis_check:
			return self.get_olis_data(self.loadSubFilmOlis_str)
		
		else:
			return [], []
		
		
	def combined_Ts(self):
		print('method combined_Ts runs...')
		
		if self.loadSubOlis_check and self.loadSubFTIR_check:
			x_all_ftir, y_all_ftir = self.get_ftir_data(self.loadSubFTIR_str)
			x_all_olis, y_all_olis = self.get_olis_data(self.loadSubOlis_str)
			
			indx=numpy.where(x_all_olis[0]>x_all_ftir)[0]
			
			x_all_ftir = x_all_ftir[indx]
			y_all_ftir = y_all_ftir[indx]
			
			return numpy.append(x_all_ftir,x_all_olis), numpy.append(y_all_ftir,y_all_olis)
		
		elif self.loadSubFTIR_check:
			return self.get_ftir_data(self.loadSubFTIR_str)
			
		elif self.loadSubOlis_check:
			return self.get_olis_data(self.loadSubOlis_str)
		
		else:
			return [], []
		
		
	def get_olis_data(self,my_string):
		print('method get_olis_data runs...')
		# Open new datafile (.asc) form SOURCE 2 (OLIS)
		# Read and ignore header lines
		#header1 = f2.readline()
		data_eV=numpy.array([])
		data_tr=numpy.array([])
		
		# Read new datafile
		with open(''.join([self.cwd,os.sep,"data",os.sep,my_string]), 'r') as f2:
			for lines in f2:
				#line = line.strip()
				columns = lines.split()
				data_eV = numpy.append( data_eV, [1239.84187/float(columns[0])] ) # energy in eV
				data_tr = numpy.append( data_tr, [float(columns[1])] )
				
		idx=numpy.argsort(data_eV)
		data_eV=data_eV[idx]
		data_tr=data_tr[idx]
		
		if len(data_eV)==0 or len(data_tr)==0:
			raise Exception("No OLIS data found in the local method get_olis_data!")
		
		return data_eV, data_tr
	
	
	def get_ftir_data(self,my_string):
		print('method get_ftir_data runs...')
		# Open new datafile (.DPT) from SOURCE 1 (FTIR)
		# Raw FTIR data has complicated structure, severeal vales for a single wavelength
		# Read and ignore header lines
		#header1 = f1.readline()
		data_eV=numpy.array([])
		data_tr=numpy.array([])
		# Read new datafile
		with open(''.join([self.cwd,os.sep,"data",os.sep,my_string]),'r') as f1:
			for line in f1:
				#line = line.strip()
				columns = line.split()
				data_eV = numpy.append( data_eV, [1239.84187/(1000*float(columns[0]))] ) # energy in eV
				data_tr = numpy.append( data_tr, [float(columns[1])] )
				
		# Determine no. of repetitions for each sweeped wavelength (mostly 4 or 5 for FTIR)
		d3=numpy.array([len(list(group)) for key, group in groupby(data_eV)])

		avg=numpy.array([])
		shortlist_eV=numpy.array([])
		stdev_mag=numpy.array([]) 

		for tal in range(len(d3)):
			d4=numpy.sum(d3[0:tal])
			d5=numpy.sum(d3[0:tal+1])
			
			# Y axis enteries
			avg = numpy.append( avg, [numpy.sum(data_tr[d4:d5])/d3[tal]] )
			# X axis enteries
			shortlist_eV = numpy.append( shortlist_eV, [data_eV[d5-1]] ) # energy in eV
			# Python sample std dev calculated by the statistics module
			stdev_mag = numpy.append( stdev_mag, [numpy.sum(data_tr[d4:d5])/len(data_tr[d4:d5])] )
			
		idx=numpy.argsort(shortlist_eV)
		shortlist_eV=shortlist_eV[idx]
		avg=avg[idx]
		
		if len(shortlist_eV)==0 or len(avg)==0:
			raise Exception("No FTIR data found in the local method get_ftir_data!")
		
		return shortlist_eV, avg
		
		
	def make_plots(self):
		print('method make_plots in Get_raw runs...')
		pass_plots=[]
			
		fig, ax1 = plt.subplots(figsize=(15,10))
		ax2 = ax1.twinx()
		
		if self.plot_X=='eV':
			if len(self.x_Tsubfilm)>0:
				ax1.plot(self.x_Tsubfilm, self.y_Tsubfilm,'k-')
			if len(self.x_Tsub)>0:
				ax2.plot(self.x_Tsub, self.y_Tsub,'r-')
			ax1.set_xlabel("E, eV", fontsize=20)
			
		elif self.plot_X=='nm':
			if len(self.x_Tsubfilm)>0:
				ax1.plot(1239.84187/self.x_Tsubfilm, self.y_Tsubfilm,'k-')
			if len(self.x_Tsub)>0:
				ax2.plot(1239.84187/self.x_Tsub, self.y_Tsub,'r-')
			ax1.set_xlabel("Wavelength, nm", fontsize=20)
		
		if len(self.x_Tsubfilm)>0:
			ax1.set_ylabel("Tr_sub+film", fontsize=20, color='k')
			ax1.tick_params(axis="x", labelsize=20)
			ax1.tick_params(axis="y", labelsize=20, colors='k')
		
		if len(self.x_Tsub)>0:
			ax2.set_ylabel("Tr_sub", fontsize=20, color='r')			
			ax2.tick_params(axis="x", labelsize=20)
			ax2.tick_params(axis="y", labelsize=20, colors='r')
		
		#plt.xlim([0,4])
		#plt.ylim([0,1])
		plt.title("SUBSTRATE and FILM")
		#l=plt.legend(loc=1, fontsize=15)
		#l.draw_frame(False)

		string_1 = ''.join([self.filename,'_Tr_subfilmRAW_',self.timetrace,'.png'])
		if self.save_figs:
			plt.savefig(string_1)
			pass_plots.extend([string_1])
		
		########################################################################
		
		if len(self.x_Tsubfilm)>0:
			string_2 = ''.join([string_1[:-3],'txt'])
			with open(string_2, 'w') as thefile:
				thefile.write(''.join(['This data is constructed from the config file ', self.last_used_scan, '\n']))
				thefile.write('Column 1: wavelength in nm\n')
				thefile.write('Column 2: energy in eV\n')
				thefile.write('Column 3: Tr (filmRAW)\n')

				for tal0,tal1,tal2 in zip(1239.84187/self.x_Tsubfilm, self.x_Tsubfilm,self.y_Tsubfilm):
					thefile.write(''.join([str(tal0),'\t',str(tal1),'\t',str(tal2),'\n']))

			pass_plots.extend([string_2])
		
		if len(self.x_Tsub)>0:
			string_3 = ''.join([self.filename,'_Tr_subRAW_',self.timetrace,'.txt'])
			with open(string_3, 'w') as thefile:
				thefile.write(''.join(['This data is constructed from the config file ', self.last_used_scan, '\n']))
				thefile.write('Column 1: wavelength in nm\n')
				thefile.write('Column 2: energy in eV\n')
				thefile.write('Column 3: Tr (subRAW)\n')
				
				for tal0,tal1,tal2 in zip(1239.84187/self.x_Tsub,self.x_Tsub,self.y_Tsub):
					thefile.write(''.join([str(tal0),'\t',str(tal1),'\t',str(tal2),'\n']))

			pass_plots.extend([string_3])
		
		return pass_plots
	
	
	def show_plots(self):
		
		plt.show()
	
	def close_plots(self):
		
		plt.close()


if __name__ == "__main__":
	
	get_class=Get_raw()
	get_class.make_plots()
	get_class.show_plots()
	
	
	
