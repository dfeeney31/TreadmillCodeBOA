# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:38:57 2020

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig


# Define constants and options
run = 1 # Set this to 1 where participant is running on one belt so only the left are detected. 0 for dual belt
manualTrim = 0  #set this to 1 if you want to manually trim trials with ginput, 0 if you want it auto trimmed (start and end of trial)
fThresh = 50 #below this value will be set to 0.
writeData = 0 #will write to spreadsheet if 1 entered
plottingEnabled = 0 #plots the bottom if 1. No plots if 0
lookFwd = 600
pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Read in balance file
#fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Hike Work Research\\Work Pilot 2021\\WalkForces\\'
#fPath = 'C:\\Users\\Daniel.Feeney\\Boa Technology Inc\\PFL - General\\HikePilot_2021\\Hike Pilot 2021\\Data\\Forces TM\\'
fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Endurance Health Validation\\DU_Running_Summer_2021\\Data\\Forces\\'
entries = os.listdir(fPath)


# list of functions 
# finding landings on the force plate once the filtered force exceeds the force threshold
def findLandings(force):
    lic = []
    for step in range(len(force)-1):
        if force[step] == 0 and force[step + 1] >= fThresh:
            lic.append(step)
    return lic

#Find takeoff from FP when force goes from above thresh to 0
def findTakeoffs(force):
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0:
            lto.append(step + 1)
    return lto


def calcVLR(force, startVal, lengthFwd, endLoading):
    # function to calculate VLR from 80 and 20% of the max value observed in the first n
    # indices (n defined by lengthFwd). 
    # endLoading should be set to where an impact peak should have occured if there is one
    # and can be biased longer so the for loop doesn't error out
    # lengthFwd is how far forward to look to calculate VLR
    tmpDiff = np.diff(force[startVal:startVal+500])
    
    if next(x for x, val in enumerate( tmpDiff ) 
                      if val < 0) < endLoading:
        maxFindex = next(x for x, val in enumerate( tmpDiff ) 
                      if val < 0)
        maxF = force[startVal + maxFindex]
        eightyPctMax = 0.8 * maxF
        twentyPctMax = 0.2 * maxF
            # find indices of 80 and 20 and calc loading rate as diff in force / diff in time (N/s)
        eightyIndex = next(x for x, val in enumerate(force[startVal:startVal+lengthFwd]) 
                      if val > eightyPctMax) 
        twentyIndex = next(x for x, val in enumerate(force[startVal:startVal+lengthFwd]) 
                      if val > twentyPctMax) 
        VLR = ((eightyPctMax - twentyPctMax) / ((eightyIndex/1000) - (twentyIndex/1000)))
    
    else:
        maxF = np.max(force[startVal:startVal+lengthFwd])
        eightyPctMax = 0.8 * maxF
        twentyPctMax = 0.2 * maxF
        # find indices of 80 and 20 and calc loading rate as diff in force / diff in time (N/s)
        eightyIndex = next(x for x, val in enumerate(force[startVal:startVal+lengthFwd]) 
                          if val > eightyPctMax) 
        twentyIndex = next(x for x, val in enumerate(force[startVal:startVal+lengthFwd]) 
                          if val > twentyPctMax) 
        VLR = ((eightyPctMax - twentyPctMax) / ((eightyIndex/1000) - (twentyIndex/1000)))
        
    return(VLR)
    
#Find max braking force moving forward
def calcPeakBrake(force, landing, length):
    newForce = np.array(force)
    return min(newForce[landing:landing+length])

def findNextZero(force, length):
    # Starting at a landing, look forward (after first 15 indices)
    # to the find the next time the signal goes from - to +
    for step in range(length):
        if force[step] <= 0 and force[step + 1] >= 0 and step > 45:
            break
    return step


