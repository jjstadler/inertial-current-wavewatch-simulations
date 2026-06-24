import numpy as np
import pandas as pd
import xarray as xr

""" 
Need a function to automoate finding each phase
Look for max and min's of u and v? 
"""

def find_phase_inds(data, phase, amp):
    """
    Function to find indicies for a given phase
    Input:
        data: xarray dataframe with the ww3 output
        phase: string, one of ["west", "north", "east", "south"]
        amp: maximum amplitude of current
    output:
        inds: list of indicies where current matches the desired phase
    """

    if phase == "west":
        ucur = -1*amp
        vcur = 0
    elif phase== "north":
        vcur = amp
        ucur=0
    elif phase== "east":
        vcur = 0
        ucur = amp
    elif phase == "south":
        vcur=-1*amp
        ucur=0
    elif not isinstance(phase, str):
        #phase better be radians from 0->2pi (east, south, west, north) - > (0, pi/2, pi, 3pi/2)
        ucur = np.cos(phase)*amp
        vcur = -1*np.sin(phase)*amp #Want sin(pi/2)=-1
    else:
        return(0)
    epsilon = 0.001
    lat_ind = len(data.latitude)//2
    lon_ind = len(data.longitude)//2
    #inds = np.where(np.abs(data.vcur[:, lat_ind, lon_ind]-vcur)<epsilon) and np.where(np.abs(data.ucur[:, lat_ind, lon_ind]-ucur)<epsilon) 
    inds1 = np.where(np.abs(data.vcur[:, lat_ind, lon_ind]-vcur)<epsilon)[0]
    inds2 = np.where(np.abs(data.ucur[:, lat_ind, lon_ind]-ucur)<epsilon)[0]
    inds = list(set(inds1) & set(inds2))
    #Why is this returning some indicies for opposite sign of vcur?
    inds = np.sort(inds)#Get them in order
    inds = np.array(inds)
    return(inds)
