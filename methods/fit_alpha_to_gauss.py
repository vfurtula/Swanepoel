#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""


import math, numpy
import matplotlib.pyplot as plt
from numpy.polynomial import polynomial as P
import Get_TM_Tm as gtt
import get_m_d as gmd
import alpha as al



# Import ndfit
#import ndfit as ndf

class Gaussian_fit:
	
	def __init__(self,my_string,sep_low,sep_up):
		#my_string= 'spline'
		#separator=0.8 #in eV
		self.my_st=my_string
		self.my_se_low=sep_low
		self.my_se_up=sep_up
		ignored_points = gtt.ig_po()
		self.common_xaxis,self.alpha_wm = al.alpha_(ignored_points, my_string)
		
		self.x_rest=[]
		self.y_rest=[]
		self.x_gauss=[]
		self.y_gauss=[]
		self.rest_idx=[]
		self.gauss_idx=[]
		for i in range(len(self.common_xaxis)):
		  if self.common_xaxis[i]<sep_up and self.common_xaxis[i]>sep_low:
				self.gauss_idx.extend([ i ])
				self.x_gauss.extend([ self.common_xaxis[i] ])
				self.y_gauss.extend([ math.log(1e4*self.alpha_wm[i]) ])
		  else:
				self.rest_idx.extend([ i ])
				self.x_rest.extend([ self.common_xaxis[i] ])
				self.y_rest.extend([ math.log(1e4*self.alpha_wm[i]) ])
				
				
	def get_data(self):
		# order all the x and y values, NOT necessary but a good check
		# total_x=common_xaxis
		# total_y=alpha_wm
		total_x = [0] * len(self.common_xaxis)
		for i in range(len(self.gauss_idx)):
			total_x[self.gauss_idx[i]] = self.x_gauss[i]
		for i in range(len(self.rest_idx)):
			total_x[self.rest_idx[i]] = self.x_rest[i]
			
		total_y = [0] * len(self.common_xaxis)
		for i in range(len(self.gauss_idx)):
			total_y[self.gauss_idx[i]] = self.y_gauss[i]
		for i in range(len(self.rest_idx)):
			total_y[self.rest_idx[i]] = self.y_rest[i]
			
		return total_x, total_y
	
	
	def fit_data_to_poly(self,x,y,order):
		coefs = P.polyfit(x,y,order)
		#print "polyfit coef = ", coef    
		val = [numpy.poly1d(coefs[::-1])(i) for i in x]
		if order==2:
			print 'mean =', -coefs[1]/(2*coefs[2])
			print 'variance =', -1/(2*coefs[2])
		return val, coefs
	
	
	def fit_iterations(self):
		
		gf=Gaussian_fit(self.my_st,self.my_se_low,self.my_se_up)
		fitted_rest, coefs_rest = gf.fit_data_to_poly(self.x_rest,self.y_rest,4)
		basis_gauss = [numpy.poly1d(coefs_rest[::-1])(i) for i in self.x_gauss]
		
		new_vals_gauss=[self.y_gauss[i]-basis_gauss[i] for i in range(len(basis_gauss))]
		val_gauss, coefs_gauss = gf.fit_data_to_poly(self.x_gauss,new_vals_gauss,2)
		
		fitted_gauss = [val_gauss[i]+basis_gauss[i] for i in range(len(basis_gauss))]
		
		'''
		total_x = [0] * len(self.common_xaxis)
		for i in range(len(self.gauss_idx)):
			total_x[self.gauss_idx[i]] = self.x_gauss[i]
		for i in range(len(self.rest_idx)):
			total_x[self.rest_idx[i]] = self.x_rest[i]
			
		total_y = [0] * len(self.common_xaxis)
		for i in range(len(self.gauss_idx)):
			total_y[self.gauss_idx[i]] = fitted_gauss[i]
		for i in range(len(self.rest_idx)):
			total_y[self.rest_idx[i]] = fitted_rest[i]
			
		return total_x, total_y
		'''
		return self.x_gauss, fitted_gauss, self.x_rest, fitted_rest
        
