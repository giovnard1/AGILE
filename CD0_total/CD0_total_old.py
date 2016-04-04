import math
import os
import tixiwrapper
import tiglwrapper
import xml.etree.ElementTree as ET
from scipy import interpolate
import numpy as np
import shutil
from aerocalc import std_atm
import matplotlib.pyplot as plt

#AGGIORNATO AL 16/03/2016

###################################Initialization##############################
cwd=os.getcwd()
inputfile =cwd+'/ToolInput/toolInput.xml'
outfile = cwd+'/ToolOutput/toolOutput.xml'

## Thanks to tixi and tigl handle it's possible to open and modify files and extract useful parameters
tixi_s= tixiwrapper.Tixi()
tigl_s= tiglwrapper.Tigl()
tixi_s.open(inputfile)

## Check Model
nModel=tixi_s.getNamedChildrenCount('/cpacs/vehicles/aircraft', 'model')
aircraftModelUID=[0]*nModel
for i in range(0,nModel):
    aircraftModelUID[i]=tixi_s.getTextAttribute('/cpacs/vehicles/aircraft/model[%d+1]' %i,'uID') 

modelUID=tixi_s.getTextElement('/cpacs/toolspecific/UNINA_modules/aircraftModelUID')

## Check UID model
for i in range(0,len(aircraftModelUID)):
    if modelUID==aircraftModelUID[i]:
        print "UID model found"
        aircraftPos=i
        break
    else : 
        print "UID model don't found"
   
# to enter in the aircraft model and extract the parameters
tigl_s.open(tixi_s,aircraftModelUID[aircraftPos])

aircraftConfiguration=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/aircraftConfiguration')
if aircraftConfiguration==0:
    print "Chosen a Traditional Configuration (W-HT-VT)"
if aircraftConfiguration==1:
    print "Chosen a Advanced Configuration"
    
#####################################WING######################################
nWing=tigl_s.getWingCount()
# the length of the following array 
# (aircraft data) is equal to the number of the wing 

## Initialization
i=0
wingUid  =[0]*nWing
wIndex   =[0]*nWing
wSegCount=[0]*nWing
wSurfArea=[0]*nWing
wWettedArea=[0]*nWing
wRefArea =[0]*nWing
wSecCount=[0]*nWing
wSymmetry=[0]*nWing 
wSpan    =[0]*nWing
wMAC     =[[0]]*nWing
wSegUid  =[[0]]*nWing
wSegIndex=[[0]]*nWing

wIndexPosition=[[0]]*nWing
wingElemIndex_inner=[[0]]*nWing
wingElemIndex_outer=[[0]]*nWing
wingSectionIndex_inner=[[0]]*nWing
wingSectionIndex_outer=[[0]]*nWing
wingElemIndex=[[0]]*nWing
wingSectionIndex=[[0]]*nWing
wProfileName=[[0]]*nWing

## Load the value
for i in range(0,nWing):
    wingUid[i]  =tigl_s.wingGetUID(i+1)#since python array begins from 0 position
    wIndex[i]   =tigl_s.wingGetIndex(wingUid[i])
    wSegCount[i]=tigl_s.wingGetSegmentCount(wIndex[i])
    wSurfArea[i]=tigl_s.wingGetSurfaceArea(wIndex[i])#wetted surface of the isolate wing
    wRefArea[i] =tigl_s.wingGetReferenceArea(wIndex[i],wSymmetry[i])#half surface
    wSecCount[i]=tigl_s.wingGetSectionCount(wIndex[i])
    wSymmetry[i]=tigl_s.wingGetSymmetry(wIndex[i])#number of symmetry-axes
    wSpan[i]    =tigl_s.wingGetSpan(wingUid[i])
    wMAC[i]     =tigl_s.wingGetMAC(wingUid[i])    
    i=i+1

print "nWing = {}".format(nWing)
print "wingUid = {}".format(wingUid)
print "wIndex = {}".format(wIndex)
print "wSegCount = {}".format(wSegCount)
print "wSurfArea = {}".format(wSurfArea)
print "wRefArea = {}".format(wRefArea)
print "wSectionCount = {}".format(wSecCount)
print "wSymmetry = {}".format(wSymmetry)
print "wSpan = {}".format(wSpan)

#print "nWing = ({}), wingUid = ({})".format(nWing,wingUid)

for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        wSegUid[i]  =[[0]]*wSegCount[i]#in this way wSegUid will be [[0,0,0],[0],[0]]
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        wSegUid[i][j]=tigl_s.wingGetSegmentUID(i+1,j+1)
print "wSegUid = {}".format(wSegUid)
  
for i in range(0,nWing):
    for j in range(0,wSegCount[i]):
        wSegIndex[i]  =[[0]]*wSegCount[i]
        wIndexPosition[i]=[[0]]*wSegCount[i]        
for i in range(0,nWing):
    for j in range(0,wSegCount[i]):
        (wSegIndex[i][j],wIndexPosition[i][j])=tigl_s.wingGetSegmentIndex(wSegUid[i][j])
print "wSegIndex = {}".format(wSegIndex)

#wingSectionIndex=[[1,2,3,4],[1,2],[1,2]] #si puo ricavare dal wSecCount che mi da quante sono le sezioni per ogni wing, resta da costruire il vettore
for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :
        wingSectionIndex[i]=[[0]]*wSecCount[i]
for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :  
        wingSectionIndex[i][j]=j+1   
print "wingSectionIndex = {}".format(wingSectionIndex) 

#wingElemIndex=[[1,1,1,1],[1,1],[1,1]]    #non esiste un comando per il conteggio degli elementi, dovrei fare il conteggio degli elementi per ogni sezione
for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :
        wingElemIndex[i]=[[0]]*wSecCount[i]
for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :  
        wingElemIndex[i][j]=1       #non contemplati piu' elementi in una sola section
print "wingElemIndex = {}".format(wingElemIndex)

for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :
        wProfileName[i] =[[0]]*wSecCount[i]#in this way wProfileName will be [[0,0,0,0],[0,0],[0,0]]
for i in range(0,nWing):
    for j in range(0,wSecCount[i]):
        wProfileName[i][j]=tigl_s.wingGetProfileName(wIndex[i], wingSectionIndex[i][j], wingElemIndex[i][j])
print "Profile_name = {}".format(wProfileName) #profili utilizzati

#wing segment global coordinates calculation,(segment means the single part that of a wing, 
#NB:for the main wing there are 3 segments-->from x-axes to fuselage connection-->from this one to the kink-->from this one to the tip
wChordPoint=[[0]*4]*nWing#every segment has 4 extremity 
for i in range(0,nWing):
    for j in range(0,wSegCount[i]):
        wChordPoint[i]=[[0]*4]*wSegCount[i]
 
#range of local coordinates inside CPACS file
eta=[0,1]
xsi=[0,1]

nSegTot=0
for i in range(0,len(wSegCount)):
    nSegTot=nSegTot+wSegCount[i]#number of all wing (main,HT,VT) segment 

#if you consider the first segment from x-axes to fuselage connections it is like a rectangle:
#A-----eta------B
#|              |
#|              |
#csi           csi   
#|              |
#|              |
#C--------------D
#eta=0 and xsi=0 --> punto A
#eta=1 and xsi=0 --> punto B
#eta=0 and xsi=1 --> punto C
#eta=1 and xsi=1 --> punto D
#finding steps-->A-->B-->C-->D

###################################Alternative: section and element index
# for i in range(0,nWing) :
#     for j in range(0,wSegCount[i]) :
#         wingSectionIndex_inner[i] =[[0]]*wSegCount[i]
#         wingElemIndex_inner[i] =[[0]]*wSegCount[i]
#      
# for i in range(0,nWing):
#     for j in range(0,wSegCount[i]) :
#         (wingSectionIndex_inner[i][j],wingElemIndex_inner[i][j])=tigl_s.wingGetInnerSectionAndElementIndex(wIndex[i],wSegIndex[i][j])        
# 
# for i in range(0,nWing) :
#     for j in range(0,wSegCount[i]) :
#         wingSectionIndex_outer[i] =[[0]]*wSegCount[i]
#         wingElemIndex_outer[i] =[[0]]*wSegCount[i]
#      
# for i in range(0,nWing):
#     for j in range(0,wSegCount[i]) :
#         (wingSectionIndex_outer[i][j],wingElemIndex_outer[i][j])=tigl_s.wingGetOuterSectionAndElementIndex(wIndex[i],wSegIndex[i][j])        
# 
# print wingElemIndex_inner
# print wingElemIndex_outer
# print wingSectionIndex_inner
# print wingSectionIndex_outer
##per ogni sezone si hanno n elementi, di conseguenza la numerazione degli elementi parte da 1 per ogni sezione


######################################FUSELAGE#################################
nFus=tigl_s.getFuselageCount()

## Inizialization
fusSegCount=[0]*nFus
fusUid     =[0]*nFus
fusIndex   =[0]*nFus
fusSegCount=[0]*nFus
fusSecCount=[0]*nFus
fusSegUid  =[[0]]*nFus
fusSegIndex=[[0]]*nFus
fusSurfArea=[0]*nFus

## Load value
for i in range(0,nFus):
    fusSegCount[i]=tigl_s.fuselageGetSegmentCount(i+1)
    fusUid[i]     =tigl_s.fuselageGetUID(i+1)#since python array begins from 0 position
    fusIndex[i]   =tigl_s.fuselageGetIndex(fusUid[i])
    fusSecCount[i]=tigl_s.fuselageGetSectionCount(fusIndex[i])
    fusSurfArea[i]=tigl_s.fuselageGetSurfaceArea(fusIndex[i])
    fusSecUid=[[0]]*fusSecCount[i]
    for j in range(0,fusSecCount[i]):
        fusSecUid[j]=tigl_s.fuselageGetSectionUID(fusIndex[i], j+1)
    fusSegUid=[[0]]*fusSegCount[i]  
    for k in range(0,fusSegCount[i]):
            fusSegUid[k]=tigl_s.fuselageGetSegmentUID(fusIndex[i], k+1)
   