def delimitTrial(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.LForceZ, label = 'Left Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = inputDF.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

def filterForce(inputForce, sampFrq, cutoffFrq):
        # low-pass filter the input force signals
        #t = np.arange(len(inputForce)) / sampFrq
        w = cutoffFrq / (sampFrq / 2) # Normalize the frequency
        b, a = sig.butter(4, w, 'low')
        filtForce = sig.filtfilt(b, a, inputForce)
        return(filtForce)
    
def trimForce(inputDF, threshForce):
    forceTot = inputDF.LForceZ
    forceTot[forceTot<threshForce] = 0
    forceTot = np.array(forceTot)
    return(forceTot)

def trimLandings(landingVec, takeoffVec):
    if landingVec[0] > takeoffVec[0]:
        landingVec.pop(0)
        return(landingVec)
    else:
        return(landingVec)
    
def trimTakeoffs(landingVec, takeoffVec):
    if landingVec[0] > takeoffVec[0]:
        takeoffVec.pop(0)
        return(takeoffVec)
    else:
        return(takeoffVec)

#Preallocation
loadingRate = []
peakBrakeF = []
brakeImpulse = []
VLR = []
VLRtwo = []
sName = []
tmpConfig = []
timeP = []
NL = []
PkMed = []
PkLat = []
CT = []

# when COPx is more negative, that is left foot strike
## loop through the selected files
for file in entries[41:47]:
    try:
        
        fName = file #Load one file at a time
        
        #Parse file name into subject and configuration 
        subName = fName.split(sep = "_")[0]
        config = fName.split(sep = "_")[1]
        #config = config.split(sep = " ")[0]

        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)  
        dat = dat.fillna(0)
        dat.LForceZ = -1 * dat.LForceZ
        #dat.LForceZ = filterForce(dat.LForceZ, 1000, 20)
        #dat.LForceY = filterForce(dat.LForceY, 1000, 20)
        #dat.LForceX = filterForce(dat.LForceX, 1000, 20)
        
        # Trim the trials to a smaller section and threshold force
        if manualTrim == 1:
            print('Select start and end of analysis trial 1')
            forceDat = delimitTrial(dat)
        else: 
            forceDat = dat
            
        forceZ = trimForce(forceDat, fThresh)
        MForce = forceDat.LForceX
        brakeFilt = forceDat.LForceY * -1
                
        #find the landings and takeoffs of the FP as vectors
        landings = findLandings(forceZ)
        takeoffs = findTakeoffs(forceZ)
        
        #landings = trimLandings(landings, takeoffs)
        takeoffs = trimTakeoffs(landings, takeoffs)
        # determine if first step is left or right then delete every other
        # landing and takeoff. MORE NEGATIVE IS LEFT
        if run == 1:
            if (np.mean(dat.LCOPx[landings[0]:takeoffs[0]]) < np.mean(dat.LCOPx[landings[1]:takeoffs[1]])): #if landing 0 is left, keep all evens
                trimmedLandings = [i for a, i in enumerate(landings) if  a%2 == 0]
                trimmedTakeoffs = [i for a, i in enumerate(takeoffs) if  a%2 == 0]
            else: #keep all odds
                trimmedLandings = [i for a, i in enumerate(landings) if  a%2 != 0]
                trimmedTakeoffs = [i for a, i in enumerate(takeoffs) if  a%2 != 0]
        else:
            trimmedLandings = landings
            trimmedTakesoffs = takeoffs
        
        #For each landing, calculate rolling averages and time to stabilize
    
        for countVar, landing in enumerate(trimmedLandings):
            try:
               # Define where next zero is
                VLR.append(calcVLR(forceZ, landing, 150,50))
                VLRtwo.append( (np.max( np.diff(forceZ[landing+5:landing+50]) )/(1/1000) ) )
                try:
                    CT.append(trimmedTakeoffs[countVar] - landing)
                except:
                    CT.append(0)
                try:
                    nextLanding = findNextZero( np.array(brakeFilt[landing:landing+lookFwd]),lookFwd )
                    brakeImpulse.append(np.nansum( (brakeFilt[landing:landing+nextLanding]) ))
                except:
                    brakeImpulse.append(0)
                #stepLen.append(findStepLen(forceZ[landing:landing+800],800))
                sName.append(subName)
                tmpConfig.append(config)
                peakBrakeF.append(calcPeakBrake(brakeFilt,landing, lookFwd))
                try:
                    PkMed.append(np.max(MForce[landing:trimmedTakeoffs[countVar]]))
                except:
                    PkMed.append(0)
                try:
                    PkLat.append(np.min(MForce[landing:trimmedTakeoffs[countVar]]))
                except:
                    PkLat.append(0)
                            
            except:
                print(landing)
        
    except:
            print(file)

outcomes = pd.DataFrame({'Subject':list(sName), 'Config': list(tmpConfig),'peakBrake': list(peakBrakeF),
                         'brakeImpulse': list(brakeImpulse), 'VLR': list(VLR), 'VILR':list(VLRtwo),'PkMed':list(PkMed),
                         'PkLat':list(PkLat), 'CT':list(CT)})

outcomes.to_csv("C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Endurance Health Validation\\DU_Running_Summer_2021\\Data\\Forces3.csv",mode='a',header=False)

