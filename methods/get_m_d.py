#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

from matplotlib import pyplot as plt

import time, math, os, sys, numpy
from numpy.polynomial import polynomial as P
import scipy.optimize as scop
from methods import get_Tmax_Tmin, get_raw
#from numpy import linalg as lng


'''
## For Matplotlib fonts
from matplotlib import rc
## for LaTeX style use:
rc("text", usetex=True)
rc("font", family="serif")
''' 

class Gmd:
	
	def __init__(self,cwd):
		print('method __init__ in Gmd runs...')
		
		self.gtt = get_Tmax_Tmin.Get_Tmax_Tmin(cwd)
		self.gw = get_raw.Get_raw(cwd)
		
		_, _, com_axisTminTmax_final, _ = self.gtt.get_T_alpha()
		self.common_xaxis_eV, self.Tmin, self.Tmax = com_axisTminTmax_final
		_, self.Ts = self.gtt.fit_Ts_to_data(self.common_xaxis_eV)
		
		# convert to wavelength in nm
		self.common_xaxis_nm = 1239.84187/self.common_xaxis_eV
		
		_, self.nn1 = self.n1()
		
		if self.gw.ignore_data_pts==0:
			_, self.m_start_min, self.nn2, self.d2 = self.n2(self.common_xaxis_nm,self.nn1)
		else:
			_, self.m_start_min, self.nn2, self.d2 = self.n2(self.common_xaxis_nm[:-self.gw.ignore_data_pts],self.nn1[:-self.gw.ignore_data_pts])
			
		_, self.n_trans = self.n_trans()
		
		
	def n_trans(self):
		print('method n_trans runs...')

		s = (1.0/self.Ts)+(1.0/self.Ts**2-1)**0.5
		M = 2.0*s/self.Tmin-(s**2+1.0)/2 
		n_trans = (M+(M**2-s**2)**0.5)**0.5

		return self.common_xaxis_eV, n_trans
	

	def n1(self):
		print('method n1 runs...')

		s = (1.0/self.Ts)+(1/self.Ts**2-1)**0.5
		N = 2.0*s*(self.Tmax-self.Tmin)/(self.Tmax*self.Tmin)+(s**2+1)/2.0 
		n_min_max = (N+(N**2-s**2)**0.5)**0.5

		return self.common_xaxis_eV, n_min_max


	def minimize_d_dispersion(self,m_start,common_xaxis,n):
		print('method minimize_d_dispersion runs...')
		
		m_start=round(m_start[0]*2.0)/2.0
		m=numpy.arange(int(10*m_start),int(10*m_start)+len(common_xaxis)*5,5)/10.0 
		
		d=m*common_xaxis/(2.0*n)
		
		return numpy.std(d)
		

	def n2(self,common_xaxis,n):
		print('method n2 runs...')
		
		y0 = 5
		m_start = scop.fmin_powell(self.minimize_d_dispersion,y0,args=(common_xaxis,n),xtol=0.1)
		
		m_start_min=round(m_start*2.0)/2.0
		
		m_=numpy.arange(int(10*m_start_min),int(10*m_start_min)+len(common_xaxis)*5,5)/10.0
		d2_ = m_*common_xaxis/(2.0*n)
		
		m_=numpy.arange(int(10*m_start_min),int(10*m_start_min)+len(self.common_xaxis_nm)*5,5)/10.0
		n2 = m_*self.common_xaxis_nm/(2*numpy.mean(d2_))

		return self.common_xaxis_eV, m_start_min, n2, numpy.mean(d2_)
	

	def get_md_igpo(self):
		print('method get_md_igpo runs...')

		dispersion_std = []
		d_dispersion_max = []
		d_dispersion_min = []
		d_mean = []
		m_start_min = []
		ign_pts = []
		
		for tal in range(len(self.common_xaxis_nm)-1):
			
			y0 = 5
			if tal>0:
				my_len=len(self.common_xaxis_nm[:-tal])
				m_start = scop.fmin_powell(self.minimize_d_dispersion,y0,args=(self.common_xaxis_nm[:-tal],self.nn1[:-tal]),xtol=0.1)
				
				m_start_min_=round(m_start*2.0)/2.0
				m=numpy.arange(int(10*m_start_min_),int(10*m_start_min_)+my_len*5,5)/10.0

				d2_ = m*self.common_xaxis_nm[:-tal]/(2.0*self.nn1[:-tal])
				dispersion = numpy.std(d2_)
				
			else:
				my_len=len(self.common_xaxis_nm)
				m_start = scop.fmin_powell(self.minimize_d_dispersion,y0,args=(self.common_xaxis_nm,self.nn1),xtol=0.1)
				
				m_start_min_=round(m_start*2.0)/2.0
				m=numpy.arange(int(10*m_start_min_),int(10*m_start_min_)+my_len*5,5)/10.0

				d2_ = m*self.common_xaxis_nm/(2.0*self.nn1)
				dispersion = numpy.std(d2_)
			
			dispersion_std.extend([dispersion])
			d_dispersion_max.extend([numpy.max(d2_)])
			d_dispersion_min.extend([numpy.min(d2_)])
			d_mean.extend([numpy.mean(d2_)])
			
			m_start_min.extend([m_start_min_])
			ign_pts.extend([tal])
			
		return ign_pts, m_start_min, d_dispersion_max, d_dispersion_min, d_mean, dispersion_std
	

	def make_plots(self):
		print('method make_plots in Gmd runs...')
		
		pass_plots=[]
	
		plt.figure(figsize=(15,10))
		
		if self.gw.plot_X=='eV':
			plt.plot(self.common_xaxis_eV, self.nn2, 'ro-', label=''.join(['n2 (', self.gw.fit_linear_spline,')']))
			plt.plot(self.common_xaxis_eV, self.nn1, 'k-', label=''.join(['n1 (', self.gw.fit_linear_spline,')']))
			plt.plot(self.common_xaxis_eV, self.n_trans, 'mo-', label=''.join(['n_trans (', self.gw.fit_linear_spline,')']))
			
			plt.xlabel("E, eV", fontsize=20)
			
		elif self.gw.plot_X=='nm':
			plt.plot(self.common_xaxis_nm, self.nn2, 'ro-', label=''.join(['n2 (', self.gw.fit_linear_spline,')']))
			plt.plot(self.common_xaxis_nm, self.nn1, 'k-', label=''.join(['n1 (', self.gw.fit_linear_spline,')']))
			plt.plot(self.common_xaxis_nm, self.n_trans, 'mo-', label=''.join(['n_trans (', self.gw.fit_linear_spline,')']))
			plt.xlabel("Wavelength, nm", fontsize=20)
		
		plt.ylabel("n", fontsize=20)
		plt.title(''.join(["Refractive index n, Order no. m_start=",str(self.m_start_min),", d_mean=",str(round(self.d2))," nm"]))
		plt.tick_params(axis="both", labelsize=20)
		#plt.ylim([0,5])
		#plt.yticks( numpy.linspace(2,3,11) )
		l=plt.legend(loc=1, fontsize=15)
		l.draw_frame(False)

		if self.gw.save_figs:
			string_3 = ''.join([self.gw.filename, '_n1_n2_', self.gw.fit_linear_spline,'_', self.gw.timetrace, '.png'])
			plt.savefig(string_3)
			pass_plots.extend([string_3])

		##########################################################
		
		# save datas as a txt file  
		string_4 = ''.join([self.gw.filename, '_n_', self.gw.fit_linear_spline,'_', self.gw.timetrace, '.txt'])
		with open(string_4, 'w') as thefile:
			thefile.write(''.join(['This data is constructed from the config file ', self.gw.last_used_scan, '\n']))
			thefile.write(''.join(['Interpolation method for Tmin and Tmax points is ', self.gw.fit_linear_spline, '\n']))
			thefile.write('Column 1: energy in eV\n')
			thefile.write('Column 2: wavelength in nm\n')
			thefile.write('Column 3: ref index n2\n')
		    
			for tal0,tal1,tal2 in zip(self.common_xaxis_eV,self.common_xaxis_nm,self.nn2):
				thefile.write(''.join([str(tal0),'\t',str(tal1),'\t',str(tal2),'\n',]))
		
		pass_plots.extend([string_4])
	
		return pass_plots


	def show_plots(self):
		
		plt.show()
		
		
	def close_plots(self):
		
		plt.close()
		
		
		
		
if __name__ == "__main__":
	
	get_class=Gmd()
	get_class.make_plots()
	get_class.show_plots()