fusSegTot=np.sum(fusSegCount)#total number of segment depends by nFus
fusPoint=[[0]]*nFus

for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fusPoint=[[0]*(fusSegCount[i]+1)]
  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fusPoint[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0)
        fusPoint[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0)


#####################################CHECH UID###############################

## Check UID mainW
mainWingUID=tixi_s.getTextElement('/cpacs/toolspecific/UNINA_modules/wings/MainWing/mainWingUID')
for i in range(0,len(wingUid)):
    if mainWingUID==wingUid[i]:
        print "UID mainW found"
        break
    else : 
        print "UID mainW don't found"
 
## Check UID Fuselage
FuselageUID=tixi_s.getTextElement('/cpacs/toolspecific/UNINA_modules/fuselages/FuselageUID')
for i in range(0,len(fusUid)):
    if FuselageUID==fusUid[i]:
        FusPos=i
        print "UID Fus found"
        break
    else : 
        print "UID Fus don't found"

## Check HT UID
HorizontalTailUID=tixi_s.getTextElement('/cpacs/toolspecific/UNINA_modules/wings/HorizTail/HorizTailUID')
for i in range(0,len(wingUid)):
    if HorizontalTailUID==wingUid[i]:
        print "UID HT found"
        break
    else : 
        print "UID HT don't found"
          
## Check UID VT
VerticalTailUID=tixi_s.getTextElement('/cpacs/toolspecific/UNINA_modules/wings/VerticalTail/VerticalTailUID')
for i in range(0,len(wingUid)):
    if VerticalTailUID==wingUid[i]:
        print "UID VT found"
        break
    else : 
        print "UID VT don't found"

   
######################################Modules################################

 
############################ WING
    
## Main Wing surface
for i in range(0,len(wingUid)):
    if mainWingUID==wingUid[i]:
        mainWPos=i 
        
## Reference surface        
Sw=2*wRefArea[mainWPos]

# ## wetted wing surface
# Sw_wet=2*wWettedArea[mainWPos]
# print "Sw_wet = {}".format(Sw_wet)

## Wing span
bw=wSpan[mainWPos]  

## Wing AspectRatio
ARw=bw**2/(Sw)

## MAC
MAC_W=wMAC[mainWPos][0]

print "Sw = {}".format(Sw)

######################### FUSELAGE

## Number of fuselages 
n_fus = tigl_s.getFuselageCount()

## Fuselage Length
#fuselage x-coordinates sections
x_ell=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        x_ell=[[0]*(fusSegCount[i]+1)]  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        x_ell[i][j]=fusPoint[i][j][0]

#fuselage length
Lf=x_ell[FusPos][-1]
print "Lf = {}".format(Lf)

## Fuselage diameter Z
Z=-100#in this way is possible to consider all fuselage point in a new arbitrary REFERENCE axes

#FP1
fP_1_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the upper or lower points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,1)
        fP_1_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0)
fP_1=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_1[i][j]=fP_1_array[i][j][2]
  
#FP2
fP_2_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the upper or lower points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.5)
        fP_2_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0)
fP_2=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_2[i][j]=fP_2_array[i][j][2]
  
#vectors inizialization about lower and upper fuselage points 
fP_up=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_up=[[0]*(fusSegCount[i]+1)]
fP_down=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_down=[[0]*(fusSegCount[i]+1)]

#thanks to the following check is possible to separate the upper and lower points  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if fP_1[i][j]-Z>fP_2[i][j]-Z:
            fP_up[i][j]=fP_1[i][j]-Z
            fP_down[i][j]=fP_2[i][j]-Z
        else :
            fP_up[i][j]=fP_2[i][j]-Z
            fP_down[i][j]=fP_1[i][j]-Z
   
#FP3 
fP_3_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the upper or lower points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.25)
        fP_3_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0.25)
fP_3=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3=[[0]*(fusSegCount[i]+1)]
  
#we are ineresting to z-coordinate
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_3[i][j]=fP_3_array[i][j][2]

#FP4
fP_4_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the upper or lower points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.75)
        fP_4_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0.75)
fP_4=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4=[[0]*(fusSegCount[i]+1)]

#we are ineresting to z-coordinate
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_4[i][j]=fP_4_array[i][j][2]
  
#vectors inizialization about lower and upper fuselage points 
fP_up_2=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_up_2=[[0]*(fusSegCount[i]+1)]

fP_down_2=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_down_2=[[0]*(fusSegCount[i]+1)]

#thanks to the following check is possible to separate the upper and lower points  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if fP_3[i][j]-Z>fP_4[i][j]-Z:
            fP_up_2[i][j]=fP_3[i][j]-Z
            fP_down_2[i][j]=fP_4[i][j]-Z
        else :
            fP_up_2[i][j]=fP_4[i][j]-Z
            fP_down_2[i][j]=fP_4[i][j]-Z

#diff and diff_2 -->vectors of the difference between fP_up and fP_down
#initialization
diff=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff[i][j]=math.fabs(fP_up[i][j]-fP_down[i][j])

diff_2=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff_2=[[0]*(fusSegCount[i]+1)]  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff_2[i][j]=math.fabs(fP_up_2[i][j]-fP_down_2[i][j])
  
section_diameter=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        section_diameter=[[0]*(fusSegCount[i]+1)]  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if math.fabs(fP_up_2[i][j])-math.fabs(fP_down_2[i][j])<10**(-5):
            section_diameter[i][j]=math.fabs(fP_up[i][j]-fP_down[i][j])
        else :
            section_diameter[i][j]=math.fabs(fP_up_2[i][j]-fP_down_2[i][j]) 
# print "diametri_z"
# print section_diameter 
# d_fus_max_z=np.max(section_diameter[FusPos])
# print "d_fus_max_z = {}".format(d_fus_max_z)
d_fus_max_z_array=[0]*nFus
for i in range(0,nFus):
    d_fus_max_z_array[i]=np.max(section_diameter[i])
print "d_fus_max_z = {}".format(d_fus_max_z_array)


## Fuselage diameter_Y
Y=-100#in this way is possible to consider all fuselage point in a new arbitrary REFERENCE axes

#FP1
fP_1_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the right or left points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,1)
        fP_1_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0)
fP_1_y=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_1_y=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_1_y[i][j]=fP_1_array[i][j][1]
  
#FP2
fP_2_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the right or left points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.5)
        fP_2_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0)
fP_2_y=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_2_y=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_2_y[i][j]=fP_2_array[i][j][1]
  
#vectors inizialization about left and right fuselage points 
fP_right=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_right=[[0]*(fusSegCount[i]+1)]
fP_left=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_left=[[0]*(fusSegCount[i]+1)]

#thanks to the following check is possible to separate the right and left points  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if fP_1_y[i][j]-Y>fP_2_y[i][j]-Y:
            fP_right[i][j]=fP_1_y[i][j]-Y
            fP_left[i][j]=fP_2_y[i][j]-Y
        else :
            fP_right[i][j]=fP_2_y[i][j]-Y
            fP_left[i][j]=fP_1_y[i][j]-Y
   
#FP3 
fP_3_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the right or left points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.25)
        fP_3_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0.25)
fP_3_y=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_3_y=[[0]*(fusSegCount[i]+1)]
  
#we are ineresting to y-coordinate
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_3_y[i][j]=fP_3_array[i][j][1]

#FP4
fP_4_array=[[0]]*nFus#i need just 1 point for each segment which corresponds to eta=0,xsi=1
#to extract the right or left points (is a CPACS characteristic)
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4_array=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4_array[i][j]=tigl_s.fuselageGetPoint(fusIndex[i],j+1,0,0.75)
        fP_4_array[i][-1]=tigl_s.fuselageGetPoint(fusIndex[i],fusSegCount[i],1,0.75)
fP_4_y=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_4_y=[[0]*(fusSegCount[i]+1)]

#we are ineresting to y-coordinate
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        fP_4_y[i][j]=fP_4_array[i][j][1]
  
#vectors inizialization about left and right fuselage points 
fP_right_2=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_right_2=[[0]*(fusSegCount[i]+1)]

fP_left_2=[[0]]*nFus  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        fP_left_2=[[0]*(fusSegCount[i]+1)]

#thanks to the following check is possible to separate the right and left points  
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if fP_3_y[i][j]-Y>fP_4_y[i][j]-Y:
            fP_right_2[i][j]=fP_3_y[i][j]-Y
            fP_left_2[i][j]=fP_4_y[i][j]-Y
        else :
            fP_right_2[i][j]=fP_4_y[i][j]-Y
            fP_left_2[i][j]=fP_4_y[i][j]-Y

#diff and diff_2 -->vectors of the difference between fP_up and fP_left
#iniYialization
diff=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff[i][j]=math.fabs(fP_right[i][j]-fP_left[i][j])
diff_2=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff_2=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        diff_2[i][j]=math.fabs(fP_right_2[i][j]-fP_left_2[i][j])
  
section_diameter_y=[[0]]*nFus
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]):
        section_diameter_y=[[0]*(fusSegCount[i]+1)]
for i in range(0,nFus):
    for j in range(0,fusSegCount[i]+1):
        if math.fabs(fP_right_2[i][j])-math.fabs(fP_left_2[i][j])<10**(-5):
            section_diameter_y[i][j]=math.fabs(fP_right[i][j]-fP_left[i][j])
        else:
            section_diameter_y[i][j]=math.fabs(fP_right_2[i][j]-fP_left_2[i][j])
