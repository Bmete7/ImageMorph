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
from scipy.spatial import Delaunay


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
    
    def TargetImage(self,fN):    
        
        self.qpTarget = QPixmap(fN)
        
        self.labTarget.setPixmap(self.qpTarget) 
        
        self.vBox2.addWidget(self.labTarget)
        
        
        
    def InputImage(self,fN):
        
        self.qpInput = QPixmap(fN)
        self.labInput.setPixmap(self.qpInput)
        self.labInput.move(50,50)
        self.vBox1.addWidget(self.labInput)


    def ResultImage(self,fN,val):
        print('smth')
        
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.title = "Histogram Matching"
        self.top = 1000
        self.left = 200
        self.width = 500
        self.height = 500
        self.inputImage = None
        self.targetImage = None
        self.result = None
        self.inputFile = ''
        self.targetFile= ''
        self.selectedPoints = 0
        self.pointCount = 20
        self.fP= None
        self.initWindow()
        self.inputPoints= np.zeros((20,2) ,dtype = 'int32')
        self.targetPoints= np.zeros((20,2) ,dtype = 'int32')
        self.inputTrianglePoints = []
        self.targetTrianglePoints = []
        self.inputTriangle = np.zeros((6,6) ,dtype = 'int32')
        self.targetTriangle =  np.zeros((6,6) ,dtype = 'int32')
        
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
        if( fileName == ''):
            return
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
        if( fileName == ''):
            return
        self.targetFile = fileName[0]
        self.targetImage = cv2.imread(fileName[0])
        self.targetImage = cv2.cvtColor(self.targetImage,cv2.COLOR_BGR2RGB)
        self.content = ExampleContent(self, self.inputFile,self.targetFile)
        self.setCentralWidget(self.content)
        
        try:    
            self.fP = open((self.targetFile[:-3] + 'txt'), 'r')
      
            for i in range(0,self.pointCount):
                
                str_point = self.fP.readline()
                self.targetPoints[i,0] = str_point.split('\t')[0]
                self.targetPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()
        except:
            self.fP = open((self.targetFile[:-3] + 'txt'), 'w')
            self.getImageCoordinates(self.targetFile)
            self.fP.close()
        
     
    def createResultImage(self):
        print('Result')
    def createMorph(self):
        print('morphing phase')
    def draw_point(self,img, p, color ) :
        cv2.circle( img, p, 2, color, cv2.FILLED, cv2.LINE_AA, 0 )
    def rect_contains(self,rect, point) :
        if point[0] < rect[0] :
            return False
        elif point[1] < rect[1] :
            return False
        elif point[0] > rect[2] :
            return False
        elif point[1] > rect[3] :
            return False
        return True
    
    
    def draw_voronoi(self,img, subdiv):
 
        ( facets, centers) = subdiv.getVoronoiFacetList([])
     
        for i in range(0,len(facets)) :
            ifacet_arr = []
            for f in facets[i] :
                ifacet_arr.append(f)
             
            ifacet = np.array(ifacet_arr, np.int)
            print(ifacet)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
     
            cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0);
            ifacets = np.array([ifacet])
            cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)
            cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), cv2.FILLED, cv2.LINE_AA, 0)
     
    
    def draw_delaunay(self,img, subdiv, delaunay_color,tr_list):
     
        triangleList = subdiv.getTriangleList();
        
        #print(triangleList)
        size = img.shape
        r = (0, 0, size[1], size[0])

        for t in triangleList :
             
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])
             
            
            if self.rect_contains(r, pt1) and self.rect_contains(r, pt2) and self.rect_contains(r, pt3) :
                cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)

        return triangleList                
    def createTriangulation(self):
        if(self.targetFile == '' or self.inputFile == ''):
            return
        self.inputImage = cv2.cvtColor(self.inputImage,cv2.COLOR_BGR2RGB)
        self.targetImage = cv2.cvtColor(self.targetImage,cv2.COLOR_BGR2RGB)
        
        delaunay_color = (255,255,255)
        
        input_size = self.inputImage.shape
        input_size_target = self.targetImage.shape
        
        rect = (0,0,input_size[1], input_size[0])
        rect_target = (0,0,input_size_target[1], input_size_target[0])
        
        img_org = self.inputImage.copy()
        img_org_target = self.targetImage.copy()
        
        subdiv = cv2.Subdiv2D(rect)
        subdiv_target = cv2.Subdiv2D(rect_target)
        points= []
        points_target = []
        
        for i in range(0,self.pointCount):
            points.append((self.inputPoints[i,0] , self.inputPoints[i,1]))
            points_target.append((self.targetPoints[i,0] , self.targetPoints[i,1]))
        
        for p in points:
            subdiv.insert(p)
            img_copy = img_org.copy()
            self.draw_delaunay(img_copy,subdiv,(255,255,255),self.inputTriangle)
            cv2.imshow('deneme', img_copy)
            cv2.waitKey(100)
        
        for p in points_target:
            subdiv_target.insert(p)
            img_copy_target = img_org_target.copy()
            self.draw_delaunay(img_copy_target,subdiv_target,(255,255,255),self.targetTriangle)
            cv2.imshow('deneme_target', img_copy_target)
            cv2.waitKey(100)
        
        
        
        
        tri_list_input = self.draw_delaunay(self.inputImage,subdiv,(255,255,255),self.inputTriangle)
        tri_list_target = self.draw_delaunay(self.targetImage,subdiv_target,(255,255,255),self.targetTriangle)
        
        
        print(tri_list_input)
        
        for p in points:
            self.draw_point(self.inputImage,p,(0,0,255))
        
        for p in points_target:
            self.draw_point(self.targetImage,p,(0,0,255))

        
        img_voronoi= np.zeros(self.inputImage.shape, dtype = self.inputImage.dtype)
        
        self.draw_voronoi(img_voronoi,subdiv)
        
        cv2.imshow('delauney', self.inputImage)
        cv2.imshow('target', self.targetImage)
    
        
        cv2.imwrite('delauneyInput.jpg',self.inputImage)
        cv2.imwrite('delauneyTarget.jpg', self.targetImage)
        
        cv2.destroyAllWindows()
        self.content = ExampleContent(self, 'delauneyInput.jpg','delauneyTarget.jpg')
        self.setCentralWidget(self.content)
        
        
        #tri = Delaunay(points)
        #print(tri.simplices)
        
    
    
if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    cv2.destroyAllWindows()
    sys.exit(App.exec())
    