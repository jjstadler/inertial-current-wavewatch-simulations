
# inertial-current-wavewatch-simulations

This repository contains all the necessary code for running a series of idealied WaveWatchIII models to test the impacts of inertial currents on surface waves. The repository is broken up into 3 directories, each with its own purpose. The _Modeling_ directory contains code and files necessary to run a series of WaveWatchIII models forced by idealized current to investigate the impacts of the time variance of inertial currents on wave heights. The _Analysis_ directory contains python notebooks for generating figures to analyze the output of the wave models. The _src_ directory contains helper functions called by files in the other two directories.

Imapct of inertial period on Significant Wave Height (Hs) modulation:

https://github.com/user-attachments/assets/575890c5-62e4-4531-9e93-3f508f035e8f 

### Modeling

This directory contains all the necessary files for running a sereis of wave models to test the impact of inertial period (Ti), peak wave period (Tp), current speed (U), and current length scale (L).

Modify the files _makeSteadyCurrents.ipynb_ and _makeSteadyWaveForcing.ipynb_ to choose your desired model parameters and generate the necessary current and boundary condition files. The naming conventions are such that the generated current files are named: `equator_currents_{L}_{Ti}_{U}.nc`. For example, for currents with a speed of U=0.5m/s, L=200km, and inertial period Ti=16 hours, the resulting current file would be:

`equator_currents_200_16_05.nc`

In order to run the model, activate a docker environment, either by building from the Dockerfile provided, or pulling from my docker repository: 

docker://stadlerj/wavewatch3:1.0.0