# print "diametri_y"
# print section_diameter_y 
# d_fus_max_y=np.max(section_diameter_y[FusPos])
# print "d_fus_max_y = {}".format(d_fus_max_y)
d_fus_max_y_array=[0]*nFus
for i in range(0,nFus):
    d_fus_max_y_array[i]=np.max(section_diameter_y[i])
print "d_fus_max_y = {}".format(d_fus_max_y_array)

## Maximum diameter of equivalent circular cross section
maximum_fuselage_section_array=[0]*nFus
for i in range(0,nFus):
    maximum_fuselage_section_array[i]=math.pi*(d_fus_max_z_array[i]/2)*(d_fus_max_y_array[i]/2)
print "Maximum fuselage cross section= {}".format(maximum_fuselage_section_array)

d_fus_max_equiv_array=[0]*nFus
for i in range(0,nFus):
    d_fus_max_equiv_array[i]=2*math.sqrt(maximum_fuselage_section_array[i]/math.pi)
print "Maximum diameter of equivalent circular cross section= {}".format(d_fus_max_equiv_array)

## Fineness Ratio
FR=[0]*nFus
for i in range(0,nFus):
    FR[i]=x_ell[i][-1]/d_fus_max_equiv_array[i]
print "Fineness ratio = {}".format(FR)

## Tailcone and nose
if np.max(diff_2)<10**(-4):
    epsilon=10**(-4)#reference axes-->fuselage lower side ->z coordinates cabin =0 but the beginning cone section z=4*10^-5, we need epsilon
    j=-1 #scorro dalla fine
    while j>(-len(x_ell[FusPos])):
        if fP_down[FusPos][j]-fP_down[FusPos][j-1]<epsilon:
            in_cone=fusSecCount[FusPos]+j+1
            print "Tailcone starts at section number = {}".format(in_cone)#ok
            break
        j=j-1
    for j in range(1,len(x_ell[FusPos])):
        if fP_down[FusPos][j+1]-fP_down[FusPos][j]<epsilon:
            print "Nose finishes at section number = {}".format(j)
            in_nose=j
            break
if np.max(diff)<10**(-4):
    epsilon=10**(-4)#reference axes-->fuselage lower side ->z coordinates cabin =0 but the beginning cone section z=4*10^-5, we need epsilon
    j=-1
    while j>(-len(x_ell[FusPos])):
        if fP_down_2[FusPos][j]-fP_down_2[FusPos][j-1]<epsilon:
            in_cone=fusSecCount[FusPos]+j+1
            print "Tailcone starts at section number = {}".format(in_cone)
            break
        j=j-1
    for j in range(1,len(x_ell[FusPos])):
        if fP_down_2[FusPos][j+1]-fP_down_2[FusPos][j]<epsilon:
            print "Nose finishes at section number = {}".format(j)
            in_nose=j
            break

#tail cone length
Lcone=Lf-x_ell[FusPos][in_cone]
print "Tailcone length = {}".format(Lcone)

#nose length
Lnose=x_ell[FusPos][in_nose]
print "Nose length = {}".format(Lnose)

###################################### VERTICAL TAIL

for i in range(0,len(wingUid)):
    if VerticalTailUID==wingUid[i]:
        VTPos=i
for i in range(0,len(wingUid)):
    for j in range(0,len(wSegUid)):
        if VerticalTailUID==wingUid[i]:
            VT_seg_pos=j

Sv=wRefArea[VTPos]
print "Sv = {}".format(Sv)

# Sv_wet=wSurfArea[VTPos]
# print "Sv_wet = {}".format(Sv_wet)

bv=wSpan[VTPos]

ARv=(bv**2)/Sv

MAC_VT=wMAC[VTPos][0]


#################################### HORIZONTAL TAIL

for i in range(0,len(wingUid)):
    if HorizontalTailUID==wingUid[i]:
        HTPos=i

for i in range(0,len(wingUid)):
    for j in range(0,len(wSegUid)):
        if HorizontalTailUID==wingUid[i]:
            HT_seg_pos=j

Sh=2*wRefArea[HTPos]
print "Sh = {}".format(Sh)

# Sh_wet=2*wSurfArea[HTPos]
# print "Sh_wet = {}".format(Sh_wet)

bh=wSpan[HTPos]

ARh=(bh**2)/Sv

MAC_HT=wMAC[HTPos][0]


############################### Chords of the surfaces
#load chord
for i in range(0,nWing):
    for j in range(0,wSegCount[i]): 
        y=0
        for k in eta:
            for h in xsi:
                wChordPoint[i][j][y]=tigl_s.wingGetChordPoint(wIndex[i], j+1, eta[h], xsi[k])
                #main wing
                if (i==mainWPos and j==wSegCount[mainWPos]-wSegCount[mainWPos] and y==0):
                    A_root_wing=wChordPoint[i][j][y]
                if (i==mainWPos and j==wSegCount[mainWPos]-wSegCount[mainWPos] and y==2):
                    C_root_wing=wChordPoint[i][j][y]
                if (i==mainWPos and j==wSegCount[mainWPos]-1 and y==1):
                    B_tip_wing=wChordPoint[i][j][y]
                if (i==mainWPos and j==wSegCount[mainWPos]-1 and y==3):
                    D_tip_wing=wChordPoint[i][j][y] 
                #vertical tail
                if (i==VTPos and j==wSegCount[VTPos]-wSegCount[VTPos] and y==0):
                    A_root_VT=wChordPoint[i][j][y] 
                if (i==VTPos and j==wSegCount[VTPos]-wSegCount[VTPos] and y==2):
                    C_root_VT=wChordPoint[i][j][y] 
                if (i==VTPos and j==wSegCount[VTPos]-1 and y==1):
                    B_tip_VT=wChordPoint[i][j][y]
                if (i==VTPos and j==wSegCount[VTPos]-1 and y==3):
                    D_tip_VT=wChordPoint[i][j][y]  
                #horizontal tail
                if (i==HTPos and j==wSegCount[HTPos]-wSegCount[HTPos] and y==0):
                    A_root_HT=wChordPoint[i][j][y]
                if (i==HTPos and j==wSegCount[HTPos]-wSegCount[HTPos] and y==2):
                    C_root_HT=wChordPoint[i][j][y] 
                if (i==HTPos and j==wSegCount[HTPos]-1 and y==1):
                    B_tip_HT=wChordPoint[i][j][y]
                if (i==HTPos and j==wSegCount[HTPos]-1 and y==3):
                    D_tip_HT=wChordPoint[i][j][y]  
                y=y+1

#Wing chord (root and tip)
x_A_root_w=A_root_wing[0]#(first segment point A)0 is the first position of (x,y,z)-->x
x_C_root_w=C_root_wing[0]#first segment, point C
x_B_tip_w =B_tip_wing[0]#last segment, point B
x_D_tip_w=D_tip_wing[0]#last segment, point C
Croot_w=math.fabs(x_C_root_w-x_A_root_w)#is right
Ctip_w=math.fabs(x_D_tip_w-x_B_tip_w)#is right

#horizontal tail chord (root and tip)
x_A_root_HT=A_root_HT[0]#(first segment point A)0 is the first position of (x,y,z)-->x
x_C_root_HT=C_root_HT[0]#first segment, point C
x_B_tip_HT =B_tip_HT[0]#last segment, point B
x_D_tip_HT=D_tip_HT[0]#last segment, point C
Croot_HT=math.fabs(x_C_root_HT-x_A_root_HT)#is right
Ctip_HT=math.fabs(x_D_tip_HT-x_B_tip_HT)#is right

#vertical tail chord (root and tip)
x_A_root_VT=A_root_VT[0]#(first segment point A)0 is the first position of (x,y,z)-->x
x_C_root_VT=C_root_VT[0]#first segment, point C
x_B_tip_VT =B_tip_VT[0]#last segment, point B
x_D_tip_VT=D_tip_VT[0]#last segment, point C
Croot_VT=math.fabs(x_C_root_VT-x_A_root_VT)#is right
Ctip_VT=math.fabs(x_D_tip_VT-x_B_tip_VT)#is right


########################################### Thickness

max_thickness_array=[[0]]*nWing
for i in range(0,nWing) :
    for j in range(0,wSecCount[i]) :
        max_thickness_array[i] =[[0]]*wSecCount[i]#in this way wProfileName will be [[0,0,0,0],[0,0],[0,0]]
 
Number_airfoils=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/wings/Airfoils/Airfoil_number')
profilo=[0]*Number_airfoils
thickness=[0]*Number_airfoils

tree = ET.parse(inputfile)
root = tree.getroot()

i=0
for airfoil in root.findall('toolspecific/UNINA_modules/wings/Airfoils/airfoil',namespaces=None):
    profilo[i]=airfoil.find('airfoilName').text
    thickness[i]=airfoil.find('max_thickness').text
    thickness[i]=float(thickness[i])
    i=i+1
print 'Chosen airfoils = {}'.format(profilo)
print 'Maximum thickness of the chosen airfoils = {}'.format(thickness)

for i in range(0,nWing):
    for j in range(0,wSecCount[i]):
        for k in range(0,Number_airfoils):
            if wProfileName[i][j]==profilo[k]:
                max_thickness_array[i][j]=thickness[k] 
print 'Max_thickness_array = {}'.format(max_thickness_array)

#distanza tra due sezioni consecutive
X_outer=[[0]]*nWing
Y_outer=[[0]]*nWing
Z_outer=[[0]]*nWing
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        X_outer[i] =[[0]]*wSegCount[i]
        Y_outer[i] =[[0]]*wSegCount[i]
        Z_outer[i] =[[0]]*wSegCount[i] #sara' leggermente differente       
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) : 
        (X_outer[i][j],Y_outer[i][j],Z_outer[i][j])=tigl_s.wingGetUpperPoint(wIndex[i], wSegIndex[i][j], 1, 0)
 
