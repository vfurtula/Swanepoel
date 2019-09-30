#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

import os, re, time, yagmail, configparser

from PyQt5.QtWidgets import (QDialog, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QCheckBox)





class Email_dialog(QDialog):
	
	def __init__(self, parent, lcd, cwd):
		super().__init__(parent)
		
		# Initial read of the config file
		self.config = configparser.ConfigParser()
		self.cwd = cwd
		
		try:
			self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
			self.last_used_scan = self.config.get('LastScan','last_used_scan')
			
			self.emailset_str = self.config.get(self.last_used_scan,'emailset').strip().split(',')
			self.emailrec_str = self.config.get(self.last_used_scan,'emailrec').strip().split(',')
		except configparser.NoOptionError as e:
			QMessageBox.critical(self, 'Message',''.join(["Main fault while reading the config.ini file\n",str(e)]))
			return
		
		self.lcd = lcd
		
		self.setupUi()
		
		
	def setupUi(self):
		
		grid_0 = QGridLayout()
		
		self.lb4 = QLabel("Active gmail account:",self)
		self.lb5 = QLabel(self.emailset_str[0],self)
		self.lb5.setStyleSheet("color: magenta")
		grid_0.addWidget(self.lb4,0,0)
		grid_0.addWidget(self.lb5,0,1)
		
		self.btnNewGmail = QPushButton("Register account",self)
		self.btnNewGmail.clicked.connect(self.btn_newgmail)
		self.btnNewGmail.setEnabled(False)
		grid_0.addWidget(self.btnNewGmail,1,0)
		
		self.cb_passwd = QCheckBox('Show',self)
		self.cb_passwd.toggle()
		self.cb_passwd.setChecked(True)
		
		grid_2 = QGridLayout()
		self.le2 = QLineEdit("username",self)
		self.le2.setFixedWidth(100)
		self.le2.textChanged.connect(self.on_text_changed2)
		self.le3 = QLineEdit("password",self)
		self.le3.setFixedWidth(100)
		#self.le3.setEchoMode(QLineEdit.Password)
		self.le3.textChanged.connect(self.on_text_changed2)
		grid_2.addWidget(self.le2,0,0)
		grid_2.addWidget(self.le3,0,1)
		grid_2.addWidget(self.cb_passwd,0,2)
		grid_0.addLayout(grid_2,1,1)
		
		self.lb1 = QLabel("Receiver(s) comma(,) separated:",self)
		self.le1 = QLineEdit()
		self.le1.setText(', '.join([i for i in self.emailrec_str]))
		self.le1.textChanged.connect(self.on_text_changed)
		grid_0.addWidget(self.lb1,2,0)
		grid_0.addWidget(self.le1,2,1)
		
		############################################################################
		
		self.lb2 = QLabel("Send notification when scan is done?",self)
		self.cb2 = QComboBox(self)
		mylist=["yes","no"]
		self.cb2.addItems(mylist)
		self.cb2.setCurrentIndex(mylist.index(self.emailset_str[1]))
		grid_0.addWidget(self.lb2,3,0)
		grid_0.addWidget(self.cb2,3,1)
		
		self.lb3 = QLabel("Send data when scan is done?",self)
		self.cb3 = QComboBox(self)
		self.cb3.addItems(mylist)
		self.cb3.setCurrentIndex(mylist.index(self.emailset_str[2]))
		grid_0.addWidget(self.lb3,4,0)
		grid_0.addWidget(self.cb3,4,1)
		
		if self.emailset_str[2]=="yes":
			self.emailset_str[1] = "no"
			self.cb2.setCurrentIndex(mylist.index("no"))
			self.cb2.setEnabled(False)
		elif self.emailset_str[2]=="no":
			self.cb2.setEnabled(True)
			
		############################################################################
		
		self.btnSave = QPushButton("Changes saved",self)
		self.btnSave.clicked.connect(self.btn_accepted)
		self.btnSave.setEnabled(False)
		
		grid_1 = QGridLayout()
		grid_1.addWidget(self.btnSave,0,0)
		
		self.cb2.activated[str].connect(self.onActivated2)
		self.cb3.activated[str].connect(self.onActivated3)
		self.cb_passwd.toggled.connect(self.passwd)
		
		v0 = QVBoxLayout()
		v0.addLayout(grid_0)
		v0.addLayout(grid_1)
		
		self.setLayout(v0)
		self.setWindowTitle("E-mail settings")
		
		
	def onActivated2(self, text):
		
		self.emailset_str[1] = str(text)
		self.btnSave.setText("*Save changes*")
		self.btnSave.setEnabled(True)
		
		
	def onActivated3(self, text):
		
		self.emailset_str[2] = str(text)
		self.btnSave.setText("*Save changes*")
		self.btnSave.setEnabled(True)
		
		if self.emailset_str[2]=="yes":
			self.emailset_str[1] = "no"
			mylist=["yes","no"]
			self.cb2.setCurrentIndex(mylist.index("no"))
			self.cb2.setEnabled(False)
		elif self.emailset_str[2]=="no":
			self.cb2.setEnabled(True)
		
		
	def on_text_changed(self):
		
		self.emailrec_str = str(self.le1.text()).split(',')
		self.emailrec_str = [emails.strip() for emails in self.emailrec_str]
		
		for emails in self.emailrec_str:
			if not re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", emails):
				self.btnSave.setText("*Invalid e-mail(s)*")
				self.btnSave.setEnabled(False)
			else:
				self.btnSave.setText("*Save changes*")
				self.btnSave.setEnabled(True)
				
				
	def on_text_changed2(self):
		
		if str(self.le2.text())!="username" and len(str(self.le2.text()))>0:
			if str(self.le3.text())!="password" and len(str(self.le3.text()))>0:
				self.btnNewGmail.setText("Register account")
				self.btnNewGmail.setEnabled(True)
			else:
				self.btnNewGmail.setText("*Invalid account*")
				self.btnNewGmail.setEnabled(False)
		else:
			self.btnNewGmail.setText("*Invalid account*")
			self.btnNewGmail.setEnabled(False)
			
			
	def passwd(self):
		
		if not self.cb_passwd.isChecked():
			self.le3.setEchoMode(QLineEdit.Password)
		else:
			self.le3.setEchoMode(QLineEdit.Normal)
			
			
	def btn_newgmail(self):
		
		try:
			yagmail.register(''.join([str(self.le2.text()),'@gmail.com']),str(self.le3.text()))
		except Exception as e:
			QMessageBox.critical(self, 'Message',''.join(["Could not register the gmail account\n",str(e)]))
			return
			
		self.btnNewGmail.setText("Account registered")
		self.btnNewGmail.setEnabled(False)
		
		self.emailset_str[0]=str(self.le2.text())
		self.lb5.setText(self.emailset_str[0])
		self.btnSave.setText("*Save changes*")
		self.btnSave.setEnabled(True)
		
		
	def btn_accepted(self):
		
		self.save_()
		
		self.btnSave.setText("Changes saved")
		self.btnSave.setEnabled(False)
		
		
	def save_(self):
		
		self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
		self.config.set(self.last_used_scan, 'emailrec', ','.join([i for i in self.emailrec_str]))
		self.config.set(self.last_used_scan, 'emailset', ','.join([i for i in self.emailset_str]))
		
		with open(''.join([self.cwd,os.sep,"config.ini"]), 'w') as configfile:
			self.config.write(configfile)
			
			
			
			
			
