#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""



import time

from PyQt5.QtWidgets import (QDialog, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton)





class Message_dialog(QDialog):
	
	def __init__(self, parent, title, msg):
		super().__init__(parent)
		
		# constants
		self.title = title
		self.msg = msg
		
		self.closenow=False
		self.setupUi()
		
		
	def setupUi(self):
		
		dummy = QLabel(" ",self)
		dummy.setFixedWidth(30)
		
		
		lb0 = QLabel(self.msg,self)
		
		grid_0 = QHBoxLayout()
		grid_0.addWidget(dummy)
		grid_0.addWidget(lb0)
		grid_0.addWidget(dummy)
		
		self.setLayout(grid_0)
		self.setWindowTitle(self.title)
		self.setModal(True)
		self.show()
		
		
	def close_(self):
		
		self.closenow=True
		self.close()
		
	
	def closeEvent(self,event):
		
		if self.closenow:
			event.accept()
		else:
			event.ignore()
		
		
		
		
		
		
		
		
		
		
		
		
		