max_thickness_wing=[0]*nWing 
for i in range(0,nWing) :
    cont=0
    if wSymmetry[i]==2: #immagino che l'unico piano ad avere 2 assi di simmetria sia quello HT
        for j in range(0,wSegCount[i]) : 
            if j==0:
                max_thickness_wing[i]=cont+Y_outer[i][j]*(max_thickness_array[i][j]+max_thickness_array[i][j+1])/2/(wSpan[i]/2)
                cont=max_thickness_wing[i]
            else:
                max_thickness_wing[i]=cont+(Y_outer[i][j]-Y_outer[i][j-1])*(max_thickness_array[i][j]+max_thickness_array[i][j+1])/2/(wSpan[i]/2) #
                cont=max_thickness_wing[i]
    else :
        for j in range(0,wSegCount[i]) : 
            if j==0:
                max_thickness_wing[i]=cont+Z_outer[i][j]*(max_thickness_array[i][j]+max_thickness_array[i][j+1])/2/(Z_outer[i][-1])
                cont=max_thickness_wing[i]
            else:
                max_thickness_wing[i]=cont+(Z_outer[i][j]-Z_outer[i][j-1])*(max_thickness_array[i][j]+max_thickness_array[i][j+1])/2/(Z_outer[i][-1])
                cont=max_thickness_wing[i] 
print 'Max_thickness_wing = {}'.format(max_thickness_wing)        


# #########################################Alternative:Calculate thickness
# #profili definiti dal TE al LE
# #il primo elemento del vettore e' l elemento zero

# #WING
# x_wing_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[2]/pointList/x')
# x_wing_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[2]/pointList/x',x_wing_profile_size)
#  
# z_wing_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[2]/pointList/z')
# z_wing_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[2]/pointList/z',z_wing_profile_size)
#
# # print x_wing_profile
# # print z_wing_profile
#  
# x_wing_profile_upper=[0]*x_wing_profile_size
# x_wing_profile_lower=[0]*x_wing_profile_size
#  
# t=0
# k=0
# for i in range(0,x_wing_profile_size-1):
#     if x_wing_profile[i]-x_wing_profile[i+1]>0:
#         x_wing_profile_upper[i]=x_wing_profile[i]
#         k=k+1
#     else:
#         x_wing_profile_lower[t]=x_wing_profile[i] 
#         t=t+1
#          
# x_wing_profile_lower[t]=x_wing_profile[0]
#  
# x_wing_profile_upper_cut=[0]*k
# x_wing_profile_lower_cut=[0]*t
#  
# for i in range(0,k):
#     x_wing_profile_upper_cut[i]=x_wing_profile_upper[i]
#      
# for i in range(0,t):
#     x_wing_profile_lower_cut[i]=x_wing_profile_lower[i] 
#  
# z_wing_profile_upper=[0]*k
# z_wing_profile_lower=[0]*t
#  
# for i in range(0,k):
#     z_wing_profile_upper[i]=z_wing_profile[i]
#  
# for i in range(0,t):
#     z_wing_profile_lower[i]=z_wing_profile[k+i]    
#      
# z_wing_profile_upper_fliplr=z_wing_profile_upper[ ::-1 ] 
# x_wing_profile_upper_fliplr=x_wing_profile_upper_cut[ ::-1 ] 
#  
# xlinspace=np.linspace(0.05,0.95, num=100) #modificare gli estremi
# f_wing_upper=interpolate.interp1d(x_wing_profile_upper_fliplr,z_wing_profile_upper_fliplr)(xlinspace)
# f_wing_lower=interpolate.interp1d(x_wing_profile_lower_cut,z_wing_profile_lower)(xlinspace)
# thickness_wing=[0]*xlinspace
# thickness_wing=np.subtract(f_wing_upper,f_wing_lower)
# max_thickness_wing=np.max(thickness_wing)#percent of chord
#  
# # print "x_lower_WING"
# # print x_wing_profile_lower_cut
# # print "x_upper_WING"
# # print x_wing_profile_upper_cut
# # print k
# # print t
# # print x_wing_profile_size
# # print z_wing_profile_lower
# # print z_wing_profile_upper
# print "wing_thickness = {}".format(max_thickness_wing)
# 
# #HT
# x_HT_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[3]/pointList/x')
# x_HT_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[3]/pointList/x',x_HT_profile_size)
# 
# z_HT_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[3]/pointList/z')
# z_HT_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[3]/pointList/z',z_HT_profile_size)
# 
# # print x_HT_profile
# # print z_HT_profile
# 
# x_HT_profile_upper=[0]*x_HT_profile_size
# x_HT_profile_lower=[0]*x_HT_profile_size
# 
# t=0
# k=0
# for i in range(0,x_HT_profile_size-1):
#     if x_HT_profile[i]-x_HT_profile[i+1]>0:
#         x_HT_profile_upper[i]=x_HT_profile[i]
#         k=k+1
#     else:
#         x_HT_profile_lower[t]=x_HT_profile[i] 
#         t=t+1
#         
# x_HT_profile_lower[t]=x_HT_profile[0]
# 
# x_HT_profile_upper_cut=[0]*k
# x_HT_profile_lower_cut=[0]*t
# 
# for i in range(0,k):
#     x_HT_profile_upper_cut[i]=x_HT_profile_upper[i]
#     
# for i in range(0,t):
#     x_HT_profile_lower_cut[i]=x_HT_profile_lower[i] 
# 
# z_HT_profile_upper=[0]*k
# z_HT_profile_lower=[0]*t
# 
# for i in range(0,k):
#     z_HT_profile_upper[i]=z_HT_profile[i]
# 
# for i in range(0,t):
#     z_HT_profile_lower[i]=z_HT_profile[k+i]    
#     
# z_HT_profile_upper_fliplr=z_HT_profile_upper[ ::-1 ] 
# x_HT_profile_upper_fliplr=x_HT_profile_upper_cut[ ::-1 ] 
# 
# xlinspace=np.linspace(0.05,0.95, num=100) #modificare gli estremi
# f_HT_upper=interpolate.interp1d(x_HT_profile_upper_fliplr,z_HT_profile_upper_fliplr)(xlinspace)
# f_HT_lower=interpolate.interp1d(x_HT_profile_lower_cut,z_HT_profile_lower)(xlinspace)
# thickness_HT=[0]*xlinspace
# thickness_HT=np.subtract(f_HT_upper,f_HT_lower)
# max_thickness_HT=np.max(thickness_HT)#percent of chord
# 
# # print "x_lower_HT"
# # print x_HT_profile_lower_cut
# # print "x_upper_HT"
# # print x_HT_profile_upper_cut
# # print k
# # print t
# # print x_HT_profile_size
# # print z_HT_profile_lower
# # print z_HT_profile_upper
# print "HT_thickness = {}".format(max_thickness_HT)
# 
# 
# #VT
# x_VT_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[4]/pointList/x')
# x_VT_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[4]/pointList/x',x_VT_profile_size)
# 
# z_VT_profile_size=tixi_s.getVectorSize('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[4]/pointList/z')
# z_VT_profile=tixi_s.getFloatVector('/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil[4]/pointList/z',z_VT_profile_size)
# 
# # print x_VT_profile
# # print z_VT_profile
# 
# x_VT_profile_upper=[0]*x_VT_profile_size
# x_VT_profile_lower=[0]*x_VT_profile_size
# 
# t=0
# k=0
# for i in range(0,x_VT_profile_size-1):
#     if x_VT_profile[i]-x_VT_profile[i+1]>0:
#         x_VT_profile_upper[i]=x_VT_profile[i]
#         k=k+1
#     else:
#         x_VT_profile_lower[t]=x_VT_profile[i] 
#         t=t+1
#         
# x_VT_profile_lower[t]=x_VT_profile[0]
# 
# x_VT_profile_upper_cut=[0]*k
# x_VT_profile_lower_cut=[0]*t
# 
# for i in range(0,k):
#     x_VT_profile_upper_cut[i]=x_VT_profile_upper[i]
#     
# for i in range(0,t):
#     x_VT_profile_lower_cut[i]=x_VT_profile_lower[i] 
# 
# z_VT_profile_upper=[0]*k
# z_VT_profile_lower=[0]*t
# 
# for i in range(0,k):
#     z_VT_profile_upper[i]=z_VT_profile[i]
# 
# for i in range(0,t):
#     z_VT_profile_lower[i]=z_VT_profile[k+i]    
#     
# z_VT_profile_upper_fliplr=z_VT_profile_upper[ ::-1 ] 
# x_VT_profile_upper_fliplr=x_VT_profile_upper_cut[ ::-1 ] 
# 
# xlinspace=np.linspace(0.05,0.95, num=100) #modificare gli estremi
# f_VT_upper=interpolate.interp1d(x_VT_profile_upper_fliplr,z_VT_profile_upper_fliplr)(xlinspace)
# f_VT_lower=interpolate.interp1d(x_VT_profile_lower_cut,z_VT_profile_lower)(xlinspace)
# thickness_VT=[0]*xlinspace
# thickness_VT=np.subtract(f_VT_upper,f_VT_lower)
# max_thickness_VT=np.max(thickness_VT) #percent of chord
# 
# # print "x_lower_VT"
# # print x_VT_profile_lower_cut
# # print "x_upper_VT"
# # print x_VT_profile_upper_cut
# # print k
# # print t
# # print x_VT_profile_size
# # print z_VT_profile_lower
# # print z_VT_profile_upper
# print "VT_thickness = {}".format(max_thickness_VT)


########################################### Sweep Angle (LE and q.c)

#Leading edge
sweep_angle_array=[[0]]*nWing
X_inner=[[0]]*nWing
Y_inner=[[0]]*nWing
Z_inner=[[0]]*nWing

for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        X_inner[i] =[[0]]*wSegCount[i]
        Y_inner[i] =[[0]]*wSegCount[i]
        Z_inner[i] =[[0]]*wSegCount[i]         
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) : 
        (X_inner[i][j],Y_inner[i][j],Z_inner[i][j])=tigl_s.wingGetUpperPoint(wIndex[i], wSegIndex[i][j], 0, 0)

