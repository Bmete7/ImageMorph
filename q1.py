# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:44:14 2018

@author: BurakBey
"""


import cv2
 
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random



class ExampleContent(QWidget):
    def __init__(self, parent,fileName1,fileName2):
        self.parent = parent
        self.labInput= QLabel()
        self.labTarget= QLabel()
        self.qpTarget = None
        self.qpInput = None
        QWidget.__init__(self, parent)
        self.initUI(fileName1,fileName2)
        
        
    def initUI(self,fileName1,fileName2):        

        groupBox1 = QGroupBox('Input File')
        self.vBox1 = QVBoxLayout()
        
        groupBox1.setLayout(self.vBox1)
        
        groupBox2 = QGroupBox('Target File')
        self.vBox2 = QVBoxLayout()
        groupBox2.setLayout(self.vBox2)
        
        groupBox3 = QGroupBox('Output File')
        self.vBox3 = QVBoxLayout()
        groupBox3.setLayout(self.vBox3)
        hBox = QHBoxLayout()
        
        hBox.addWidget(groupBox1)
        hBox.addWidget(groupBox2)
        hBox.addWidget(groupBox3)
        

        self.setLayout(hBox)
        self.setGeometry(0, 0, 0,0)
        self.InputImage(fileName1)
        self.TargetImage(fileName2)
        self.labTarget.mousePressEvent = self.GetCoord
    
    def TargetImage(self,fN):    
        
        self.qpTarget = QPixmap(fN)
        
        self.labTarget.setPixmap(self.qpTarget) 
        
        self.vBox2.addWidget(self.labTarget)
        
    def GetCoord(self,event):
        print(event.pos())
        
        
    def InputImage(self,fN):
        
        self.qpInput = QPixmap(fN)
        self.labInput.setPixmap(self.qpInput)
        self.labInput.move(50,50)
        self.qpInput
        self.vBox1.addWidget(self.labInput)
        print(self.labInput.x())
        print(self.labInput.pos())

    def ResultImage(self,fN,val):
        print('smth')
        
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.title = "Histogram Matching"
        self.top = 50
        self.left = 50
        self.width = 1800
        self.height = 1200
        self.inputImage = None
        self.TargetImage = None
        self.result = None
        self.inputFile = ''
        self.targetFile= ''
        self.selectedPoints = 0
        self.pointCount = 20
        self.fP= None
        self.initWindow()
        self.inputPoints= np.zeros((20,2) ,dtype = 'int32')
        self.targetPoints= np.zeros((20,2) ,dtype = 'int32')

        
    def initWindow(self):
         
        exitAct = QAction(QIcon('exit.png'), '&Exit' , self)
        importAct = QAction('&Open Input' , self)
        targetAct = QAction('&Open Target' , self)
        triangleAction = QAction('&Create Triangulation' , self)
        morphAction = QAction('&Morph' , self)
    
        exitAct.setShortcut('Ctrl+Q')
        
        exitAct.setStatusTip('Exit application')
        importAct.setStatusTip('Open Input')
        targetAct.setStatusTip('Open Target')
        
        exitAct.triggered.connect(self.closeApp)
        importAct.triggered.connect(self.importInput)
        targetAct.triggered.connect(self.importTarget)
        triangleAction.triggered.connect(self.createTriangulation)
        morphAction.triggered.connect(self.createMorph)
        
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        
        fileMenu.addAction(exitAct)
        fileMenu.addAction(importAct)
        fileMenu.addAction(targetAct)

        self.content = ExampleContent(self, '', '')
        self.setCentralWidget(self.content)
        
        self.triangleToolbar = self.addToolBar('Create Triangulation')
        self.triangleToolbar.addAction(triangleAction)
        
        self.morphToolbar = self.addToolBar('Morph')
        self.morphToolbar.addAction(morphAction)
        
        self.setWindowTitle(self.title)
        self.setStyleSheet('QMainWindow{background-color: darkgray;border: 1px solid black;}')
        self.setGeometry( self.top, self.left, self.width, self.height)
        self.show()
    

            
    def savePoints(self,event,x,y,flags,param):
        
        if event == cv2.EVENT_LBUTTONDOWN:            
            print(str(x) + '\t' + str(y))
            self.fP.write(str(x) + '\t' + str(y) +'\n')
            self.selectedPoints += 1

    def closeApp(self):
        sys.exit()
    

        
    def getImageCoordinates(self,fN):
        self.selectedPoints = 0
        I = cv2.imread(fN)       
        cv2.namedWindow('Im')
        cv2.setMouseCallback('Im',self.savePoints)
        while(self.selectedPoints < self.pointCount):
            cv2.imshow('Im',I)
            k = cv2.waitKey(1)
            if k == 27:
                break
        cv2.destroyAllWindows()
    def importInput(self):
        fileName = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Png Files (*.png)")
        self.inputFile = fileName[0]
        self.inputImage = cv2.imread(fileName[0])
        self.inputImage = cv2.cvtColor(self.inputImage,cv2.COLOR_BGR2RGB)
        
        self.content = ExampleContent(self, self.inputFile,self.targetFile)
        self.setCentralWidget(self.content)

        self.input_points = np.zeros((20,2), dtype= 'int32')
        try:    
            self.fP = open((self.inputFile[:-3] + 'txt'), 'r')
            for i in range(0,self.pointCount):
                str_points = self.fP.readline()
                
                self.inputPoints[i,0] = str_points.split('\t')[0]
                self.inputPoints[i,1] = str_points.split('\t')[1]
                
            self.fP.close()
        except:
            self.fP = open((self.inputFile[:-3] + 'txt'), 'w')
            self.getImageCoordinates(self.inputFile)
            self.fP.close()

    def importTarget(self):
        fileName = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Png Files (*.png)")
        self.targetFile = fileName[0]
        self.targetImage = cv2.imread(fileName[0])
        self.targetImage = cv2.cvtColor(self.targetImage,cv2.COLOR_BGR2RGB)
        self.content = ExampleContent(self, self.inputFile,self.targetFile)
        self.setCentralWidget(self.content)
        
        try:    
            self.fP = open((self.targetFile[:-3] + 'txt'), 'r')
      
            for i in range(0,self.pointCount-1):
                
                str_point = self.fP.readline()
                self.targetPoints[i,0] = str_point.split('\t')[0]
                self.targetPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()
        except:
            self.fP = open((self.targetFile[:-3] + 'txt'), 'w')
            self.getImageCoordinates(self.targetFile)
            self.fP.close()
        
        print(self.targetPoints)
        print(self.inputPoints)
    def createResultImage(self):
        print('smth')
    def createMorph(self):
        print('morphing phase')
    def createTriangulation():
        print('triangulation')
    
    
if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    cv2.destroyAllWindows()
    sys.exit(App.exec())
    