#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""

import re, serial, time

from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import (QDialog, QWidget, QMessageBox, QGridLayout, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton)


class Indicator_invs_dialog(QDialog):
	
	def __init__(self, parent, title, textcolor, mypath):
		super().__init__(parent)
		
		# constants
		self.title = title
		self.mypath = mypath
		self.textcolor = textcolor
		
		self.closenow=False
		self.setupUi()
		
		
	def setupUi(self):
		
		title = QLabel(self.title,self)
		title.setStyleSheet(''.join(["QWidget {font: 14pt; color: ",self.textcolor,"}"]))
		
		lbl_movie = QLabel("",self)
		self.movie = QMovie(self.mypath, QByteArray(),self)
		lbl_movie.setMovie(self.movie)
		lbl_movie.setAlignment(Qt.AlignCenter)
		
		grid_0 = QVBoxLayout()
		grid_0.addWidget(title)
		grid_0.addWidget(lbl_movie)
		
		self.setLayout(grid_0)
		self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		
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
		
		
		
		
		
		
		
		
		
		
		
		
		