# print X_inner[mainWPos]
# print Y_inner[mainWPos]
# print X_outer[mainWPos]
# print Y_outer[mainWPos]

for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        sweep_angle_array[i] =[[0]]*wSegCount[i]
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        if wSymmetry[i]==2:
            sweep_angle_array[i][j] = math.atan((X_outer[i][j]-X_inner[i][j])/(Y_outer[i][j]-Y_inner[i][j]))  
            sweep_angle_array[i][j] = math.degrees(sweep_angle_array[i][j])
        else:
            sweep_angle_array[i][j] = math.atan((X_outer[i][j]-X_inner[i][j])/(Z_outer[i][j]-Z_inner[i][j])) 
            sweep_angle_array[i][j] = math.degrees(sweep_angle_array[i][j])
print 'sweep_angle_LE_array = {}'.format(sweep_angle_array)

sweep_angle_i=[0]*nWing
for i in range(0,nWing) :
    kk=0
    if wSymmetry[i]==2:
        for j in range(0,wSegCount[i]) :
            if j==0:
                sweep_angle_i[i]=kk+Y_outer[i][j]*sweep_angle_array[i][j]/(wSpan[i]/2)
                kk=sweep_angle_i[i]
            else:
                sweep_angle_i[i]=kk+(Y_outer[i][j]-Y_outer[i][j-1])*sweep_angle_array[i][j]/(wSpan[i]/2)
                kk=sweep_angle_i[i]
    else:
        for j in range(0,wSegCount[i]) :
            if j==0:
                sweep_angle_i[i]=kk+Z_outer[i][j]*sweep_angle_array[i][j]/(Z_outer[i][-1])
                kk=sweep_angle_i[i]
            else:
                sweep_angle_i[i]=kk+(Z_outer[i][j]-Z_outer[i][j-1])*sweep_angle_array[i][j]/(Z_outer[i][-1])
                kk=sweep_angle_i[i]             
print 'sweep_angle_LE_i = {}'.format(sweep_angle_i)

#Quarter of the chord
sweep_angle_qc_array=[[0]]*nWing
X_inner_qc=[[0]]*nWing
Y_inner_qc=[[0]]*nWing
Z_inner_qc=[[0]]*nWing
X_outer_qc=[[0]]*nWing
Y_outer_qc=[[0]]*nWing
Z_outer_qc=[[0]]*nWing

for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        X_inner_qc[i] =[[0]]*wSegCount[i]
        Y_inner_qc[i] =[[0]]*wSegCount[i]
        Z_inner_qc[i] =[[0]]*wSegCount[i]         
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) : 
        (X_inner_qc[i][j],Y_inner_qc[i][j],Z_inner_qc[i][j])=tigl_s.wingGetUpperPoint(wIndex[i], wSegIndex[i][j], 0, 0.25)
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        X_outer_qc[i] =[[0]]*wSegCount[i]
        Y_outer_qc[i] =[[0]]*wSegCount[i]
        Z_outer_qc[i] =[[0]]*wSegCount[i] #sara' leggermente differente       
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) : 
        (X_outer_qc[i][j],Y_outer_qc[i][j],Z_outer_qc[i][j])=tigl_s.wingGetUpperPoint(wIndex[i], wSegIndex[i][j], 1, 0.25)
        
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        sweep_angle_qc_array[i] =[[0]]*wSegCount[i]
for i in range(0,nWing) :
    for j in range(0,wSegCount[i]) :
        if wSymmetry[i]==2:
            sweep_angle_qc_array[i][j] = math.atan((X_outer_qc[i][j]-X_inner_qc[i][j])/(Y_outer_qc[i][j]-Y_inner_qc[i][j]))  
            sweep_angle_qc_array[i][j] = math.degrees(sweep_angle_qc_array[i][j])
        else:
            sweep_angle_qc_array[i][j] = math.atan((X_outer_qc[i][j]-X_inner_qc[i][j])/(Z_outer_qc[i][j]-Z_inner_qc[i][j])) 
            sweep_angle_qc_array[i][j] = math.degrees(sweep_angle_qc_array[i][j])
print 'sweep_angle_qc_array = {}'.format(sweep_angle_qc_array)

sweep_angle_qc_i=[0]*nWing
for i in range(0,nWing) :
    kk=0
    if wSymmetry[i]==2:
        for j in range(0,wSegCount[i]) :
            if j==0:
                sweep_angle_qc_i[i]=kk+Y_outer_qc[i][j]*sweep_angle_qc_array[i][j]/(wSpan[i]/2)
                kk=sweep_angle_qc_i[i]
            else:
                sweep_angle_qc_i[i]=kk+(Y_outer_qc[i][j]-Y_outer_qc[i][j-1])*sweep_angle_qc_array[i][j]/(wSpan[i]/2)
                kk=sweep_angle_qc_i[i]
    else:
        for j in range(0,wSegCount[i]) :
            if j==0:
                sweep_angle_qc_i[i]=kk+Z_outer_qc[i][j]*sweep_angle_qc_array[i][j]/(Z_outer_qc[i][-1])
                kk=sweep_angle_qc_i[i]
            else:
                sweep_angle_qc_i[i]=kk+(Z_outer_qc[i][j]-Z_outer_qc[i][j-1])*sweep_angle_qc_array[i][j]/(Z_outer_qc[i][-1])
                kk=sweep_angle_qc_i[i]             
print 'sweep_angle_qc_i = {}'.format(sweep_angle_qc_i)


################################################## Nacelles

nacelle_length=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/engine/nacelle/length')   
nacelle_diameter=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/engine/nacelle/diameter')   
d_fine_nacelle=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/engine/nacelle/last_section_diameter')   
Number_engines=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/engine/number')   
S_wet_nacelle=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/engine/nacelle/S_wet')   
S_wet_nacelle=[S_wet_nacelle]*Number_engines


############################################# Conditions
#altitude in meters
cruise_altitude = tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/ReferencePoint/altitude')
H=cruise_altitude
mu0=1.79*10**(-5) #kg/(ms)
T0=288#K
T_celsius=std_atm.alt2temp(H, alt_units='m', temp_units='C')
T=T_celsius+273.15

#dynamic_viscosity
dynamic_viscosity=mu0*(T/T0)**(1.5)*(T0+110)/(T+110)

#density at cruise altitude
rho=std_atm.alt2density(H, alt_units='m', density_units = 'kg/m**3')#[Kg]/[m^3]

#Cruise Mach Number
MachSize=tixi_s.getVectorSize('/cpacs/toolspecific/UNINA_modules/ReferencePoint/MachNumber')
Mach=tixi_s.getFloatVector('/cpacs/toolspecific/UNINA_modules/ReferencePoint/MachNumber',MachSize)
Mach_number=Mach[0]
# oppure da 
# Mach= tixi_s.getDoubleElement('/cpacs/missions/mission[2]/segments/segment[1]/mach')
# Mach=tixi_s.getDoubleElement('/cpacs/vehicles/aircraft/model/global/machCruise')
sound_speed=std_atm.temp2speed_of_sound(T_celsius, temp_units='C', speed_units='m/s')

#oppure da
#cruise_altitude = tixi_s.getDoubleElement('/cpacs/missions/mission[2]/segments/segment[1]/altitude')

############################################ Reynolds Number

#Inizialization
R_co_surface=[0]*nWing
Re_surface_scaled=[0]*nWing
k_surface_material=[0]*nWing   
Cf_lam_surface=[0]*nWing
Cf_tur_surface=[0]*nWing
x_tr=[0]*nWing                              #upper surface transition point
Cf_surf_total=[0]*nWing

R_co_fuselage=[0]*nFus
Re_fuselage_scaled=[0]*nFus
k_fuselage_material=[0]*nFus   
Cf_tur_fuselage=[0]*nFus

Re_co_nacelle=[0]*Number_engines
Re_nacelle_scaled=[0]*Number_engines
k_nacelle_material=[0]*Number_engines   
Cf_tur_nacelle=[0]*Number_engines

Index_surface_material=[0]*nWing
Index_fuselage_material=[0]*nFus
Index_nacelle_material=0

#Load the values
Index_surface_material[0]=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/wings/MainWing/material')
Index_surface_material[1]=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/wings/HorizTail/material')
Index_surface_material[2]=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/wings/VerticalTail/material')

Index_fuselage_material[0]=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/fuselages/material')

Index_nacelle_material=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/engine/nacelle/material')

for i in range(0,nWing):
    if Index_surface_material[i]==0:
        k_surface_material[i]=0.052*10**(-5)  #Scabrosita' superficiale composito (m)
    if Index_surface_material[i]==1:
        k_surface_material[i]=1.015*10**(-5)  #Scabrosita' superficiale alluminio (m)
    if Index_surface_material[i]==2:
        k_surface_material[i]=0.634*10**(-5)  #Scabrosita' superficiale alluminio verniciato (m)
print "Index_surface_material = {}".format(Index_surface_material)

for i in range(0,nFus):
    if Index_fuselage_material[i]==0:
        k_fuselage_material[i]=0.052*10**(-5)  #Scabrosita' superficiale composito (m)
    if Index_fuselage_material[i]==1:
        k_fuselage_material[i]=1.015*10**(-5)  #Scabrosita' superficiale alluminio (m)
    if Index_fuselage_material[i]==2:
        k_fuselage_material[i]=0.634*10**(-5)  #Scabrosita' superficiale alluminio verniciato (m)
    if Index_fuselage_material[i]==3:
        k_fuselage_material[i]=0.405*10**(-5)  #Scabrosita' superficiale metallo (m)
    if Index_fuselage_material[i]==4:
        k_fuselage_material[i]=0.152*10**(-5)  #Scabrosita' superficiale metallo trattato (m)