if __name__ == "__main__":
  
	figures_folder, data_folder, raw_olis, raw_ftir, sub_olis, sub_ftir=gtt.folders_and_data()

	Ld=Gaussian_fit('spline',0.22,0.65) # <--------- EDIT VALUES IN THIS LINE
	total_x_real, total_y_real = Ld.get_data()  
	x_gauss, fitted_gauss, x_rest, fitted_rest = Ld.fit_iterations()

	plt.figure(1, figsize=(15,10)) 
	plt.plot(total_x_real,total_y_real,'ko-',label='Abs. alpha (spline)')
	plt.plot(x_gauss,fitted_gauss, 'ro-', label='Gaussian fit')  
	plt.plot(x_rest, fitted_rest, 'yo', label='4th order polyfit') 
	plt.xlabel("E, eV", fontsize=20)
	plt.ylabel("log_e(alpha), *10^3 cm^-1", fontsize=20)
	plt.tick_params(axis="both", labelsize=20)
	l=plt.legend(loc=4, fontsize=15)
	l.draw_frame(False)
	plt.show()

	total_y_real_exp=[math.exp(total_y_real[i]) for i in range(len(total_y_real))]
	fitted_gauss_exp=[math.exp(fitted_gauss[i]) for i in range(len(fitted_gauss))]
	fitted_rest_exp=[math.exp(fitted_rest[i]) for i in range(len(fitted_rest))]

	plt.figure(2, figsize=(15,10)) 
	plt.plot(total_x_real,total_y_real_exp,'ko-',label='Abs. alpha (spline)')
	plt.plot(x_gauss,fitted_gauss_exp, 'ro-', label='Gaussian fit')  
	plt.plot(x_rest, fitted_rest_exp, 'yo', label='4th order polyfit')  
	plt.xlabel("E, eV", fontsize=20)
	plt.ylabel("alpha, *10^3 cm^-1", fontsize=20)
	plt.tick_params(axis="both", labelsize=20)
	l=plt.legend(loc=4, fontsize=15)
	l.draw_frame(False)
	plt.show()
	'''
	mean = -rp[1]/(2*rp[0])
	var = -1/(2*rp[0])
	string_1 = ''.join(['Mean = ', str(math.ceil(mean*1e5)/1e5) ])
	string_2 = ''.join(['Variance = ', str(math.ceil(var*1e5)/1e5) ])
	plt.text(x[0], max(y), 'Fit function for alpha:', fontsize=20)	
	plt.text(x[0], max(y)-0.2, string_1, fontsize=20)
	plt.text(x[0], max(y)-0.4, string_2, fontsize=20)
	plt.xlabel("E, eV", fontsize=20)
	plt.ylabel("log_e(alpha), *10^3 cm^-1", fontsize=20)
	plt.tick_params(axis="both", labelsize=20)
	l=plt.legend(loc=1, fontsize=15)
	l.draw_frame(False)

	if not raw_olis:
		string_3 = ''.join([figures_folder, raw_ftir, '_alpha_fit.pdf'])
	else:
		string_3 = ''.join([figures_folder, raw_olis, '_alpha_fit.pdf'])
	plt.savefig(string_3)
	plt.show()

	########################################

	plt.figure(2, figsize=(15,10)) 
	plt.plot(x,[math.exp(tal) for tal in y],'ko-',label='Data (spline)')     # <--- plot the original data
	plt.plot(x,[math.exp(tal) for tal in curve], 'ro-', label='Gaussian fit (spline)')    # <--- plot the result of the fit
	plt.xlabel("E, eV", fontsize=20)
	plt.ylabel("alpha, *10^3 cm^-1", fontsize=20)
	plt.tick_params(axis="both", labelsize=20)
	l=plt.legend(loc=1, fontsize=15)
	l.draw_frame(False)

	if not raw_olis:
		string_4 = ''.join([figures_folder, raw_ftir, '_alpha_gaussFit(2).pdf'])
	else:
		string_4 = ''.join([figures_folder, raw_olis, '_alpha_gaussFit(2).pdf'])
	plt.savefig(string_4)

	plt.show()

	'''
