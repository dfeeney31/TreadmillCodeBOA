# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 15:46:24 2021

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import os

def calcMean3MinLate(fullDat, inputMarker):
    ## used after 1 hour of testing has elapsed because the date format
    ## is longer
    startTime = fullDat[fullDat['Marker'] == inputMarker].index.tolist()
    td1 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:03:00')
    td2 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:04:00')
    tp1 = fullDat[(fullDat['t'] > str(td1)[5:22]) & (fullDat['t'] < str(td2)[5:22])].reset_index()
    return(np.mean(tp1['EEm']))
    
def calcMean4MinLate(fullDat, inputMarker):
    ## used after 1 hour of testing has elapsed because the date format
    ## is longer
    startTime = fullDat[fullDat['Marker'] == inputMarker].index.tolist()
    td1 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:04:00')
    td2 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:05:00')
    tp1 = fullDat[(fullDat['t'] > str(td1)[5:22]) & (fullDat['t'] < str(td2)[5:22])].reset_index()
    return(np.mean(tp1['EEm']))

def calcMean3min(fullDat, inputMarker):
    startTime = fullDat[fullDat['Marker'] == inputMarker].index.tolist()
    td1 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:03:00')
    td2 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:04:00')
    tp1 = fullDat[(fullDat['t'] > str(td1)[5:20]) & (fullDat['t'] < str(td2)[5:20])].reset_index()

    return(np.mean(tp1['EEm']))

def calcMean4min(fullDat, inputMarker):
    startTime = fullDat[fullDat['Marker'] == inputMarker].index.tolist()
    td1 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:04:00')
    td2 = fullDat['t'][startTime] + pd.to_timedelta('0 days 00:05:00')
    tp1 = fullDat[(dat['t'] > str(td1)[5:20]) & (fullDat['t'] < str(td2)[5:20])].reset_index()

    return(np.mean(tp1['EEm']))

#Parse the column names
headerList = ['zero','one','two','three','four','five','six','seven','eight','t', 'Rf', 'VT', 'VE', 'IV', 'VO2', 'VCO2', 'RQ', 'O2exp', 'CO2exp','VE/VO2', 'VE/VCO2',
'VO2/Kg', 'METS', 'HR', 'VO2/HR', 'FeO2', 'FeCO2', 'FetO2', 'FetCO2', 'FiO2', 'FiCO2', 'PeO2',
 'PeCO2', 'PetO2', 'PetCO2', 'SpO2', 'Phase', 'Marker', 'AmbTemp', 'RHAmb', 'AnalyPress', 'PB', 'EEkc',	
 'EEh',	'EEm', 'EEtot',	'EEkg',	'PRO', 'FAT', 'CHO', 'PRO%', 'FAT%', 'CHO%', 'npRQ', 'GPSDist', 'Ti',
 'Te', 'Ttot', 'Ti/Ttot', 'VD/VTe',	'LogVE', 'tRel', 'markSpeed', 'markDist', 'Phase time', 'VO2/Kg%Pred','BR',	
 'VT/Ti', 'HRR', 'PaCO2_e']

fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Endurance Health Validation\\DU_Running_Summer_2021\\Data\\Metabolics\\'
entries = os.listdir(fPath)

met = []
subject = []
config = []

for file in entries:
    try:
        fName = file
        
        dat = pd.read_excel(fPath+fName, skiprows=2, names = headerList)
        
        dat = dat.drop(dat.columns[[0, 1, 2,3,4,5,6,7,8]], axis=1)  
        dat['t'] = pd.to_timedelta(dat['t'].astype(str)) #Convert time to time delta from start
        
        # this is super hacky but works for now
        for i in range(4):
            config.append('SD')
        for i in range(4):
            config.append('SL')
        for i in range(4):
            config.append('DD')

        met.append(calcMean3min(dat, 'SD_1_Start'))
        met.append(calcMean3min(dat, 'SD_1_Start'))
        met.append(calcMean3MinLate(dat, 'SD_2_Start'))
        met.append(calcMean4MinLate(dat, 'SD_2_Start'))
        
        met.append(calcMean3min(dat, 'SL_1_Start'))
        met.append(calcMean4min(dat, 'SL_1_Start'))
        met.append(calcMean3MinLate(dat, 'SL_2_Start'))
        met.append(calcMean4MinLate(dat, 'SL_2_Start'))   
        
        met.append(calcMean3min(dat, 'DD_1_Start'))
        met.append(calcMean4min(dat, 'DD_1_Start'))
        met.append(calcMean3MinLate(dat, 'DD_2_Start'))
        met.append(calcMean4MinLate(dat, 'DD_2_Start'))
        
        for i in range(12):
            subject.append(file.split(' ')[0])

    except:
        print(file)

        
outcomes = pd.DataFrame({'Subject':list(subject),'Config':list(config), 'EE':list(met)})

outcomes.to_csv('C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Endurance Health Validation\\DU_Running_Summer_2021\\Data\\Met.csv', mode = 'a', header = False)