print "Index_fuselage_material = {}".format(Index_fuselage_material)

for i in range(0,Number_engines):
    if Index_nacelle_material==0:
        k_nacelle_material[i]=0.052*10**(-5)  #Scabrosita' superficiale composito (m)
    if Index_nacelle_material==1:
        k_nacelle_material[i]=1.015*10**(-5)  #Scabrosita' superficiale alluminio (m)
    if Index_nacelle_material==2:
        k_nacelle_material[i]=0.634*10**(-5)  #Scabrosita' superficiale alluminio verniciato (m)
    if Index_nacelle_material==3:
        k_nacelle_material[i]=0.405*10**(-5)  #Scabrosita' superficiale metallo (m)
    if Index_nacelle_material==4:
        k_nacelle_material[i]=0.152*10**(-5)  #Scabrosita' superficiale metallo trattato (m)
print "Index_nacelle_material = {}".format(Index_nacelle_material)

#ReSize=tixi_s.getVectorSize('/cpacs/toolspecific/UNINA_modules/ReferencePoint/ReynoldsNumber')
#Re=tixi_s.getFloatVector('/cpacs/toolspecific/UNINA_modules/ReferencePoint/ReynoldsNumber',ReSize)
Re_surface=Mach_number*sound_speed*MAC_W*rho/dynamic_viscosity
Re_fuselage=Mach_number*sound_speed*Lf*rho/dynamic_viscosity
print "Surface Reynolds number = {}".format(Re_surface)
print "Fuselage Reynolds number = {}".format(Re_fuselage)

x_tr[0]=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/wings/MainWing/transition_point')
x_tr[1]=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/wings/HorizTail/transition_point')
x_tr[2]=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/wings/VerticalTail/transition_point')

for i in range(0,nWing):
    R_co_surface[i]       = 38.21*(wMAC[i][0]/k_surface_material[i])**1.053   #Reynolds di cut-off 
    Re_surface_scaled[i]  = Re_surface*wMAC[i][0]/MAC_W                      
    if R_co_surface[i]<Re_surface_scaled[i] :
        Cf_lam_surface[i]  = 1.328/math.sqrt(R_co_surface[i])
        Cf_tur_surface[i]  = 0.455/(((math.log10(R_co_surface[i]))**2.58)*(1+0.144*Mach_number**2)**0.65) #Coefficiente di attrito turbolento
    else :
        Cf_lam_surface[i]  = 1.328/math.sqrt(Re_surface_scaled[i]) 
        Cf_tur_surface[i]  = 0.455/(((math.log10(Re_surface_scaled[i]))**2.58)*(1+0.144*Mach_number**2)**0.65)
    Cf_surf_total[i]=Cf_lam_surface[i]*x_tr[i]+Cf_tur_surface[i]*(1-x_tr[i])    

for i in range(0,nFus):
    R_co_fuselage[i]       = 38.21*(x_ell[i][-1]/k_fuselage_material[i])**1.053   #Reynolds di cut-off 
    Re_fuselage_scaled[i]  = Re_fuselage*x_ell[i][-1]/Lf #oppure Re_surfacee*x_ell[i][-1]/MAC_W                   
    if R_co_fuselage[i]<Re_fuselage_scaled[i] :
        Cf_tur_fuselage[i]  = 0.455/(((math.log10(R_co_fuselage[i]))**2.58)*(1+0.144*Mach_number**2)**0.65) #Coefficiente di attrito turbolento
    else :
        Cf_tur_fuselage[i]  = 0.455/(((math.log10(Re_fuselage_scaled[i]))**2.58)*(1+0.144*Mach_number**2)**0.65)     

for i in range(0,Number_engines):
    Re_co_nacelle[i]       = 38.21*(nacelle_length/k_nacelle_material[i])**1.053   #Reynolds di cut-off 
    if Re_co_nacelle[i]!=0:
        Re_nacelle_scaled[i]  = Re_surface*nacelle_length/MAC_W                   
        if Re_co_nacelle[i]<Re_nacelle_scaled[i] :
            Cf_tur_nacelle[i]  = 0.455/(((math.log10(Re_co_nacelle[i]))**2.58)*(1+0.144*Mach_number**2)**0.65) #Coefficiente di attrito turbolento
        else :
            Cf_tur_nacelle[i]  = 0.455/(((math.log10(Re_nacelle_scaled[i]))**2.58)*(1+0.144*Mach_number**2)**0.65)      
    else:
        Re_nacelle_scaled[i]=0
        Cf_tur_nacelle[i]=0

################################################## RESULTS

## SKIN FRICTION DRAG COEFFICIENTS 
FF_surface=[0]*(nWing)
FF_fuselage=[0]*(nFus)
FF_nacelle=[0]*(Number_engines)
CD0_surface_i=[0]*(nWing)
CD0_fuselage_i=[0]*(nFus)
CD0_nacelle=[0]*(Number_engines)

#Introduce wetted area
WettedParameter=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/wings/WettedParameter')
if WettedParameter==0:
    print 'Wings Wetted Area estimated with TIGL function'
    for i in range(0,nWing):
        if wSymmetry[i]==2:  
            wWettedArea[i]=tigl_s.wingGetWettedArea(wingUid[i])
            wWettedArea[i]=2*wWettedArea[i]
        else:
            wWettedArea[i]=tigl_s.wingGetWettedArea(wingUid[i])
else:
    if aircraftConfiguration==0:
        print 'Wings Wetted Area estimated with Approximately function (Stanford)'
        X_j_TE=[0]*nWing
        X_j_LE=[0]*nWing
        Z_j_LE=[0]*nWing
        position_inner=[0]*nWing #for the fuselage
        position_outer=[0]*nWing 
       
        X_j_TE[mainWPos]=tigl_s.wingGetChordPoint(wIndex[mainWPos], 1, 0, 1)[0]   
        X_j_LE[mainWPos]=tigl_s.wingGetChordPoint(wIndex[mainWPos], 1, 0, 0)[0]
        X_j_TE[HTPos]=tigl_s.wingGetChordPoint(wIndex[HTPos], 1, 0, 1)[0]   
        X_j_LE[HTPos]=tigl_s.wingGetChordPoint(wIndex[HTPos], 1, 0, 0)[0]  
        Z_j_LE[mainWPos]=tigl_s.wingGetChordPoint(wIndex[mainWPos], 1, 0, 0)[2]  
        Z_j_LE[HTPos]=tigl_s.wingGetChordPoint(wIndex[HTPos], 1, 0, 0)[2]
                
        disp_ref=d_fus_max_z_array[0]/2-fP_up[FusPos][in_cone]-Z  
        Z_wing=Z_j_LE[mainWPos]+disp_ref 
        print "Wing Z-position in FPR= {}".format(Z_wing)
                
        Z_ht=Z_j_LE[HTPos]+disp_ref 
        print "HT Z-position in FPR= {}".format(Z_ht)
         
        #Wing   (ipotized: fuselage diameter at wing station is constant through the wing root)     
        j=0
        while j<(len(x_ell[FusPos])):
            if x_ell[FusPos][j+1]>X_inner[mainWPos][0] and x_ell[FusPos][j]<X_inner[mainWPos][0]:
                diameter_WingFuselage=(section_diameter[FusPos][j]+section_diameter[FusPos][j+1])/2  #APPROXIMATION: maximum diameter in Z-direction and linear interpolation
                break
            j=j+1 
        if Z_wing/(diameter_WingFuselage/2)<-0.5:
            wWettedArea[mainWPos]=2*(1+0.2*max_thickness_wing[mainWPos])*(2*wRefArea[mainWPos]-(X_j_TE[mainWPos]-X_j_LE[mainWPos])*diameter_WingFuselage/2)
            print "Low wing aircraft configuration"
        elif Z_wing/(diameter_WingFuselage/2)>0.5:
            print "High wing aircraft configuration"
            wWettedArea[mainWPos]=2*(1+0.2*max_thickness_wing[mainWPos])*(2*wRefArea[mainWPos]-(X_j_TE[mainWPos]-X_j_LE[mainWPos])*diameter_WingFuselage/2)
        else:
            print "Mid wing aircraft configuration"
            wWettedArea[mainWPos]=2*(1+0.2*max_thickness_wing[mainWPos])*(2*wRefArea[mainWPos]-(X_j_TE[mainWPos]-X_j_LE[mainWPos])*diameter_WingFuselage)
        
        #HT
        j=0
        while j<(len(x_ell[FusPos])):
            if x_ell[FusPos][j+1]>X_inner[HTPos][0] and x_ell[FusPos][j]<X_inner[HTPos][0]:
                diameter_WingHT_inner=(section_diameter[FusPos][j]+section_diameter[FusPos][j+1])/2  #APPROXIMATION: maximum diameter in Z-direction and linear interpolation
                position_HTinFus=j
                print "Section fuselage for HT ={}".format(position_HTinFus)
                break
            j=j+1 
        Z_Fus_HT=tigl_s.fuselageGetPoint(fusIndex[FusPos],position_HTinFus-1,0,0)[2]
        if Z_ht-Z_Fus_HT<0:
            wWettedArea[HTPos]=2*(1+0.2*max_thickness_wing[HTPos])*(2*wRefArea[HTPos]-(X_j_TE[HTPos]-X_j_LE[HTPos])*diameter_WingHT_inner/2)
            print "HT positioned in fuselage"
        else:
            wWettedArea[HTPos]=2*(1+0.2*max_thickness_wing[HTPos])*(2*wRefArea[HTPos])
            print "HT positioned in VT"
        
        #VT
        wWettedArea[VTPos]=wSurfArea[VTPos] #good estimation for the Vertical Tail
    else:
        print 'ERROR : Set WettedParameter=0 in tool_specific for Advanced Configuration'
        exit(0)
