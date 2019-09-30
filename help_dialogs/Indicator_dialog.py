#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""



import re, serial, time

from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import (QDialog, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton)




class Indicator_dialog(QDialog):
	
	def __init__(self, parent, title, mypath):
		super().__init__(parent)
		
		# constants
		self.title = title
		self.mypath = mypath
		
		self.closenow=False
		self.setupUi()
		
		
	def setupUi(self):
		
		dummy = QLabel("",self)
		dummy.setFixedWidth(60)
		
		text = QLabel("Enter the Gmail password\nin the terminal prompt",self)
		
		lbl_movie = QLabel("",self)
		self.movie = QMovie(self.mypath, QByteArray(),self)
		lbl_movie.setMovie(self.movie)
		
		grid_0 = QHBoxLayout()
		grid_0.addWidget(dummy)
		grid_0.addWidget(lbl_movie)
		grid_0.addWidget(dummy)
		
		grid_1 = QVBoxLayout()
		grid_1.addWidget(text)
		grid_1.addLayout(grid_0)
		
		self.setLayout(grid_1)
		self.setWindowTitle(self.title)
		self.movie.start()
		self.setModal(True)
		self.show()
		
		
	def close_(self):
		
		self.movie.stop()
		self.closenow=True
		self.close()
		
	
	def closeEvent(self,event):
		
		if self.closenow:
			event.accept()
		else:
			event.ignore()
		
		
		
		
		
		
		
		
		
		
		
		
		
