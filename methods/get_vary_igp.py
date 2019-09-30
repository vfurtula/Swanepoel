#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

from matplotlib import pyplot as plt

import time, numpy
from methods import get_m_d, get_raw



'''
## For Matplotlib fonts
from matplotlib import rc
## for LaTeX style use:
rc("text", usetex=True)
rc("font", family="serif")
'''
## Define absorption (alpha) functions  



class Vary_igp:
	
	def __init__(self, cwd):
		print('method __init__ in Vary_igp runs...')
		
		self.gw = get_raw.Get_raw(cwd)
		self.gmd = get_m_d.Gmd(cwd)
		
		self.ign_pts, self.m_start_min, self.d_dispersion_max, self.d_dispersion_min, self.d_mean, self.dispersion_rel = self.gmd.get_md_igpo()
		
		
	def make_plots(self):
		print('method make_plots in Vary_igp runs...')
		
		pass_plots=[]
		
		fig, ax1 = plt.subplots(figsize=(15,10))
		ax2 = ax1.twinx()
		
		ax1.plot(self.ign_pts,self.d_mean,'b-',label=''.join(['d_mean (', self.gw.fit_linear_spline, ')']))
		ax1.fill_between(self.ign_pts, self.d_dispersion_max, self.d_dispersion_min, facecolor='blue', alpha=0.3)
 
		ax1.set_xlabel("No. of ignored points", fontsize=20)
		ax1.set_ylabel("Film thickness d, nm", fontsize=20, color='b')
		ax1.set_title("Absolute dispersion in the film thickness and the optimized order number m_start")
		ax1.tick_params(axis="x", labelsize=20)
		ax1.tick_params(axis="y", labelsize=20, colors='b')
		#ax1.ylim([0,5])
		#ax1.yticks( numpy.linspace(2,3,11) )
		l=ax1.legend(loc=1, fontsize=15)
		l.draw_frame(False)
		
		ax2.plot(self.ign_pts,self.m_start_min,'r-')
		ax2.set_ylabel("Order index m_start", fontsize=20, color='r')
		ax2.tick_params(axis="x", labelsize=20)
		ax2.tick_params(axis="y", labelsize=20, colors='r')
		#ax2.ylim([0,5])
		#ax2.yticks( numpy.linspace(2,3,11) )
		#l=ax2.legend(loc=2, fontsize=15)
		#l.draw_frame(False)
		
		if self.gw.save_figs:
			string_1 = ''.join([self.gw.filename, '_d_and_m_asf_igp_', self.gw.fit_linear_spline,'_', self.gw.timetrace, '.png'])
			plt.savefig(string_1)
			pass_plots.extend([string_1])

		##############################################################
		
		fig, ax1 = plt.subplots(figsize=(15,10))
		ax2 = ax1.twinx()
		
		ax1.plot(self.ign_pts,self.dispersion_rel,'b-')
		ax1.set_xlabel("No. of ignored points", fontsize=20)
		ax1.set_ylabel("Stand.Dev.(d), nm", fontsize=20, color='b')
		ax1.set_title("Minimized standard deviation d and the optimized order number m_start")
		ax1.tick_params(axis="x", labelsize=20)
		ax1.tick_params(axis="y", labelsize=20, colors='b')
		#ax1.ylim([0,5])
		#ax1.yticks( numpy.linspace(2,3,11) )
		#l=ax1.legend(loc=1, fontsize=15)
		#l.draw_frame(False)
		
		ax2.plot(self.ign_pts,self.m_start_min,'r-')
		ax2.set_ylabel("Order index m_start", fontsize=20, color='r')
		ax2.tick_params(axis="x", labelsize=20)
		ax2.tick_params(axis="y", labelsize=20, colors='r')
		#ax2.ylim([0,5])
		#ax2.yticks( numpy.linspace(2,3,11) )
		#l=ax2.legend(loc=2, fontsize=15)
		#l.draw_frame(False)
		
		if self.gw.save_figs:
			string_2 = ''.join([self.gw.filename, '_RelDisp_and_m_asf_igp_', self.gw.fit_linear_spline,'_', self.gw.timetrace, '.png'])
			plt.savefig(string_2)
			pass_plots.extend([string_2])
			
		##############################################################
		
		# save all data as a txt file
		string_3 = ''.join([self.gw.filename, '_RelDisp_m_d_asf_igp_', self.gw.fit_linear_spline,'_', self.gw.timetrace, '.txt'])
		with open(string_3, 'w') as thefile: 
			thefile.write(''.join(['This data is constructed from the config file ', self.gw.last_used_scan, '\n']))
			thefile.write(''.join(['Interpolation method for Tmin and Tmax points is ', self.gw.fit_linear_spline, '\n']))
			thefile.write('Column 1: Number of ignored points\n')
			thefile.write('Column 2: Order index m_start\n')
			thefile.write('Column 3: Max film thickness in nm\n')
			thefile.write('Column 4: Min film thickness in nm\n')
			thefile.write('Column 5: Mean film thickness in nm\n')
			thefile.write('Column 6: Optimized relative dispersion nm/point\n')

			for tal0,tal1,tal2,tal3,tal4,tal5 in zip(self.ign_pts,self.m_start_min,self.d_dispersion_max,self.d_dispersion_min,self.d_mean,self.dispersion_rel):
				thefile.write(''.join([str(tal0),'\t',str(tal1),'\t',str(tal2),'\t',str(tal3),'\t',str(tal4),'\t',str(tal5),'\n']))
		
		pass_plots.extend([string_3])
		
		return pass_plots
	
	
	def show_plots(self):
		
		plt.show()
		
		
	def close_plots(self):
		
		plt.close()
		
		
		
		
if __name__ == "__main__":
	
	get_class=Vary_igp()
	get_class.make_plots()
	get_class.show_plots()