print 'wWettedArea = {}'.format(wWettedArea)

fuselage_wet_area=[0]*nFus
fuselage_WettedParameter=tixi_s.getIntegerElement('/cpacs/toolspecific/UNINA_modules/fuselages/WettedParameter')
fuselage_wet_area_ts=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/fuselages/wettedArea')
if fuselage_wet_area_ts==0:
    for i in range(0,nFus):
        fuselage_wet_area[i]=fusSurfArea[i]
else:
    fuselage_wet_area[FusPos]=fuselage_wet_area_ts
if fuselage_WettedParameter==0:
    print "Stanford Formula for evaluating Fuselage wetted area"
    Swet_nose=0.75*np.pi*Lnose*np.mean(section_diameter[FusPos][in_cone+1])
    Swet_tailcone=0.72*np.pi*Lcone*np.mean(section_diameter[FusPos][in_cone+1])
    Swet_cabin=np.pi*(Lf-Lcone-Lnose)*np.mean(section_diameter[FusPos][in_cone+1])
    print "Swet_nose = {}".format(Swet_nose)
    print "Swet_tailcone = {}".format(Swet_tailcone)
    print "Swet_cabin = {}".format(Swet_cabin)
    fuselage_wet_area[FusPos]=Swet_nose+Swet_tailcone+Swet_cabin
print "Fuselage_wet_area = {}".format(fuselage_wet_area)


if aircraftConfiguration==0:
    summation=[0]*wSegCount[mainWPos]
    for j in range(0,wSegCount[mainWPos]):
        if j==wSegCount[mainWPos]-1:
            summation[j]=(X_inner[mainWPos][j]+X_outer[mainWPos][-1]-2*X_inner[mainWPos][0])*(Y_outer[mainWPos][-1]/(bw/2)-Y_inner[mainWPos][j]/(bw/2))
        else:
            summation[j]=(X_inner[mainWPos][j]+X_inner[mainWPos][j+1]-2*X_inner[mainWPos][0])*(Y_inner[mainWPos][j+1]/(bw/2)-Y_inner[mainWPos][j]/(bw/2))
    sweep_angle_LE_equiv=math.atan((bw*(X_outer[mainWPos][-1]-X_inner[mainWPos][0])-0.5*bw*sum(summation))/((0.5*bw)**2))  #eta_root=0 , wing starts from x-axes
    print "sweep_angle_LE_equiv_WING = {}".format(math.degrees(sweep_angle_LE_equiv))
    sweep_angle_qc_equiv=math.degrees(sweep_angle_LE_equiv)-math.degrees(math.atan((1-(Ctip_w/Croot_w))/(ARw*(1+(Ctip_w/Croot_w)))))
    print "sweep_angle_qc_equiv_WING = {}".format(sweep_angle_qc_equiv)
    K_c=1/(math.sqrt(1-Mach_number**2*(math.cos(math.radians(sweep_angle_qc_equiv)))**2))   #insert sweep_angle_qc equivalent wing
    print "K_c = {}".format(K_c)

if aircraftConfiguration==1:
    for i in range(0,nWing) :
        FF_surface[i]=1+1.2*(max_thickness_wing[i])+100*(max_thickness_wing[i])**4
        CD0_surface_i[i]=Cf_surf_total[i]*FF_surface[i]*wWettedArea[i]/Sw
    for i in range(0,nFus) :
        FF_fuselage[i]=1+60/(FR[i])**3+0.0025*FR[i]
        CD0_fuselage_i[i]=Cf_tur_fuselage[i]*FF_fuselage[i]*fuselage_wet_area[i]/Sw
else:
    FF_surface[mainWPos]=1+1.2*(max_thickness_wing[mainWPos])*math.cos(math.radians(sweep_angle_qc_i[mainWPos]))+100*K_c**3*(math.cos(math.radians(sweep_angle_qc_i[mainWPos])))**2*(max_thickness_wing[mainWPos])**4
    FF_surface[HTPos]=1.03+1.85*(max_thickness_wing[HTPos])+80*(max_thickness_wing[HTPos])**4
    FF_surface[VTPos]=1.03+2*(max_thickness_wing[VTPos])+60*(max_thickness_wing[VTPos])**4
    CD0_surface_i[mainWPos]=Cf_surf_total[mainWPos]*FF_surface[mainWPos]*wWettedArea[mainWPos]/Sw
    CD0_surface_i[HTPos]=Cf_surf_total[HTPos]*FF_surface[HTPos]*wWettedArea[HTPos]/Sw
    CD0_surface_i[VTPos]=Cf_surf_total[VTPos]*FF_surface[VTPos]*wWettedArea[VTPos]/Sw   #VT
    FF_fuselage[FusPos]=1+60/(FR[FusPos])**3+0.0025*FR[FusPos]
    CD0_fuselage_i[FusPos]=Cf_tur_fuselage[FusPos]*FF_fuselage[FusPos]*fuselage_wet_area[FusPos]/Sw

for i in range(0,Number_engines):   
        if nacelle_length!=0 and nacelle_diameter!=0:
            FF_nacelle[i]=1+0.165+0.91/(nacelle_length/nacelle_diameter)
            CD0_nacelle[i]=Cf_tur_nacelle[i]*FF_nacelle[i]*S_wet_nacelle[i]/Sw

CD0_tot=np.sum(CD0_surface_i)+np.sum(CD0_fuselage_i)+np.sum(CD0_nacelle)
print "CD0_w_friction = {}".format(CD0_surface_i[mainWPos])
print "FF_w = {}".format(FF_surface[mainWPos])
print "Cf_w = {}".format(Cf_surf_total[mainWPos])
print "CD0_f_friction = {}".format(CD0_fuselage_i[FusPos])
print "FF_f = {}".format(FF_fuselage[FusPos])
print "Cf_f = {}".format(Cf_tur_fuselage[FusPos])
print "CD0_v_friction = {}".format(CD0_surface_i[VTPos])
print "FF_v = {}".format(FF_surface[VTPos])
print "Cf_v = {}".format(Cf_surf_total[VTPos])
print "CD0_h_friction = {}".format(CD0_surface_i[HTPos])
print "FF_h = {}".format(FF_surface[HTPos])
print "Cf_h = {}".format(Cf_surf_total[HTPos])
print "CD0_nacelle_friction = {}".format(CD0_nacelle)
print "FF_nacelle = {}".format(FF_nacelle)
print "CD0_tot_friction = {}".format(CD0_tot)


## MISCELLANEOUS EFFECTS

#EXCRESCENCES
# wSurfArea_new=[0]*nWing
# for i in range(0,nWing) :
#     if wSymmetry[i]==2:
#         wSurfArea_new[i]=2*wSurfArea[i]
#     else:
#         wSurfArea_new[i]=wSurfArea[i]  
S_wet_total=np.sum(wWettedArea)+np.sum(fuselage_wet_area)+np.sum(S_wet_nacelle)
K_ex=4*10**(-19)*S_wet_total**4-2*10**(-14)*S_wet_total**3+5*10**(-10)*S_wet_total**2-7*10**(-6)*S_wet_total+0.0825
print "K_ex = {}".format(K_ex)
print "S_wet_total = {}".format(S_wet_total)

#INTERFERENCE FACTOR 
#Wing-fuselage
if aircraftConfiguration==0:
    print "Wing X-position in FPR = {}".format(X_inner[mainWPos][0]) # Leading Edge point of wing section in fuselage
    disp_ref=d_fus_max_z_array[0]/2-fP_up[FusPos][in_cone]-Z   #to applicate the method-->reference line is at half cabin section-->disp_ref is equal to the displacement of FPR from CPACS x-y plane 
    print "Translation of FPR respect CPACS Z-axes = {}".format(disp_ref)
    Z_wing=Z_inner[mainWPos][0]+disp_ref   #in fuselage plane reference
    print "Wing Z-position in FPR= {}".format(Z_wing)
    j=0
    while j<(len(x_ell[FusPos])):
        if x_ell[FusPos][j+1]>X_inner[mainWPos][0] and x_ell[FusPos][j]<X_inner[mainWPos][0]:
            diameter_WingFuselage=(section_diameter[FusPos][j]+section_diameter[FusPos][j+1])/2  #APPROXIMATION: maximum diameter in Z-direction and linear interpolation
            break
        j=j+1 
    #print "Diameter_WingFuselage = {}".format(diameter_WingFuselage)
    if Z_wing/(diameter_WingFuselage/2)<-0.5:
        h_wing=0    #h_wing :0 for low wing, 0.5 for mid wing, 1 for high wing
        print "Low wing aircraft configuration"
    elif Z_wing/(diameter_WingFuselage/2)>0.5:
        h_wing=1
        print "High wing aircraft configuration"
    else:
        h_wing=0.5
        print "Mid wing aircraft configuration"
    CD0_int_wf = ((0.5*h_wing**2+1.25*h_wing+0.75)*2.16*Croot_w**2*(max_thickness_array[0][0])**3)/Sw
    print "CD0_int_wf = {}".format(CD0_int_wf)
else:
    CD0_int_wf=0
    print "CD0_int_wf = {}".format(CD0_int_wf)
#Wing-Nacelle
CD0_int_wn = 0.0033*nacelle_diameter**2/Sw
print "CD0_int_wn = {}".format(CD0_int_wn)

#WINDSHIELD (Roskam)
CD0_windshield=[0]*nFus
for i in range(0,nFus) :
    CD0_windshield[i]=0.025*CD0_fuselage_i[i]    #Assuming a double curvature window and streamlined configuration
print "CD0_windshield = {}".format(CD0_windshield) 
print "Assuming a double curvature window and streamlined configuration to evaluate CD0_windshield"

