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
import math
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from scipy.spatial import Delaunay


class ExampleContent(QWidget):
    def __init__(self, parent,fileName1,fileName2,fileName3=''):
        self.parent = parent
        self.labInput= QLabel()
        self.labTarget= QLabel()
        self.labResult= QLabel()
        self.qpTarget = None
        self.qpInput = None
        self.qpResult = None
        QWidget.__init__(self, parent)
        self.initUI(fileName1,fileName2,fileName3)
        
        
    def initUI(self,fileName1,fileName2,fileName3= ''):        

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
        if fileName3 != '':
            self.ResultImage(fileName3)
    
    def TargetImage(self,fN):    
        
        self.qpTarget = QPixmap(fN)
        
        self.labTarget.setPixmap(self.qpTarget) 
        
        self.vBox2.addWidget(self.labTarget)
        
        
        
    def InputImage(self,fN):
        
        self.qpInput = QPixmap(fN)
        self.labInput.setPixmap(self.qpInput)
        self.labInput.move(50,50)
        self.vBox1.addWidget(self.labInput)


    def ResultImage(self,fN):
        self.qpResult = QPixmap(fN)
        self.labResult.setPixmap(self.qpResult)
        
        self.vBox3.addWidget(self.labResult)
        
        
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
        self.inputImageTemp = None
        self.targetImageTemp = None
        self.result = None
        self.inputFile = ''
        self.targetFile= ''
        self.selectedPoints = 0
        self.pointCount = 20
        self.fP= None
        self.initWindow()
        self.inputPoints= np.zeros((20,2) ,dtype = 'int32')
        self.inputEdges= []
        self.targetEdges= []
        self.targetPoints= np.zeros((20,2) ,dtype = 'int32')
        self.inputTrianglePoints = None
        self.targetTrianglePoints = None
        self.affine_parameters = None
        self.inputTriangleMorph = None
        self.targetTriangleMorph = None
        self.triCount = 0 
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
    
    def sortPoints(self,arr): # insertion sort for selected feature points
        for i in range(1,(self.pointCount) -1 ):
            key = arr[i,0]
            little_key = arr[i,1]
            j  = i - 1
            
            while(j>= 0 and (arr[j,0] < key or (arr[j,0] == key and (arr[j,1] <  little_key)))):
                arr[j+1,0] = arr[j,0]
                arr[j+1,1] = arr[j,1]
                j -= 1
            arr[j+1,0] = key
            arr[j+1,1] = little_key
                
        return arr
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
        self.inputImageTemp = cv2.imread(fileName[0])
        self.inputImageTemp = cv2.cvtColor(self.inputImageTemp,cv2.COLOR_BGR2RGB)
        self.content = ExampleContent(self, self.inputFile,self.targetFile)
        self.setCentralWidget(self.content)

        self.input_points = np.zeros((20,2), dtype= 'int32')
        try:    
            self.fP = open((self.inputFile[:-3] + 'txt'), 'r')
            for i in range(0,self.pointCount):
                str_point = self.fP.readline()
                self.inputEdges.append(list(map(lambda x: int(x.strip()), str_point.split('\t'))))
                self.inputPoints[i,0] = str_point.split('\t')[0]
                self.inputPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()
        except:
            self.fP = open((self.inputFile[:-3] + 'txt'), 'w')
            self.getImageCoordinates(self.inputFile)
            self.fP.close()
            self.fP = open((self.inputFile[:-3] + 'txt'), 'r')
            for i in range(0,self.pointCount):
                str_point = self.fP.readline()
                self.inputEdges.append(list(map(lambda x: int(x.strip()), str_point.split('\t'))))
                self.inputPoints[i,0] = str_point.split('\t')[0]
                self.inputPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()

    def importTarget(self):
        fileName = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Png Files (*.png)")
        if( fileName == ''):
            return
        self.targetFile = fileName[0]
        self.targetImage = cv2.imread(fileName[0])
        
        self.targetImage = cv2.cvtColor(self.targetImage,cv2.COLOR_BGR2RGB)
        self.targetImageTemp = cv2.imread(fileName[0])
        self.targetImageTemp = cv2.cvtColor(self.targetImageTemp,cv2.COLOR_BGR2RGB)
        self.content = ExampleContent(self, self.inputFile,self.targetFile)
        self.setCentralWidget(self.content)
        
        try:    
            self.fP = open((self.targetFile[:-3] + 'txt'), 'r')
      
            for i in range(0,self.pointCount):
                
                str_point = self.fP.readline()
                self.targetEdges.append(list(map(lambda x: int(x.strip()), str_point.split('\t'))))
                self.targetPoints[i,0] = str_point.split('\t')[0]
                self.targetPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()
        except:
            self.fP = open((self.targetFile[:-3] + 'txt'), 'w')
            self.getImageCoordinates(self.targetFile)
            self.fP.close()
            self.fP = open((self.targetFile[:-3] + 'txt'), 'r')
      
            for i in range(0,self.pointCount):
                
                str_point = self.fP.readline()
                
                self.targetEdges.append(list(map(lambda x: int(x.strip()), str_point.split('\t'))))
                self.targetPoints[i,0] = str_point.split('\t')[0]
                self.targetPoints[i,1] = str_point.split('\t')[1]
                
            self.fP.close()
        
     
    
    def createMorph(self):
        self.inputImage = self.inputImageTemp
        self.targetImage = self.targetImageTemp
        self.morphedImage = self.inputImage.copy()
        self.morphedImage  = cv2.cvtColor(self.morphedImage,cv2.COLOR_BGR2RGB)        
        self.inputImage  = cv2.cvtColor(self.inputImage,cv2.COLOR_BGR2RGB)   
        h,w,c = self.inputImage.shape
        
        for i in range(0,self.triCount):
            
            p1_x = self.inputTriangleMorph[i,0,0]
            p1_y = self.inputTriangleMorph[i,0,1]
            p2_x = self.inputTriangleMorph[i,2,0]
            p2_y = self.inputTriangleMorph[i,2,1]
            p3_x = self.inputTriangleMorph[i,4,0]
            p3_y = self.inputTriangleMorph[i,4,1]
            
            q1Index = self.inputEdges.index([(p1_x),(p1_y)])
            q2Index = self.inputEdges.index([(p2_x),(p2_y)])
            q3Index = self.inputEdges.index([(p3_x),(p3_y)])
                
            q1_x = self.targetEdges[q1Index][0]
            q1_y = self.targetEdges[q1Index][1]
            q2_x = self.targetEdges[q2Index][0]
            q2_y = self.targetEdges[q2Index][1]
            q3_x = self.targetEdges[q3Index][0]
            q3_y = self.targetEdges[q3Index][1]
            
            tri1= np.float32([[[p1_x,p1_y],[p2_x,p2_y],[p3_x,p3_y]]])
            tri2= np.float32([[[q1_x,q1_y],[q2_x,q2_y],[q3_x,q3_y]]])
            
            r1 = cv2.boundingRect(tri1)
            r2 = cv2.boundingRect(tri2)
            
            temp0 = r1[0]
            temp1 = r1[1]
            temp2 = r1[2]
            temp3 = r1[3]
            temp00 = r2[0] 
            temp01 = r2[1] 
            temp02 = r2[2] 
            temp03 = r2[3] 
            
            
            r1 = (temp1,temp0,temp3,temp2)
            r2 = (temp01,temp00,temp03,temp02)
            
            
            
            
            
            tri1Cropped = []
            tri2Cropped = []
            
            
            for i in range(0, 3):
              tri1Cropped.append(((tri1[0][i][0] - r1[1]),(tri1[0][i][1] - r1[0])))
              tri2Cropped.append(((tri2[0][i][0] - r2[1]),(tri2[0][i][1] - r2[0])))
            
            
            
            
            img1Cropped = self.inputImage[r1[0]:r1[0] + r1[2], r1[1]:r1[1] + r1[3]]
            input_coord = np.asarray([[tri1Cropped[0][1],tri1Cropped[0][0],1,0,0,0],[0,0,0,tri1Cropped[0][1],tri1Cropped[0][0],1],[tri1Cropped[1][1],tri1Cropped[1][0],1,0,0,0],[0,0,0,tri1Cropped[1][1],tri1Cropped[1][0],1],[tri1Cropped[2][1],tri1Cropped[2][0],1,0,0,0],[0,0,0,tri1Cropped[2][1],tri1Cropped[2][0],1]])
            
            target_coord = np.asarray([tri2Cropped[0][1],tri2Cropped[0][0],tri2Cropped[1][1],tri2Cropped[1][0],tri2Cropped[2][1],tri2Cropped[2][0]])
            affMat = np.matmul(np.linalg.inv(input_coord), target_coord)
           
            
            src = []
            xc,hc,cc = img1Cropped.shape
            for ii in range(xc):
                for jj in range(hc):
                   src.append([ii,jj,1,0,0,0]) 
                   src.append([0,0,0,ii,jj,1]) 
            sonuc = np.matmul(src,affMat)
            dogruIndex = 0
            dogruIndex2 = 0
            for i in range(int(len(sonuc)/2)):
                dogruIndex = max(dogruIndex, sonuc[i*2])
                dogruIndex2 = max(dogruIndex2, sonuc[i*2 + 1])
                
                
            croppedIm = np.ndarray(( r2[2] , r2[3],3 ),dtype='uint8')
            for i in range(int(len(sonuc)/2)):
                if(sonuc[i*2]) >= 0 and sonuc[i*2 +1 ] >= 0 and sonuc[i*2] < r2[2] and  sonuc[i*2 +1] < r2[3]:
                    croppedIm[int(sonuc[i*2]),int(sonuc[i*2 +1])] =   img1Cropped[src[i*2][0] , src[i*2][1]]
            
            
            warpMat = cv2.getAffineTransform( np.float32(tri1Cropped), np.float32(tri2Cropped) )
            
            
            img2Cropped = cv2.warpAffine( img1Cropped, warpMat, (r2[3], r2[2]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )
            
            
            
            
            print(img2Cropped[:100])
            print(croppedIm[:100])
            
            # Get mask by filling triangle
            mask = np.zeros((r2[2], r2[3], 3), dtype = np.float32)
            cv2.fillConvexPoly(mask, np.int32(tri2Cropped), (1.0, 1.0, 1.0), 16, 0);
            

            # Apply mask to cropped region
            img2Cropped = img2Cropped * mask
            croppedIm = croppedIm * mask
            
            self.morphedImage[r2[0]:r2[0]+r2[2], r2[1]:r2[1]+r2[3]] = self.morphedImage[r2[0]:r2[0]+r2[2], r2[1]:r2[1]+r2[3]] * ( (1.0, 1.0, 1.0) - mask )
     
            self.morphedImage[r2[0]:r2[0]+r2[2], r2[1]:r2[1]+r2[3]] = self.morphedImage[r2[0]:r2[0]+r2[2], r2[1]:r2[1]+r2[3]] + croppedIm
            cv2.imshow('a', self.morphedImage)
            cv2.waitKey(0)
            cv2.imwrite('sonuc.jpg', self.morphedImage)

        
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
            #print(ifacet)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
     
            cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0);
            ifacets = np.array([ifacet])
            cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)
            cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), cv2.FILLED, cv2.LINE_AA, 0)
     
    
    def draw_delaunay(self,img, subdiv, delaunay_color):
     
        triangleList = subdiv.getTriangleList();
        
        #print(triangleList)
        size = img.shape
        r = (0, 0, size[1], size[0])
        point_list = []
        for t in triangleList :
            
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])
             
            
            if self.rect_contains(r, pt1) and self.rect_contains(r, pt2) and self.rect_contains(r, pt3) :
                
                individual_triangle =  [[int(t[0]),int(t[1]),1,0,0,0],[0,0,0,int(t[0]),int(t[1]),1],[int(t[2]),int(t[3]),1,0,0,0],[0,0,0,int(t[2]),int(t[3]),1],[int(t[4]),int(t[5]),1,0,0,0],[0,0,0,int(t[4]),int(t[5]),1]]
                point_list.append(individual_triangle)
                cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
                cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)

        return point_list           
    def createTriangulation(self):
        if(self.targetFile == '' or self.inputFile == ''):
            return
        
        self.inputImage = cv2.cvtColor(self.inputImage,cv2.COLOR_BGR2RGB)
        self.targetImage = cv2.cvtColor(self.targetImage,cv2.COLOR_BGR2RGB)
        
        self.inputPoints = self.sortPoints(self.inputPoints)
        self.targetPoints = self.sortPoints(self.targetPoints)
        
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
            
            self.draw_delaunay(img_copy,subdiv,(255,255,255))
            
            cv2.imshow('deneme', img_copy)
            cv2.waitKey(100)
        
        for p in points_target:
            subdiv_target.insert(p)
            img_copy_target = img_org_target.copy()
            
            self.draw_delaunay(img_copy_target,subdiv_target,(255,255,255))
            
            cv2.imshow('deneme_target', img_copy_target)
            cv2.waitKey(100)
        
        self.inputTrianglePoints = self.draw_delaunay(self.inputImage,subdiv,(255,255,255))
        self.targetTrianglePoints = self.draw_delaunay(self.targetImage,subdiv_target,(255,255,255))
                
        
        
        
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
        
   
        self.triCount = 0
        
        for p in self.targetTrianglePoints:
            self.triCount+=1
        
        self.inputTriangleMorph = np.asarray(self.inputTrianglePoints[:][:][:])
        self.targetTriangleMorph = np.asarray(self.targetTrianglePoints[:][:][:]) 

        self.content = ExampleContent(self, 'delauneyInput.jpg','delauneyTarget.jpg','delauneyInput.jpg')
        self.setCentralWidget(self.content)
        
        aff_parameters =  self.calculateAffine(self.triCount)
        self.affine_parameters = np.asarray(aff_parameters[:][:][:])
        
                
    def calculateAffine(self,count):
        res = []
        for i in range(count):
            target_coord = np.asarray( [ self.targetTrianglePoints[i][0][0],self.targetTrianglePoints[i][0][1],self.targetTrianglePoints[i][2][0],self.targetTrianglePoints[i][2][1],self.targetTrianglePoints[i][4][0], self.targetTrianglePoints[i][4][1]]).reshape(-1,1)
            
            
            p1_x = self.inputTriangleMorph[i,0,0]
            p1_y = self.inputTriangleMorph[i,0,1]
            p2_x = self.inputTriangleMorph[i,2,0]
            p2_y = self.inputTriangleMorph[i,2,1]
            p3_x = self.inputTriangleMorph[i,4,0]
            p3_y = self.inputTriangleMorph[i,4,1]
            input_coord = np.asarray([[p1_x,p1_y,1,0,0,0],[0,0,0,p1_x,p1_y,1],[p2_x,p2_y,1,0,0,0],[0,0,0,p2_x,p2_y,1],[p3_x,p3_y,1,0,0,0],[0,0,0,p3_x,p3_y,1]])
            q1Index = self.inputEdges.index([(p1_x),(p1_y)])
            q2Index = self.inputEdges.index([(p2_x),(p2_y)])
            q3Index = self.inputEdges.index([(p3_x),(p3_y)])
            
            q1_x = self.targetEdges[q1Index][0]
            q1_y = self.targetEdges[q1Index][1]
            q2_x = self.targetEdges[q2Index][0]
            q2_y = self.targetEdges[q2Index][1]
            q3_x = self.targetEdges[q3Index][0]
            q3_y = self.targetEdges[q3Index][1]
            
            target_coord = np.asarray([q1_x,q1_y,q2_x,q2_y,q3_x,q3_y])
            
            res.append(np.matmul(np.linalg.inv(input_coord),target_coord))
        return res
    
if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    cv2.destroyAllWindows()
    sys.exit(App.exec())
    