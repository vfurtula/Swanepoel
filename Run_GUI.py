#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

from matplotlib import pyplot as plt
'''
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
'''

import os, sys, time, numpy, yagmail, configparser, pathlib, getpass, traceback

from PyQt5.QtCore import QObject, QThreadPool, QTimer, QRunnable, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QDialog, QWidget, QMainWindow, QCheckBox, QLCDNumber, QMessageBox, QGridLayout,
														 QInputDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout,
														 QHBoxLayout, QApplication, QMenuBar, QPushButton, QFileDialog)

from help_dialogs import Indicator_invs_dialog, Indicator_dialog
import asyncio

import Email_settings_dialog, Send_email_dialog, Load_config_dialog





class WorkerSignals(QObject):
	# Create signals to be used
	lcd = pyqtSignal(object)
	pass_plots = pyqtSignal(object)
	
	error = pyqtSignal(object)
	finished = pyqtSignal()
	warning = pyqtSignal(object)
	critical = pyqtSignal(object)
	
	
	
	
	
class Send_Email_Worker(QRunnable):
	"""
	Worker thread
	:param args: Arguments to make available to the run code
	:param kwargs: Keywords arguments to make available to the run code
	"""
	def __init__(self,*argv):
		super(Send_Email_Worker, self).__init__()
		
		# constants	
		self.subject = argv[0].subject
		self.contents = argv[0].contents
		self.emailset_str = argv[0].settings
		self.emailrec_str = argv[0].receivers
		
		self.signals = WorkerSignals()
		
		
	@pyqtSlot()
	def run(self):
		asyncio.set_event_loop(asyncio.new_event_loop())
		try:
			yag = yagmail.SMTP(self.emailset_str[0], getpass.getpass( prompt=''.join(["Password for ",self.emailset_str[0],"@gmail.com:"]) )) # yag = yagmail.SMTP(self.emailset_str[0])
			yag.send(self.emailrec_str, subject=self.subject, contents=self.contents)
			self.signals.warning.emit(''.join(["E-mail is sent to ", ' and '.join([i for i in self.emailrec_str]) ," including ",str(len(self.contents[1:]))," attachment(s)!"]))
		except Exception as e:
			self.signals.critical.emit(''.join(["Could not send e-mail from the gmail account ",self.emailset_str[0],"! Try following steps:\n1. Check your internet connection. \n2. Check the account username and password.\n3. Make sure that the account accepts less secure apps.\n4. Make sure that keyring.get_password(\"system\", \"username\") works in your operating system.\n\n",str(e)]))
			
		self.signals.finished.emit()
	
	
	
	
	
	
class Worker(QRunnable):
	'''
	Worker thread
	:param args: Arguments to make available to the run code
	:param kwargs: Keywords arguments to make available to the run code
	'''
	def __init__(self, *argv):
		super(Worker, self).__init__()
		
		self.sender = argv[0]
		self.cwd = argv[1]
		
		self.signals = WorkerSignals()
		
		
	def abort(self):
		self.abort_flag=True
		
		
	@pyqtSlot()
	def run(self):
		try:
			if self.sender=='Raw data':
				from methods import get_raw
				my_arg = get_raw.Get_raw(self.cwd)
				
			elif self.sender=='Tmin and Tmax':
				from methods import get_Tmax_Tmin
				my_arg = get_Tmax_Tmin.Get_Tmax_Tmin(self.cwd)
				
			elif self.sender=='Std.Dev. in d':
				from methods import get_vary_igp
				my_arg = get_vary_igp.Vary_igp(self.cwd)
				
			elif self.sender=='Index n':
				from methods import get_m_d
				my_arg = get_m_d.Gmd(self.cwd)
				
			elif self.sender=='Absorption alpha':
				from methods import alpha
				my_arg = alpha.Alpha(self.cwd)
				
			elif self.sender=='Wavenumber k':
				from methods import k
				my_arg = k.K_class(self.cwd)
				
			self.signals.pass_plots.emit([my_arg, self.sender])
			
		except Exception as inst:
			self.signals.critical.emit( ''.join(["Critical message returned from the local method ",self.sender,":\n\n",str(inst)]) )
			
			
		self.signals.finished.emit()
		
		
		
		
		
		
		