#BASE DRAG
#fuselage 
CD0_base_f=[0]*nFus
CD0_base_n=[0]*Number_engines
for i in range(0,nFus) :
    CD0_base_f[i]=(0.029*(section_diameter[i][-2]/d_fus_max_equiv_array[i])**3/(CD0_fuselage_i[i]*(Sw/(math.pi*d_fus_max_equiv_array[i]**2/4))**0.5))*(Sw/(math.pi*d_fus_max_equiv_array[i]**2/4))**(-1)  # [-1] because the last section is equal to zero
print "CD0_base_f = {}".format(CD0_base_f) #Roskam
#nacelle
for i in range(0,Number_engines) :
    if d_fine_nacelle!=0 and nacelle_diameter!=0 and CD0_nacelle[i]!=0:
        CD0_base_n[i]=(0.029*(d_fine_nacelle/nacelle_diameter)**3/(CD0_nacelle[i]*(Sw/(math.pi*nacelle_diameter**2/4))**0.5))*(Sw/(math.pi*nacelle_diameter**2/4))**(-1)
    else:
        CD0_base_n[i]=0
print "CD0_base_n = {}".format(CD0_base_n) #Roskam

#COOLINGS
CD0_cool=[0]*(nFus+nWing+Number_engines) 
for i in range(0,nWing) :
    CD0_cool[i]=0.08*(CD0_surface_i[i])
for i in range(0,nFus) :
    CD0_cool[i+nWing]=0.08*(CD0_fuselage_i[i])
for i in range(0,Number_engines) :
    CD0_cool[nFus+nWing+i]=0.08*(CD0_nacelle[i])
print "CD0_cool = {}".format(CD0_cool) #Roskam

#UPSWEEP (Stanford)
if aircraftConfiguration==0:
    CD0_up=[0]*nFus
    l_up=0.75*Lcone #75 per cent of the tail length
    disp_ref=d_fus_max_z_array[0]/2-fP_up[FusPos][in_cone]-Z   #to applicate the method-->reference line is at half cabin section-->disp_ref is equal to the displacement of FPR from CPACS x-y plane 
    j=-1
    while j>(-len(x_ell[FusPos])):
        if x_ell[FusPos][j]>Lf-0.25*Lcone and x_ell[FusPos][j-1]<Lf-0.25*Lcone:
            if math.fabs(fP_up_2[FusPos][j])-math.fabs(fP_down_2[FusPos][j])<10**(-5):
                z_tail=(fP_up[FusPos][j]+Z+fP_up[FusPos][j-1]+Z)/2
                diameter_upsweep=(section_diameter[FusPos][j]+section_diameter[FusPos][j-1])/2         
            else:
                z_tail=(fP_up_2[FusPos][j]+Z+fP_up[FusPos][j-1]+Z)/2
                diameter_upsweep=(section_diameter[FusPos][j]+section_diameter[FusPos][j-1])/2
            print "Z_tail = {}".format(z_tail) #linear approximation
            print "diameter_upsweep = {}".format(diameter_upsweep) #linear approximation
            break
        j=j-1   
    h_up=z_tail+disp_ref-diameter_upsweep/2 #height of the fuselage respect to the reference line at 75 per cent of the tail length
    #print "h_up = {}".format(h_up)
    for i in range(0,nFus) :
        CD0_up[i]=(0.075*(h_up/l_up)*math.pi*(d_fus_max_equiv_array[i]/2)**2)/Sw
else:
    CD0_up=0
print "CD0_up = {}".format(CD0_up)

#TOTAL
CD0_total=(np.sum(CD0_surface_i)+np.sum(CD0_fuselage_i)+np.sum(CD0_nacelle))*(1+K_ex)+CD0_int_wf+Number_engines*CD0_int_wn+np.sum(CD0_up)+np.sum(CD0_windshield)+np.sum(CD0_base_n)+np.sum(CD0_base_f)+np.sum(CD0_cool)
print "CD0_total = {}".format(CD0_total)

#PARTIAL EFFECTS
CD0_ex=(np.sum(CD0_surface_i)+np.sum(CD0_fuselage_i)+np.sum(CD0_nacelle))*(K_ex)
CD0_int=CD0_int_wf+Number_engines*CD0_int_wn
CD0_w=np.sum(CD0_windshield)
CD0_bd=np.sum(CD0_base_n)+np.sum(CD0_base_f)
CD0_c=np.sum(CD0_cool)
CD0_u=np.sum(CD0_up)


#######################################PARABOLIC POLAR
CD0_tot_print=format(CD0_total, '.4f')
#Oswald Factor
Oswald_Factor=tixi_s.getDoubleElement('/cpacs/toolspecific/UNINA_modules/ReferencePoint/Oswald_Factor')
CL=np.linspace(-1.5, 1.5, num=100)
CD=CD0_total+1/(math.pi*ARw*Oswald_Factor)*CL**2

plt.figure(1)
plt.plot(CD, CL, 'b-')
plt.ylabel('CL')
plt.xlabel('CD')
plt.grid()
plt.text(0.08,0.1,'CD0_tot = {}'.format(CD0_tot_print),horizontalalignment='center',verticalalignment='center', fontsize=12)
plt.savefig('parabolic_polar.png')
shutil.copy('parabolic_polar.png',cwd+'/ReturnDirectory')
plt.show() #NB after the save

#######################################Alternative: Results
# #Determinate t_w 
# #FF_w=1+1.2*(t_w/MAC_W)+100*(t_w/MAC_W)**4
# FF_w   = 1+1.2*(max_thickness_wing)+100*(max_thickness_wing)**4
# CD0_w  = Cf_surf_total[0] * FF_w * Sw_wet / Sw
# 
# # Determinate t_v 
# #FF_v=1+1.2*(t_v/MAC_VT)+100*(t_v/MAC_VT)**4
# FF_v=1+1.2*(max_thickness_VT)+100*(max_thickness_VT)**4
# CD0_v = Cf_surf_total[2] * FF_v * Sv_wet / Sw
# 
# #Determinate t_h 
# #FF_h=1+1.2*(t_h/MAC_HT)+100*(t_h/MAC_HT)**4
# FF_h=1+1.2*(max_thickness_HT)+100*(max_thickness_HT)**4
# CD0_h = Cf_surf_total[1]* FF_h * Sh_wet / Sw
# 
# ## Calculate the friction drag for the fuselage (turbulent)
# FF_f = 1+(60)/(FR)**3+0.0025*FR
# CD0_f = Cf_tur_fuselage[0] * FF_f * fuselage_wet_area / Sw
# 
# #CD0 total
# CD0_tot=CD0_w+CD0_f+CD0_h+CD0_v

# print "CD0_w_friction = {}".format(CD0_w)
# print "FF_w = {}".format(FF_w)
# print "CD0_f_friction = {}".format(CD0_f)
# print "FF_f = {}".format(FF_f)
# print "CD0_v_friction = {}".format(CD0_v)
# print "FF_v = {}".format(FF_v)
# print "CD0_h_friction = {}".format(CD0_h)
# print "FF_h = {}".format(FF_h)
# print "CD0_tot_friction = {}".format(CD0_tot) 

# UPSWEEP  
# j=-1
# while j>(-len(x_ell[FusPos])):
#     if x_ell[FusPos][j]>Lf-0.25*Lcone and x_ell[FusPos][j-1]<Lf-0.25*Lcone:
#         if x_ell[FusPos][j]-(Lf-0.25*Lcone)<=Lf-0.25*Lcone-x_ell[FusPos][j-1]:
#             x_upsweep=fusSecCount[FusPos]+j
#         else:
#             x_upsweep=fusSecCount[FusPos]+j-1
#         print "Next Section of 0.75 Lcone = {}".format(x_upsweep) #approximation
#         break
#     j=j-1   
# disp_ref=d_fus_max_z_array[0]/2-fP_up[FusPos][in_cone]-Z   #to applicate the method-->reference line is at half cabin section-->disp_ref is equal to the displacement of FPR from CPACS x-y plane 
# for i in range(0,nFus):
#     for j in range(0,fusSegCount[i]+1):
#         if math.fabs(fP_up_2[i][j])-math.fabs(fP_down_2[i][j])<10**(-5):
#             z_tail=fP_up[FusPos][x_upsweep]+Z
#         else :
#             z_tail=fP_up_2[FusPos][x_upsweep]+Z
# diameter_upsweep=section_diameter[FusPos][x_upsweep]

## Close handle 
tigl_s.close()
tixi_s.close()


######################################UPDATE#####################################
 
## Update CD0.xml

outputfile=cwd+'/CD0.xml'
print outputfile
tixi_s.open(outputfile)
tixi_s.updateDoubleElement('/CD0/Final_Value/CD0_total/value', CD0_total, '%f')
tixi_s.updateDoubleElement('/CD0/Skin_friction/CD0_w/value', CD0_surface_i[mainWPos], '%f')
tixi_s.updateDoubleElement('/CD0/Skin_friction/CD0_f/value', CD0_fuselage_i[FusPos], '%f')
tixi_s.updateDoubleElement('/CD0/Skin_friction/CD0_h/value', CD0_surface_i[HTPos], '%f')
tixi_s.updateDoubleElement('/CD0/Skin_friction/CD0_v/value', CD0_surface_i[VTPos], '%f')
tixi_s.updateDoubleElement('/CD0/Skin_friction/CD0_n/value', CD0_nacelle[0], '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_Excrescenses/value', CD0_ex, '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_Interference/value', CD0_int, '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_Windshield/value', CD0_w, '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_BaseDrag/value', CD0_bd, '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_Coolings/value', CD0_c, '%f')
tixi_s.updateDoubleElement('/CD0/Miscellaneous_effects/CD0_Upsweep/value', CD0_u, '%f')
tixi_s.save(outputfile)
tixi_s.close() 
#in this way you can save outputfile ('CD0.xml') like outfile (toolOutput)
shutil.copyfile(outputfile,outfile)
shutil.copy(outputfile,cwd+'/ReturnDirectory')

