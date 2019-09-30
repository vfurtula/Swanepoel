#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

import os, re, serial, time, configparser

from PyQt5.QtWidgets import (QDialog, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton)


class Load_config_dialog(QDialog):
	
	def __init__(self, parent, config, load_, initUI_, cwd):
		super().__init__(parent)
		
		# constants
		self.config = config
		self.load_ = load_
		self.initUI_ = initUI_
		self.last_used_scan = self.config.get('LastScan','last_used_scan')
		self.cwd = cwd
		
		self.setupUi()
		
		
	def get_scan_sections(self):
		
		mylist=[]
		for i in self.config.sections():
			if i not in ["LastScan","Instruments"]:
				mylist.extend([i])
		
		return mylist
	
	
	def setupUi(self):
		
		#self.lb0 = QLabel("Receiver(s) comma(,) separated:",self)
		#self.le1 = QLineEdit()
		#self.le1.setText(', '.join([i for i in self.emailrec_str]))
		#self.le1.textChanged.connect(self.on_text_changed)
		
		self.lbl1 = QLabel("Pick a setting from the config file:", self)
		self.combo1 = QComboBox(self)
		mylist1=self.get_scan_sections()
		self.combo1.addItems(mylist1)
		self.combo1.setCurrentIndex(mylist1.index(self.last_used_scan))
		self.combo1.setFixedWidth(300)
		self.combo1.activated[str].connect(self.onActivated1)
		self.current_selected_setting=self.last_used_scan
		
		self.btnLoadSection = QPushButton("Setting loaded",self)
		self.btnLoadSection.clicked.connect(self.btn_load_section)
		self.btnLoadSection.setEnabled(False)
		#self.btnLoadSection.setFixedWidth(90)
		
		self.btnDeleteSection = QPushButton("Delete setting",self)
		self.btnDeleteSection.clicked.connect(self.btn_delete_section)
		self.btnDeleteSection.setText("Can not delete")
		self.btnDeleteSection.setEnabled(False)
		#self.btnDeleteSection.setFixedWidth(90)
		
		self.lbl2 = QLabel("or create a new config setting:", self)
		self.sectionEdit = QLineEdit(self.last_used_scan,self)
		#self.self.sectionEdit.setFixedWidth(90)
		self.sectionEdit.textChanged.connect(self.text_stch)
		
		self.btnAcceptText= QPushButton("Accept new setting",self)
		self.btnAcceptText.clicked.connect(self.btn_accept_text)
		self.btnAcceptText.setEnabled(False)
		#self.btnAcceptText.setFixedWidth(90)
		
		self.lbl3 = QLabel("Currently loaded setting:", self)
		self.lbl4 = QLabel("", self)
		self.lbl4.setStyleSheet("color: red; font: 16pt")
		self.lbl4.setText(self.last_used_scan)
		
		# set layout
		grid_0 = QGridLayout()
		grid_0.addWidget(self.lbl1,0,0)
		grid_0.addWidget(self.combo1,1,0)
		
		grid_1 = QGridLayout()
		grid_1.addWidget(self.btnLoadSection,0,0)
		grid_1.addWidget(self.btnDeleteSection,0,1)
		
		grid_2 = QGridLayout()
		grid_2.addWidget(self.lbl2,0,0)
		grid_2.addWidget(self.sectionEdit,1,0)
		grid_2.addWidget(self.btnAcceptText,2,0)
		grid_2.addWidget(self.lbl3,3,0)
		grid_2.addWidget(self.lbl4,4,0)
		
		v1 = QVBoxLayout()
		v1.addLayout(grid_0)
		v1.addLayout(grid_1)
		v1.addLayout(grid_2)
		
		self.setLayout(v1)
		self.setWindowTitle("Configure settings in the config.ini file")
		
		
	def onActivated1(self, text):
		
		self.current_selected_setting=str(text)
		if str(text)!=self.last_used_scan:
			self.btnLoadSection.setText("*Load setting*")
			self.btnLoadSection.setEnabled(True)
			mylist1=self.get_scan_sections()
			if len(mylist1)>1:
				self.btnDeleteSection.setText("Delete setting")
				self.btnDeleteSection.setEnabled(True)
		else:
			self.btnLoadSection.setText("Setting loaded")
			self.btnLoadSection.setEnabled(False)
			self.btnDeleteSection.setText("Can not delete")
			self.btnDeleteSection.setEnabled(False)
		
		
	def text_stch(self):
		
		mylist1=self.get_scan_sections()
		
		if not str(self.sectionEdit.text()):
			self.btnAcceptText.setText("Empty string not accepted")
			self.btnAcceptText.setEnabled(False)
		elif str(self.sectionEdit.text()) not in mylist1:
			self.btnAcceptText.setText("*Accept new setting*")
			self.btnAcceptText.setEnabled(True)
		else:
			self.btnAcceptText.setText("Setting accepted")
			self.btnAcceptText.setEnabled(False)
			
			
	def btn_load_section(self):
		
		self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
		self.config.set("LastScan","last_used_scan", self.current_selected_setting)
		with open(''.join([self.cwd,os.sep,"config.ini"]), 'w') as configfile:
			self.config.write(configfile)
		
		self.btnLoadSection.setText("Setting loaded")
		self.btnLoadSection.setEnabled(False)
		self.btnDeleteSection.setText("Can not delete")
		self.btnDeleteSection.setEnabled(False)
		
		self.load_()
		self.initUI_()
		self.last_used_scan=self.current_selected_setting
		self.lbl4.setText(self.last_used_scan)
		
		#self.close()
		
		
	def btn_delete_section(self):
		
		try:
			self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
			self.config.remove_section(self.current_selected_setting)
			with open(''.join([self.cwd,os.sep,"config.ini"]), 'w') as configfile:
				self.config.write(configfile)
		except Exception as e:
			QMessageBox.critical(self, 'Message', str(e))
			return
		
		mylist1=self.get_scan_sections()
		self.combo1.clear()
		self.combo1.addItems(mylist1)
		self.combo1.setCurrentIndex(mylist1.index(self.last_used_scan))
		
		self.btnLoadSection.setText("Setting loaded")
		self.btnLoadSection.setEnabled(False)
		self.btnDeleteSection.setText("Can not delete")
		self.btnDeleteSection.setEnabled(False)
		
		if str(self.sectionEdit.text()) not in mylist1:
			self.btnAcceptText.setText("*Accept new setting*")
			self.btnAcceptText.setEnabled(True)
		else:
			self.btnAcceptText.setText("Setting accepted")
			self.btnAcceptText.setEnabled(False)
			
		self.load_()
		self.initUI_()
		
		
	def btn_accept_text(self):
		
		read_text=str(self.sectionEdit.text())
		
		try:
			self.config.add_section(read_text)
		except configparser.DuplicateSectionError as e:
			QMessageBox.critical(self, 'Message', str(e))
			return
		
		self.i = list(dict(self.config.items(self.last_used_scan)).keys())
		self.j = list(dict(self.config.items(self.last_used_scan)).values())
		
		self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
		self.config.set("LastScan","last_used_scan", read_text)
		for i_,j_ in zip(self.i,self.j):
			self.config.set(read_text,i_, j_)
		with open(''.join([self.cwd,os.sep,"config.ini"]), 'w') as configfile:
			self.config.write(configfile)
		
		self.btnLoadSection.setText("Setting loaded")
		self.btnLoadSection.setEnabled(False)
		self.btnDeleteSection.setText("Can not delete")
		self.btnDeleteSection.setEnabled(False)
		
		mylist1=self.get_scan_sections()
		self.combo1.clear()
		self.combo1.addItems(mylist1)
		self.combo1.setCurrentIndex(mylist1.index(read_text))
		
		self.last_used_scan=read_text
		
		self.btnAcceptText.setText("Setting accepted")
		self.btnAcceptText.setEnabled(False)
		self.lbl4.setText(self.last_used_scan)
		
		self.load_()
		self.initUI_()
		
		#self.close()
			
			
	def closeEvent(self,event):
	
		event.accept()
		
