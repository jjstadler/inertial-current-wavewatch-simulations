import numpy as np
import xarray as xr
import os
def pm_spectrum(f, fm, Hs):
    """
    Inputs:
        f - numpy array of frequency values (x,) 
        fm - peak frequency (float)
        Hs - Significant Wave Height ( float)
    Outputs:
        f - freqeucy array
        Sf - Energy density Spectrum
    """
    Sf = (5/16) * (Hs**2) * (fm**4) * (f**-5) *np.exp((-5/4)*((f/fm)**-4))
    return(f, Sf)

def dir_normalization_coeff(directions, theta_0, s):
    """
    Return a direcitonal spreading normalization coefficient so that the integral of D_theta over theta = 1
    Cs should be a real number
    """
    dir_sort = np.sort(directions) # Sort
    integral = np.trapz(np.cos((dir_sort-theta_0)/2)**(2*s), dir_sort)
    Cs = 1/integral
    return(Cs)

def dir_spreading(directions, f, theta_0, Sf, s=1):
    """
    Turn 1d spectrum into 2d spectrum. TO DO: Add other directional spreading options other than cos*2.
    Inputs:
        directions - list of directions
        f - list of frequeuncies
        theta_0 - mean wave direction
        Sf - 1d spectrum with freqeuncy bins f

    Outputs:
        F, Theta - Meshgrid frequency and direction coordinates
        S_f_theta - 2d energy density spectra
    """
    #Get normalization coefficient
    Cs = dir_normalization_coeff(directions, theta_0, s)
    
    D_theta = (Cs) * np.cos((directions - theta_0)/2)**(2*s)# Example normalization
    #D_theta = (2 / np.pi) * np.cos((directions - theta_0))**(n*s)# Example normalization

    #don't want spreading in 
    #D_theta[directions>np.pi]=0
    # Create 2D grid
    F, Theta = np.meshgrid(f, directions)
    
    # 2D Pierson-Moskowitz Spectrum
    S_f_theta = np.outer(Sf, D_theta).T # Transpose to match (direction, frequency)

    return(F, Theta, S_f_theta)
    
def save_steady_waves(bounds, hs, fm, save_path, s=1): 
    """
    Inputs:
        hs - target hs of wave forcing
        fm - target peak frequency of wave spectrum
        bounds - [latmin, lonmin, latmax, lonmax]
        save_path - directory to which to save the boundary files
        s = 1 

    """

    #Constants
    g = 9.8 #gravity


    #Direction (to east)
    theta_0 = np.pi/2
    
    #Check if filepath exists, and if not create it
    os.makedirs(save_path, exist_ok=True)

    
    f0 = 0.04118
    f = np.zeros(30)
    f[0] = f0
    xfr = 1.1
    for ind in range(1, len(f)):
        f[ind] = f[ind-1]*1.1
    directions_unsorted = (np.pi/180)*np.array([90.,  75.,  60.,  45.,  30.,  15.,   0., 345., 330., 315., 300., 285.,
       270., 255., 240., 225., 210., 195., 180., 165., 150., 135., 120., 105.])  # degrees
    
    #Seems like maybe these functions behave nicer if directions is monotomically increasing
    directions = np.sort(directions_unsorted)
    f, Sf = pm_spectrum(f, fm, hs)
    F, Theta, S_f_theta = dir_spreading(directions, f, theta_0, Sf, s)

    Sf_calc2 = np.trapz(S_f_theta, Theta, axis=0)
    print(4*np.sqrt(np.trapz(Sf_calc2, F[0, :])))
    #Somewhere between here and the final file the Hs goes from 2.5m to 2.66m
    #create boundary arrays
    lat_range = np.arange(bounds[0], bounds[1]+1, 2)
    lon_range = np.arange(bounds[2], bounds[3]+1, 2)
    right_boundary_lons = np.ones(len(lat_range))*bounds[3]
    right_boundary_lats = lat_range
    top_boundary_lats = np.ones(len(lon_range))*bounds[1]
    top_boundary_lons = lon_range
    left_boundary_lats = lat_range
    left_boundary_lons = np.ones(len(lat_range))*bounds[2]
    bottom_boundary_lats = np.ones(len(lon_range))*bounds[0]
    bottom_boundary_lons = lon_range


    #Load sample spectrum file to build off of (to get formatting for ww3 correct)
    spec ="/Users/jamesstadler/Documents/UW/TFO/Code/ww3_docker/inertial_current_simulations/sample_spec.nc"
    spec = xr.open_dataset(spec)
    #Need to assign frequencies we want
    spec['frequency']= f
    target_dirs = spec.direction
    print(directions_unsorted*180/np.pi)
    #print(spec.direction)
    #Get spec w/ a monotomically increasing direction
    spec = spec.sortby('direction')
    #print(spec.direction)
    #Apply spectrum throughout time
    for time_st in range(len(spec.time)):
        spec.efth[time_st, 0, :, :] = S_f_theta.T

    #Now put spec back in the orginal direcitonal ordering which ww3 likes
    spec = spec.reindex(direction=target_dirs)
    print(spec.direction)
    #print(spec.direction)
    #Save left boundary
    for ind in range(len(left_boundary_lons)):
        spec_save = spec.copy()
        spec_save.longitude[:, 0] = np.ones(len(spec.longitude))*left_boundary_lons[ind]
        spec_save.latitude[:, 0] = np.ones(len(spec.latitude))*left_boundary_lats[ind]
        spec_save.to_netcdf(save_path+"/boundary_spec_left_"+str(ind)+".nc")
        
    #Save top boundary
    for ind in range(len(top_boundary_lats)):
        spec_save = spec.copy()
        spec_save.longitude[:, 0] = np.ones(len(spec.longitude))*top_boundary_lons[ind]
        spec_save.latitude[:, 0] = np.ones(len(spec.latitude))*top_boundary_lats[ind]
        spec_save.to_netcdf(save_path+"/boundary_spec_top_"+str(ind)+".nc")
    
    #Save right boundary    
    for ind in range(len(right_boundary_lats)):
        spec_save = spec.copy()
        spec_save.longitude[:, 0] = np.ones(len(spec.longitude))*right_boundary_lons[ind]
        spec_save.latitude[:, 0] = np.ones(len(spec.latitude))*right_boundary_lats[ind]
        spec_save.to_netcdf(save_path+"/boundary_spec_right_"+str(ind)+".nc")

    #Save bottom boundary
    for ind in range(len(bottom_boundary_lats)):
        spec_save = spec.copy()
        spec_save.longitude[:, 0] = np.ones(len(spec.longitude))*bottom_boundary_lons[ind]
        spec_save.latitude[:, 0] = np.ones(len(spec.latitude))*bottom_boundary_lats[ind]
        spec_save.to_netcdf(save_path+"/boundary_spec_bottom_"+str(ind)+".nc")

    
    return(1)