class Run_gui(QMainWindow):
	
	def __init__(self):
		super().__init__()
		
		self.cwd = os.getcwd()
		self.load_()
		
		# Enable antialiasing for prettier plots		
		self.initUI()
		
		
	def initUI(self):
		
		################### MENU BARS START ##################
		MyBar = QMenuBar(self)

		fileMenu = MyBar.addMenu("File")

		self.fileSave = fileMenu.addAction("Save thinfilm config")        
		self.fileSave.triggered.connect(self.save_) 
		self.fileSave.setShortcut('Ctrl+S')
		
		self.fileLoadAs = fileMenu.addAction("Load config section")        
		self.fileLoadAs.triggered.connect(self.load_config_dialog)

		fileClose = fileMenu.addAction("Close")        
		fileClose.triggered.connect(self.close) # triggers closeEvent()
		fileClose.setShortcut('Ctrl+X')

		self.loadMenu = MyBar.addMenu("Load data")
		loadSubOlis = self.loadMenu.addAction("OLIS sub")
		loadSubFilmOlis = self.loadMenu.addAction("OLIS sub + thin film")
		loadSubFTIR = self.loadMenu.addAction("FTIR sub")
		loadSubFilmFTIR = self.loadMenu.addAction("FTIR sub + thin film")

		loadSubOlis.triggered.connect(self.loadSubOlisDialog)
		loadSubFilmOlis.triggered.connect(self.loadSubFilmOlisDialog)
		loadSubFTIR.triggered.connect(self.loadSubFTIRDialog)
		loadSubFilmFTIR.triggered.connect(self.loadSubFilmFTIRDialog)
		
		self.emailMenu = MyBar.addMenu("E-mail")
		self.emailSettings = self.emailMenu.addAction("E-mail settings")
		self.emailSettings.triggered.connect(self.email_set_dialog)
		self.emailData = self.emailMenu.addAction("E-mail data")
		self.emailData.triggered.connect(self.email_data_dialog)

		helpMenu = MyBar.addMenu("Help")
		helpParam = helpMenu.addAction("Instructions")
		helpParam.triggered.connect(self.helpParamDialog)
		contact = helpMenu.addAction("Contact")
		contact.triggered.connect(self.contactDialog)

		################### MENU BARS END ##################

		# status info which button has been pressed
		Start_lbl = QLabel("PLOTS and analysis steps", self)
		Start_lbl.setStyleSheet("color: blue")

		self.Step0_Button = QPushButton("Raw data",self)
		self.Step0_Button.setToolTip("STEP 0. Plot raw data for OLIS and FTIR")
		self.button_style(self.Step0_Button,'black')

		self.Step1_Button = QPushButton("Tmin and Tmax",self)
		self.Step1_Button.setToolTip("STEP 1. Find all the minima and maxima positions using Gaussian filter")
		self.button_style(self.Step1_Button,'black')

		self.Step2_Button = QPushButton("Std.Dev. in d",self)
		self.Step2_Button.setToolTip("STEP 2. Minimize standard deviation in the film thickness d")
		self.button_style(self.Step2_Button,'black')

		self.Step3_Button = QPushButton("Index n",self)
		self.Step3_Button.setToolTip("STEP 3. Plot refractive indicies n1 and n2")
		self.button_style(self.Step3_Button,'black')

		self.Step4_Button = QPushButton("Absorption alpha",self)
		self.Step4_Button.setToolTip("STEP 4. Plot abosorption alpha based on n2")
		self.button_style(self.Step4_Button,'black')

		self.Step5_Button = QPushButton("Wavenumber k",self)
		self.Step5_Button.setToolTip("STEP 5. Plot wavenumber k based on n2")
		self.button_style(self.Step5_Button,'black')

		####################################################

		# status info which button has been pressed
		self.NewFiles = QLabel('No files created yet!', self)
		self.NewFiles.setStyleSheet("color: blue")
		
		newfont = QFont("Times", 10, QFont.Normal) 
		self.NewFiles.setFont(newfont)
		
		'''
		self.NewFiles = numpy.zeros(5,dtype=object)
		for i in range(4):
			self.NewFiles[i] = QLabel(''.join([str(i+1),': ']), self)
			self.NewFiles[i].setStyleSheet("color: magenta")
		'''
			
		####################################################
		loads_lbl = QLabel("RAW data files", self)
		loads_lbl.setStyleSheet("color: blue")

		configFile_lbl = QLabel("Current thinfilm", self)
		self.config_file_lbl = QLabel("", self)
		self.config_file_lbl.setStyleSheet("color: green")

		loadSubOlis_lbl = QLabel("OLIS sub", self)
		self.loadSubOlisFile_lbl = QLabel("", self)
		self.loadSubOlisFile_lbl.setStyleSheet("color: magenta")
			
		loadSubFilmOlis_lbl = QLabel("OLIS sub + thin film", self)
		self.loadSubFilmOlisFile_lbl = QLabel("", self)
		self.loadSubFilmOlisFile_lbl.setStyleSheet("color: magenta")

		loadSubFTIR_lbl = QLabel("FTIR sub", self)
		self.loadSubFTIRFile_lbl = QLabel("", self)
		self.loadSubFTIRFile_lbl.setStyleSheet("color: magenta")

		loadSubFilmFTIR_lbl = QLabel("FTIR sub + thin film", self)
		self.loadSubFilmFTIRFile_lbl = QLabel("", self)
		self.loadSubFilmFTIRFile_lbl.setStyleSheet("color: magenta")

		self.cb_sub_olis = QCheckBox('',self)
		self.cb_sub_olis.toggle()
		self.cb_subfilm_olis = QCheckBox('',self)
		self.cb_subfilm_olis.toggle()
		self.cb_sub_ftir = QCheckBox('',self)
		self.cb_sub_ftir.toggle()
		self.cb_subfilm_ftir = QCheckBox('',self)
		self.cb_subfilm_ftir.toggle()

		plot_X_lbl = QLabel("Plot X axis in", self)
		self.combo2 = QComboBox(self)
		self.mylist2=["eV","nm"]
		self.combo2.addItems(self.mylist2)
		self.combo2.setFixedWidth(70)

		####################################################

		lbl1 = QLabel("GAUSSIAN filter settings", self)
		lbl1.setStyleSheet("color: blue")

		interpol_lbl = QLabel("Interpolation method", self)
		self.combo4 = QComboBox(self)
		self.mylist4=["spline","linear"]
		self.combo4.setToolTip("Interpolation method for local minima Tmin and local maxima Tmax can only be linear or spline.")
		self.combo4.addItems(self.mylist4)
		self.combo4.setFixedWidth(70)

		factors_lbl = QLabel("Gaussian factors", self)
		self.factorsEdit = QLineEdit("",self)
		self.factorsEdit.setToolTip("HIGH gaussian factor = broadband noise filtering.\nLOW gaussian factor = narrowband noise filtering.\nHigh gauissian factors (>2) will result in relatively large deviation from the raw data.\nGauissian factors of zero or near zero (<0.5) will closely follow trend of the raw data.")
		self.factorsEdit.setFixedWidth(200)

		borders_lbl = QLabel("Gaussian borders [eV]", self)
		self.bordersEdit = QLineEdit("",self)
		self.bordersEdit.setToolTip("Gaussian borders should be typed in ascending order and the number of\nborders is always one more compared with the number of Gaussian factors.")
		self.bordersEdit.setFixedWidth(200)

		##############################################

		lbl2 = QLabel("ABSORPTION alpha and n1 and n2", self)
		lbl2.setStyleSheet("color: blue")	

		poly_lbl = QLabel("Polyfit order", self)
		self.combo1 = QComboBox(self)
		self.mylist1=["1","2","3","4","5"]
		self.combo1.addItems(self.mylist1)
		self.combo1.setFixedWidth(70)

		polybord_lbl = QLabel("Polyfit range(s) [eV]", self)
		self.poly_bordersEdit = QLineEdit("", self)
		self.poly_bordersEdit.setFixedWidth(140)

		self.cb_polybord = QCheckBox('',self)
		self.cb_polybord.toggle()

		ignore_data_lbl = QLabel("No. of ignored points", self)
		self.ignore_data_ptsEdit = QLineEdit("",self)
		self.ignore_data_ptsEdit.setFixedWidth(140)
		
		corr_slit_lbl = QLabel("Correction slit width [nm]", self)
		self.corr_slitEdit = QLineEdit("",self)
		self.corr_slitEdit.setToolTip("Finite spectrometer bandwidth (slit width) in the transmission spectrum.")
		self.corr_slitEdit.setFixedWidth(140)
		
		##############################################
		
		lbl4 = QLabel("STORAGE location (folder/file)", self)
		lbl4.setStyleSheet("color: blue")
		self.filenameEdit = QLineEdit("",self)
		#self.filenameEdit.setFixedWidth(180)
		
		self.cb_save_figs = QCheckBox('Save figs',self)
		self.cb_save_figs.toggle()
		
		##############################################
		
		self.lcd = QLCDNumber(self)
		self.lcd.setStyleSheet("color: red")
		self.lcd.setFixedHeight(60)
		self.lcd.setSegmentStyle(QLCDNumber.Flat)
		self.lcd.setToolTip("Timetrace for saving files")
		self.lcd.setNumDigits(11)
		
		##############################################
		
		self.initUI_()
		
		##############################################
		
		# Add all widgets		
		g1_0 = QGridLayout()
		g1_0.addWidget(MyBar,0,0)
		g1_1 = QGridLayout()
		g1_1.addWidget(loads_lbl,0,0)
		g1_1.addWidget(configFile_lbl,1,0)
		g1_1.addWidget(self.config_file_lbl,1,1)
		g1_1.addWidget(loadSubOlis_lbl,2,0)
		g1_1.addWidget(self.loadSubOlisFile_lbl,2,1)
		g1_1.addWidget(self.cb_sub_olis,2,2)
		g1_1.addWidget(loadSubFilmOlis_lbl,3,0)
		g1_1.addWidget(self.loadSubFilmOlisFile_lbl,3,1)
		g1_1.addWidget(self.cb_subfilm_olis,3,2)
		g1_1.addWidget(loadSubFTIR_lbl,4,0)
		g1_1.addWidget(self.loadSubFTIRFile_lbl,4,1)
		g1_1.addWidget(self.cb_sub_ftir,4,2)
		g1_1.addWidget(loadSubFilmFTIR_lbl,5,0)
		g1_1.addWidget(self.loadSubFilmFTIRFile_lbl,5,1)
		g1_1.addWidget(self.cb_subfilm_ftir,5,2)
		g1_1.addWidget(plot_X_lbl,6,0)
		g1_1.addWidget(self.combo2,6,1)

		g1_2 = QGridLayout()
		g1_2.addWidget(lbl1,0,0)
		g1_3 = QGridLayout()
		g1_3.addWidget(interpol_lbl,0,0)
		g1_3.addWidget(self.combo4,0,1)
		g1_3.addWidget(factors_lbl,1,0)
		g1_3.addWidget(self.factorsEdit,1,1)
		g1_3.addWidget(borders_lbl,2,0)
		g1_3.addWidget(self.bordersEdit,2,1)

		g1_4 = QGridLayout()
		g1_4.addWidget(lbl2,0,0)
		g1_5 = QGridLayout()
		g1_5.addWidget(poly_lbl,0,0)
		g1_5.addWidget(self.combo1,0,1)
		g1_5.addWidget(polybord_lbl,1,0)
		g1_5.addWidget(self.poly_bordersEdit,1,1)
		g1_5.addWidget(self.cb_polybord,1,2)
		g1_5.addWidget(ignore_data_lbl,2,0)
		g1_5.addWidget(self.ignore_data_ptsEdit,2,1)
		g1_5.addWidget(corr_slit_lbl,3,0)
		g1_5.addWidget(self.corr_slitEdit,3,1)

		g4_0 = QGridLayout()
		g4_0.addWidget(lbl4,0,0)
		g4_0.addWidget(self.cb_save_figs,0,1)
		g4_1 = QGridLayout()
		g4_1.addWidget(self.filenameEdit,0,0)

		v1 = QVBoxLayout()
		v1.addLayout(g1_0)
		v1.addLayout(g1_1)
		v1.addLayout(g1_2)
		v1.addLayout(g1_3)
		v1.addLayout(g1_4)
		v1.addLayout(g1_5)
		v1.addLayout(g4_0)
		v1.addLayout(g4_1)

		###################################################

		g1_6 = QGridLayout()
		g1_6.addWidget(Start_lbl,0,0)
		g1_7 = QGridLayout()
		g1_7.addWidget(self.Step0_Button,0,0)
		g1_7.addWidget(self.Step1_Button,1,0)
		g1_7.addWidget(self.Step2_Button,2,0)
		g1_7.addWidget(self.Step3_Button,3,0)
		g1_7.addWidget(self.Step4_Button,4,0)
		g1_7.addWidget(self.Step5_Button,5,0)

		g1_8 = QGridLayout()
		g1_8.addWidget(self.NewFiles,0,0)
		g1_8.addWidget(self.lcd,1,0)


		v0 = QVBoxLayout()
		v0.addLayout(g1_6)
		v0.addLayout(g1_7)
		v0.addLayout(g1_8)

		# SET ALL VERTICAL COLUMNS TOGETHER
		hbox = QHBoxLayout()
		hbox.addLayout(v1)
		hbox.addLayout(v0)

		###############################################################################

		# reacts to choises picked in the menu
		self.combo1.activated[str].connect(self.onActivated1)
		self.combo2.activated[str].connect(self.onActivated2)
		self.combo4.activated[str].connect(self.onActivated4)

		# reacts to choises picked in the menu
		self.Step0_Button.clicked.connect(self.set_run)
		self.Step1_Button.clicked.connect(self.set_run)
		self.Step2_Button.clicked.connect(self.set_run)
		self.Step3_Button.clicked.connect(self.set_run)
		self.Step4_Button.clicked.connect(self.set_run)
		self.Step5_Button.clicked.connect(self.set_run)

		# reacts to choises picked in the checkbox
		self.cb_sub_olis.stateChanged.connect(self.sub_olis_check)
		self.cb_subfilm_olis.stateChanged.connect(self.subfilm_olis_check)
		self.cb_sub_ftir.stateChanged.connect(self.sub_ftir_check)
		self.cb_subfilm_ftir.stateChanged.connect(self.subfilm_ftir_check)
		self.cb_save_figs.stateChanged.connect(self.save_figs_check)
		self.cb_polybord.stateChanged.connect(self.polybord_check)
		
		self.threadpool = QThreadPool()
		print("Multithreading in TEST_gui_v1 with maximum %d threads" % self.threadpool.maxThreadCount())
		self.isRunning = False
		
		self.move(0,0)
		#self.setGeometry(50, 50, 800, 500)
		hbox.setSizeConstraint(hbox.SetFixedSize)
		self.setWindowTitle("Swanepoel method for thin film analysis")
		
		w = QWidget()
		w.setLayout(hbox)
		self.setCentralWidget(w)
		self.show()
		
		
	def bool_(self,txt):
		
		if txt=="True":
			return True
		elif txt=="False":
			return False
		
		
	def initUI_(self):
		
		self.config_file_lbl.setText(self.last_used_scan)
		
		self.loadSubOlisFile_lbl.setText(self.loadSubOlis_str)
		
		self.loadSubFilmOlisFile_lbl.setText(self.loadSubFilmOlis_str)
		
		self.loadSubFTIRFile_lbl.setText(self.loadSubFTIR_str)
		
		self.loadSubFilmFTIRFile_lbl.setText(self.loadSubFilmFTIR_str)
		
		##############################################
		
		self.sub_olis_check(self.loadSubOlis_check)
		self.cb_sub_olis.setChecked(self.loadSubOlis_check)
		
		self.subfilm_olis_check(self.loadSubFilmOlis_check)
		self.cb_subfilm_olis.setChecked(self.loadSubFilmOlis_check)
		
		self.sub_ftir_check(self.loadSubFTIR_check)
		self.cb_sub_ftir.setChecked(self.loadSubFTIR_check)
		
		self.subfilm_ftir_check(self.loadSubFilmFTIR_check)
		self.cb_subfilm_ftir.setChecked(self.loadSubFilmFTIR_check)
		
		self.save_figs_check(self.save_figs)
		self.cb_save_figs.setChecked(self.save_figs)
		self.filenameEdit.setText(self.filename_str)
		
		##############################################
		
		if len(self.fit_poly_ranges)==0:
			self.fit_poly_ranges_check=False
			self.polybord_check(self.fit_poly_ranges_check)
			self.cb_polybord.setChecked(self.fit_poly_ranges_check)
		else:
			self.polybord_check(self.fit_poly_ranges_check)
			self.cb_polybord.setChecked(self.fit_poly_ranges_check)
		
		##############################################
		
		self.factorsEdit.setText(self.gaussian_factors)
		self.bordersEdit.setText(self.gaussian_borders)
		
		##############################################
		
		self.combo1.setCurrentIndex(self.mylist1.index(self.fit_poly_order))
		self.combo2.setCurrentIndex(self.mylist2.index(self.plot_X))
		self.combo4.setCurrentIndex(self.mylist4.index(self.fit_linear_spline))
		
		##############################################
		
		self.poly_bordersEdit.setText(self.fit_poly_ranges)
		self.ignore_data_ptsEdit.setText(self.ignore_data_pts)
		self.corr_slitEdit.setText(self.corr_slit)
		
		##############################################
		
		self.NewFiles.setToolTip(''.join(["Display newly created and saved files in ",os.sep,self.filename_str,os.sep]))
		self.lcd.display(self.timetrace)
		
		
	def button_style(self,button,color):
		
		button.setStyleSheet(''.join(['QPushButton {background-color: lightblue; font-size: 18pt; color: ',color,'}']))
		button.setFixedWidth(260)
		button.setFixedHeight(65)
		
		
	def loadSubOlisDialog(self):
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"Open files",''.join(['data',os.sep]), "All Files (*);;Dat Files (*.dat);;Text Files (*.txt)", options=options)
		for afile in files:
			head, tail = os.path.split(str(afile))
			self.loadSubOlis_str = tail
			self.loadSubOlisFile_lbl.setText(tail)
			self.cb_sub_olis.setEnabled(True)
			
			self.loadSubOlis_check = True
			self.cb_sub_olis(self.loadSubOlis_check)
			
			
	def loadSubFilmOlisDialog(self):
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"Open files",''.join(['data',os.sep]), "All Files (*);;Dat Files (*.dat);;Text Files (*.txt)", options=options)
		for afile in files:
			head, tail = os.path.split(str(afile))
			self.loadSubFilmOlis_str = tail
			self.loadSubFilmOlisFile_lbl.setText(tail)
			self.cb_subfilm_olis.setEnabled(True)
			
			self.loadSubFilmOlis_check = True
			self.cb_subfilm_olis(self.loadSubFilmOlis_check)
			
			
	def loadSubFTIRDialog(self):
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"Open files",''.join(['data',os.sep]), "All Files (*);;Dat Files (*.dat);;Text Files (*.txt)", options=options)
		for afile in files:
			head, tail = os.path.split(str(afile))
			self.loadSubFTIR_str = tail
			self.loadSubFTIRFile_lbl.setText(tail)
			self.cb_sub_ftir.setEnabled(True)
			
			self.loadSubFTIR_check = True
			self.cb_sub_ftir(self.loadSubFTIR_check)
			
			
	def loadSubFilmFTIRDialog(self):
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		files, _ = QFileDialog.getOpenFileNames(self,"Open files",''.join(['data',os.sep]), "All Files (*);;Dat Files (*.dat);;Text Files (*.txt)", options=options)
		for afile in files:
			head, tail = os.path.split(str(afile))
			self.loadSubFilmFTIR_str = tail
			self.loadSubFilmFTIRFile_lbl.setText(tail)
			self.cb_subfilm_ftir.setEnabled(True)
			
			self.loadSubFilmFTIR_check = True
			self.cb_subfilm_ftir.setChecked(self.loadSubFilmFTIR_check)
			
			
	def load_config_dialog(self):
		
		self.Load_config_dialog = Load_config_dialog.Load_config_dialog(self, self.config, self.load_, self.initUI_, self.cwd)
		self.Load_config_dialog.exec()
		
		
	def email_data_dialog(self):
		
		self.Send_email_dialog = Send_email_dialog.Send_email_dialog(self, self.cwd)
		self.Send_email_dialog.exec()
		
		
	def email_set_dialog(self):
		
		self.Email_dialog = Email_settings_dialog.Email_dialog(self, self.lcd, self.cwd)
		self.Email_dialog.exec()
		
		
	def helpParamDialog(self):
		
		helpfile=''
		with open('config_Swanepoel_forklaringer.py','r') as f:
			for line in f:
				helpfile = helpfile+line
				
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("Apply the Swanepoel method using the following analysis steps:")
		msg.setInformativeText(helpfile)
		msg.setWindowTitle("Help")
		#msg.setDetailedText(helpfile)
		msg.setStandardButtons(QMessageBox.Ok)
		#msg.setGeometry(1000, 0, 1000+250, 350)
		
		msg.exec_()
		
		
	def contactDialog(self):
		
		QMessageBox.information(self, "Contact information","Suggestions, comments or bugs can be reported to vedran.furtula@ntnu.no")
		
		
	def onActivated1(self, text):
		
		self.fit_poly_order = int(text)
		
		
	def onActivated2(self, text):
		
		self.plot_X = str(text)
		
		
	def onActivated4(self, text):
		
		self.fit_linear_spline=str(text)
		
		
	def save_figs_check(self, state):
		  
		if state in [Qt.Checked,True]:
			self.save_figs=True
		else:
			self.save_figs=False
			
			
	def sub_olis_check(self, state):
		  
		if state in [Qt.Checked,True]:
			self.loadSubOlis_check=True
			self.loadSubOlisFile_lbl.setStyleSheet("color: magenta")
			self.cb_sub_olis.setText('incl')
		else:
			self.loadSubOlis_check=False
			self.loadSubOlisFile_lbl.setStyleSheet("color: grey")
			self.cb_sub_olis.setText('exc')
			
			
	def subfilm_olis_check(self, state):
		
		if state in [Qt.Checked,True]:
			self.loadSubFilmOlis_check=True
			self.loadSubFilmOlisFile_lbl.setStyleSheet("color: magenta")
			self.cb_subfilm_olis.setText('incl')
		else:
			self.loadSubFilmOlis_check=False
			self.loadSubFilmOlisFile_lbl.setStyleSheet("color: grey")
			self.cb_subfilm_olis.setText('exc')
			
			
	def sub_ftir_check(self, state):

		if state in [Qt.Checked,True]:
			self.loadSubFTIR_check=True
			self.loadSubFTIRFile_lbl.setStyleSheet("color: magenta")
			self.cb_sub_ftir.setText('incl')
		else:
			self.loadSubFTIR_check=False
			self.loadSubFTIRFile_lbl.setStyleSheet("color: grey")
			self.cb_sub_ftir.setText('exc')
			
			
	def subfilm_ftir_check(self, state):
		
		if state in [Qt.Checked,True]:
			self.loadSubFilmFTIR_check=True
			self.loadSubFilmFTIRFile_lbl.setStyleSheet("color: magenta")
			self.cb_subfilm_ftir.setText('incl')
		else:
			self.loadSubFilmFTIR_check=False
			self.loadSubFilmFTIRFile_lbl.setStyleSheet("color: grey")
			self.cb_subfilm_ftir.setText('exc')
			
			
	def polybord_check(self, state):
		
		if state in [Qt.Checked,True]:
			self.fit_poly_ranges_check=True
			self.poly_bordersEdit.setEnabled(True)
			self.cb_polybord.setText('incl')
		else:
			self.fit_poly_ranges_check=False
			self.poly_bordersEdit.setEnabled(False)
			self.cb_polybord.setText('exc')
			
			
	############################################################
	
	
	# Check input if a number, ie. digits or fractions such as 3.141
	# Source: http://www.pythoncentral.io/how-to-check-if-a-string-is-a-number-in-python-including-unicode/
	def is_int(self,s):
		try: 
		  int(s)
		  return True
		except ValueError:
		  return False

	def is_number(self,s):
		try:
			float(s)
			return True
		except ValueError:
			pass

		try:
			import unicodedata
			unicodedata.numeric(s)
			return True
		except (TypeError, ValueError):
			pass

		return False
	
	
	def create_file(self,mystr):
		
		head, ext = os.path.splitext(mystr)
		
		totalpath = ''.join([self.cwd,os.sep,head,'_',self.timetrace])
		
		my_dir = os.path.dirname(totalpath)
		if not os.path.isdir(my_dir):
			QMessageBox.warning(self, "Message","".join(["Folder(s) named ",my_dir," will be created!"]))
			
		try:
			os.makedirs(my_dir, exist_ok=True)
		except Exception as e:
			QMessageBox.critical(self, "Message","".join(["Folder named ",head," not valid!\n\n",str(e)]))
			return ""
		
		return totalpath
	
	
	def set_run(self):
		
		# Save all the currently changed varaibles
		self.save_()
		# Register the sender of the command (a button or similar)
		sender = self.sender()
		
		## gaussian_borders and gaussian_factors warnings and errors
		gaus_bord=str(self.bordersEdit.text()).split(',')
		for tal in gaus_bord:
			if not self.is_number(tal):
				QMessageBox.critical(self, 'Message', "Gaussian borders must be real numbers!")
				return
			elif float(tal)<0.0:
				QMessageBox.critical(self, 'Message', "Gaussian borders must be positive or zero!")
				return

		if len(gaus_bord)<2:
			QMessageBox.critical(self, 'Message', "You must enter at least 2 gaussian borders!")
			return
		
		if not numpy.array_equal([numpy.float(i) for i in gaus_bord],numpy.sort([numpy.float(i) for i in gaus_bord])):
			QMessageBox.critical(self, 'Message', "The gaussian borders must be entered in the ascending order!")
			return

		gaus_fact=str(self.factorsEdit.text()).split(',')
		for tal in gaus_fact:
			if not self.is_number(tal):
				QMessageBox.critical(self, 'Message', "Gaussian factors must be real numbers!")
				return
			elif float(tal)<0.0:
				QMessageBox.critical(self, 'Message', "Gaussian factors must be positive or zero!")
				return
		
		if len(gaus_fact) < 1:
			QMessageBox.critical(self, 'Message', "You must enter at least 1 gaussian factor!")
			return
				
		if len(gaus_bord) != len(gaus_fact)+1:
			QMessageBox.critical(self, 'Message', "The number of gaussian factors is exactly one less than the number of gaussian borders!")
			return


		## ignored data points warnings and errors
		ign_pts=str(self.ignore_data_ptsEdit.text())
		if not self.is_int(ign_pts):
			QMessageBox.critical(self, 'Message', "The number of ignored points is an integer!")
			return
		elif int(ign_pts)<0:
			QMessageBox.critical(self, 'Message', "The number of ignored points is a positive integer!")
			return
		
		
		## correction slit width warnings and errors
		corr_pts=str(self.corr_slitEdit.text())
		if not self.is_number(corr_pts):
			QMessageBox.critical(self, 'Message', "The correction slit width is a real number!")
			return
		elif float(corr_pts)<0:
			QMessageBox.critical(self, 'Message', "The correction slit width is a positive number!")
			return


		## fit_poly_ranges warnings and errors
		if self.fit_poly_ranges_check==True:
			polyfit_bord=str(self.poly_bordersEdit.text()).split(',')
			for tal in polyfit_bord:
				if not self.is_number(tal):
					QMessageBox.critical(self, 'Message', "The polyfit range enteries must be real numbers!")
					return
				elif float(tal)<0.0:
					QMessageBox.critical(self, 'Message', "The polyfit range enteries must be positive or zero!")
					return
				
			if len(polyfit_bord)<2 or len(polyfit_bord)%2!=0:
				QMessageBox.critical(self, 'Message', "The polyfit range list accepts minimum 2 or even number of enteries!")
				return

			if not numpy.array_equal([numpy.float(i) for i in polyfit_bord],numpy.sort([numpy.float(i) for i in polyfit_bord])):
				QMessageBox.critical(self, 'Message', "The polyfit range list must be entered in ascending order!")
				return
		
		
		# When all user defined enteries are approved save the data
		self.create_file(str(self.filenameEdit.text()))
		
		if sender.text()!='Raw data':
			
			## raw data files warnings and errors
			if not self.loadSubOlis_check and not self.loadSubFilmOlis_check:
				pass
			elif self.loadSubOlis_check and self.loadSubFilmOlis_check:
				pass
			else:
				QMessageBox.critical(self, 'Message', "Select both OLIS data files subfilmRAW and subRAW!")
				return
			
			if not self.loadSubFTIR_check and not self.loadSubFilmFTIR_check:
				pass
			elif self.loadSubFTIR_check and self.loadSubFilmFTIR_check:
				pass
			else:
				QMessageBox.critical(self, 'Message', "Select both FTIR data files subfilmRAW and subRAW!")
				return
			
			if not self.loadSubOlis_check and not self.loadSubFilmOlis_check and not self.loadSubFTIR_check and not self.loadSubFilmFTIR_check:
				QMessageBox.critical(self, 'Message', "No data files selected!")
				return

		if sender.text()=='Raw data':
			
			if not self.loadSubOlis_check and not self.loadSubFilmOlis_check and not self.loadSubFTIR_check and not self.loadSubFilmFTIR_check:
				QMessageBox.critical(self, 'Message', "No raw data files selected!")
				return
			
			self.button_style(self.Step0_Button,'red')
			self.button_style(self.Step1_Button,'grey')
			self.button_style(self.Step2_Button,'grey')
			self.button_style(self.Step3_Button,'grey')
			self.button_style(self.Step4_Button,'grey')
			self.button_style(self.Step5_Button,'grey')
			
		elif sender.text()=='Tmin and Tmax':
			
			self.button_style(self.Step1_Button,'red')
			self.button_style(self.Step0_Button,'grey')
			self.button_style(self.Step2_Button,'grey')
			self.button_style(self.Step3_Button,'grey')
			self.button_style(self.Step4_Button,'grey')
			self.button_style(self.Step5_Button,'grey')
			
		elif sender.text()=='Std.Dev. in d':
			
			self.button_style(self.Step2_Button,'red')
			self.button_style(self.Step0_Button,'grey')
			self.button_style(self.Step1_Button,'grey')
			self.button_style(self.Step3_Button,'grey')
			self.button_style(self.Step4_Button,'grey')
			self.button_style(self.Step5_Button,'grey')
			
		elif sender.text()=='Index n':
			
			self.button_style(self.Step3_Button,'red')
			self.button_style(self.Step0_Button,'grey')
			self.button_style(self.Step1_Button,'grey')
			self.button_style(self.Step2_Button,'grey')
			self.button_style(self.Step4_Button,'grey')
			self.button_style(self.Step5_Button,'grey')
			
		elif sender.text()=='Absorption alpha':
			
			self.button_style(self.Step4_Button,'red')
			self.button_style(self.Step0_Button,'grey')
			self.button_style(self.Step1_Button,'grey')
			self.button_style(self.Step2_Button,'grey')
			self.button_style(self.Step3_Button,'grey')
			self.button_style(self.Step5_Button,'grey')
			
		elif sender.text()=='Wavenumber k':
			
			self.button_style(self.Step5_Button,'red')
			self.button_style(self.Step0_Button,'grey')
			self.button_style(self.Step1_Button,'grey')
			self.button_style(self.Step2_Button,'grey')
			self.button_style(self.Step3_Button,'grey')
			self.button_style(self.Step4_Button,'grey')
			
		else:
			return
		
		worker = Worker(sender.text(),self.cwd)
		
		worker.signals.pass_plots.connect(self.pass_plots)
		worker.signals.critical.connect(self.critical)
		worker.signals.finished.connect(self.finished)
		
		# Execute
		self.threadpool.start(worker)
		self.isRunning = True
			
			
	def pass_plots(self,obj):
		
		self.my_plots, sender = obj
		
		my_str='Data files:\n'
		try:
			self.datafiles=self.my_plots.make_plots()
			for i,ii in zip(self.datafiles,range(len(self.datafiles))):
				head, tail = os.path.split(i)
				my_str+=''.join([str(ii+1),': ',tail,'\n'])

			self.NewFiles.setText(my_str)
			self.my_plots.show_plots()
			
		except Exception as inst:
			QMessageBox.critical(self, 'Message', str(inst))
			
			
	def load_(self):
		
		# Initial read of the config file
		self.config = configparser.ConfigParser()
		
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
			self.gaussian_factors = self.config.get(self.last_used_scan,'gaussian_factors')
			self.gaussian_borders = self.config.get(self.last_used_scan,'gaussian_borders')
			self.ignore_data_pts = self.config.get(self.last_used_scan,'ignore_data_pts')
			self.corr_slit = self.config.get(self.last_used_scan,'corr_slit')
			self.fit_poly_order = self.config.get(self.last_used_scan,'fit_poly_order')
			self.fit_poly_ranges = self.config.get(self.last_used_scan,'fit_poly_ranges').strip().split(':')[0]
			self.fit_poly_ranges_check = self.bool_(self.config.get(self.last_used_scan,'fit_poly_ranges').strip().split(':')[1])
			self.filename_str = self.config.get(self.last_used_scan,'filename')
			self.timetrace = self.config.get(self.last_used_scan,'timetrace')
			self.save_figs = self.bool_(self.config.get(self.last_used_scan,'save_figs'))
			self.plot_X = self.config.get(self.last_used_scan,'plot_x')
			self.emailset_str = self.config.get(self.last_used_scan,'emailset').strip().split(',')
			self.emailrec_str = self.config.get(self.last_used_scan,'emailrec').strip().split(',')
			
		except configparser.NoOptionError as nov:
			QMessageBox.critical(self, 'Message',''.join(["Main FAULT while reading the config.ini file\n",str(nov)]))
			raise
		
		
	def save_(self):
		
		self.timetrace=time.strftime("%y%m%d-%H%M")
		self.lcd.display(self.timetrace)
		
		self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
		self.config.set('LastScan',"last_used_scan", self.last_used_scan )
		self.config.set(self.last_used_scan,"loadSubOlis", ':'.join([self.loadSubOlis_str, str(self.loadSubOlis_check)]) )
		self.config.set(self.last_used_scan,"loadSubFilmOlis", ':'.join([self.loadSubFilmOlis_str, str(self.loadSubFilmOlis_check)]) )
		self.config.set(self.last_used_scan,"loadSubFTIR", ':'.join([self.loadSubFTIR_str, str(self.loadSubFTIR_check)]) )
		self.config.set(self.last_used_scan,"loadSubFilmFTIR", ':'.join([self.loadSubFilmFTIR_str, str(self.loadSubFilmFTIR_check)]) )
		self.config.set(self.last_used_scan,"fit_linear_spline", self.fit_linear_spline )
		self.config.set(self.last_used_scan,"gaussian_factors", str(self.factorsEdit.text()) )
		self.config.set(self.last_used_scan,"gaussian_borders", str(self.bordersEdit.text()) )
		self.config.set(self.last_used_scan,"ignore_data_pts", str(self.ignore_data_ptsEdit.text()) )
		self.config.set(self.last_used_scan,"corr_slit", str(self.corr_slitEdit.text()) )
		self.config.set(self.last_used_scan,"fit_poly_order", str(self.fit_poly_order) ) 
		self.config.set(self.last_used_scan,"fit_poly_ranges", ':'.join([ str(self.poly_bordersEdit.text()), str(self.fit_poly_ranges_check)]) )
		self.config.set(self.last_used_scan,"filename", str(self.filenameEdit.text()) )
		self.config.set(self.last_used_scan,"timetrace", self.timetrace )	
		self.config.set(self.last_used_scan,"save_figs", str(self.save_figs) )
		self.config.set(self.last_used_scan,"plot_x", self.plot_X )
		
		with open(''.join([self.cwd,os.sep,"config.ini"]), "w") as configfile:
			self.config.write(configfile)
		
			
	def finished(self):
		
		self.my_plots.close_plots()
		
		self.load_()
		
		if self.emailset_str[1]=="yes":
			self.send_notif()
		if self.emailset_str[2]=="yes":
			self.send_data()
			
		self.button_style(self.Step0_Button,'black')
		self.button_style(self.Step1_Button,'black')
		self.button_style(self.Step2_Button,'black')
		self.button_style(self.Step3_Button,'black')
		self.button_style(self.Step4_Button,'black')
		self.button_style(self.Step5_Button,'black')
		
		self.isRunning = False
		
		
	def allButtons_torf(self,trueorfalse,*argv):
		
		if argv[0]=='allfalse':
			self.cb_sub_olis.setEnabled(False)
			self.cb_subfilm_olis.setEnabled(False)
			self.cb_sub_ftir.setEnabled(False)
			self.cb_subfilm_ftir.setEnabled(False)
			
			self.poly_bordersEdit.setEnabled(False)
			
		self.fileSave.setEnabled(trueorfalse)
		self.loadMenu.setEnabled(trueorfalse)
		self.emailMenu.setEnabled(trueorfalse)
		
		self.cb_save_figs.setEnabled(trueorfalse)
		self.cb_polybord.setEnabled(trueorfalse)
		
		self.Step0_Button.setEnabled(trueorfalse)
		self.Step1_Button.setEnabled(trueorfalse)
		self.Step2_Button.setEnabled(trueorfalse)
		self.Step3_Button.setEnabled(trueorfalse)
		self.Step4_Button.setEnabled(trueorfalse)
		self.Step5_Button.setEnabled(trueorfalse)
		
		self.combo1.setEnabled(trueorfalse)
		self.combo2.setEnabled(trueorfalse)
		self.combo4.setEnabled(trueorfalse)
		
		self.factorsEdit.setEnabled(trueorfalse)
		self.bordersEdit.setEnabled(trueorfalse)
		self.ignore_data_ptsEdit.setEnabled(trueorfalse)
		self.corr_slitEdit.setEnabled(trueorfalse)
		
		self.filenameEdit.setEnabled(trueorfalse)
		
		
	def warning(self, mystr):
		
		QMessageBox.warning(self, "Message", mystr)
		
		
	def send_notif(self):
		
		contents=["The scan is done. Please visit the experiment site and make sure that all light sources are switched off."]
		subject="The scan is done"
		
		obj = type("obj",(object,),{"subject":subject, "contents":contents, "settings":self.emailset_str, "receivers":self.emailrec_str})
		
		worker=Send_Email_Worker(obj)
		worker.signals.critical.connect(self.critical)
		worker.signals.warning.connect(self.warning)
		worker.signals.finished.connect(self.finished1)
		
		# Execute
		self.md = Indicator_dialog.Indicator_dialog(self, "...sending notification...", "indicators/ajax-loader-ball.gif")
		self.threadpool.start(worker)
		self.isRunning = True
			
			
	def send_data(self):
		
		contents=["The scan is  done and the logged data is attached to this email. Please visit the experiment site and make sure that all light sources are switched off."]
		contents.extend(self.datafiles)
		subject="The scan data from the latest scan!"
		
		obj = type("obj",(object,),{"subject":subject, "contents":contents, "settings":self.emailset_str, "receivers":self.emailrec_str})
		
		worker=Send_Email_Worker(obj)
		worker.signals.critical.connect(self.critical)
		worker.signals.warning.connect(self.warning)
		worker.signals.finished.connect(self.finished1)
		
		# Execute
		self.md = Indicator_dialog.Indicator_dialog(self, "...sending files...", "indicators/ajax-loader-ball.gif")
		self.threadpool.start(worker)
		self.isRunning = True
		
		
	def finished1(self):
		
		self.isRunning = False
		self.md.close_()
		
		
	def critical(self,mystr):
		
		QMessageBox.critical(self, 'Message',mystr)
		
		
	def closeEvent(self,event):
		
		reply = QMessageBox.question(self, 'Message', "Quit now?", QMessageBox.Yes | QMessageBox.No)
		if reply == QMessageBox.Yes:
			if self.isRunning:
				QMessageBox.warning(self, 'Message', "Analysis in progress. Wait the analysis to finish and then quit!")
				event.ignore()
			else:
				event.accept()
		elif reply == QMessageBox.No:
			event.ignore()  
			
			
#########################################
#########################################
#########################################
	
	
def main():
	
	app = QApplication(sys.argv)
	ex = Run_gui()
	#sys.exit(app.exec_())

	# avoid message 'Segmentation fault (core dumped)' with app.deleteLater()
	app.exec()
	app.deleteLater()
	sys.exit()
	
	
if __name__ == '__main__':
	
	main()
