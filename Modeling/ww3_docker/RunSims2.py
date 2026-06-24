""""
Automake Runs
"""

import os
import subprocess
from pathlib import Path

#Big set
folders = ["BC_15", "BC_10", "BC_5"] #Boundary Conditions (for different peak frequencies
runs = ["no_cur", "advec", "advec_k", "advec_th", "all_cur"] #Different physics parameters
cur_files=["100_12"]
vels = ["full"] #"div", "rot", or "full"

#modifying f runs





#Need to unlink everything at the start in case there is something linked from a previous crashed run
subprocess.run(["unlink", "ww3_prnc.nml"])
subprocess.run(["unlink", "ww3_grid.nml"])
subprocess.run(["unlink", "ww3_shel.nml"])


def modify_prnc_file(vel, cur_file):
    """
    automate changing the current file names in the ww3_prnc.nml file so we don't need a separate prnc for each current setup
    vel options: ['full', 'rot', 'div']
    """
    #Open file
    with open('ww3_prnc.nml', 'r') as file:
        content = file.read()
    # Modify the content with the correct cur file name
    new_content = content.replace('equator_currents/equator_currents_100_12.nc', 'equator_currents/equator_currents_'+cur_file+'.nc')
    #Write
    with open('ww3_prnc.nml', 'w') as file:
        file.write(new_content)
    return(1)


for bc in folders:
    bc_path = "BCs/"+bc
    with open("spec.list", 'w') as f:
        bc_result = subprocess.check_call(["ls BCs/"+bc+"/*"], shell=True, stdout=f)
    for cur_file in cur_files:
        for vel in vels:
            #modify the prnc file to get the correct file/variable names for model run
            #Copy file with base file name first, then modify copy. Otherwise the modify function doesn't work bc it looks for the wrong string
            cur_result = subprocess.run(["cp", "ww3_prnc_"+vel+".nml", "ww3_prnc.nml"])
            modify_prnc_file(vel, cur_file)

            
            for run in runs:
    
                if run=="no_cur":                
                    grid_result = subprocess.run(["ln", "ww3_grid_all_cur.nml", "ww3_grid.nml"])
                    shel_result = subprocess.run(["ln", "ww3_shel_nocur.nml", "ww3_shel.nml"])
                else:
                    grid_result = subprocess.run(["ln", "ww3_grid_"+run+".nml", "ww3_grid.nml"])
                    shel_result = subprocess.run(["ln", "ww3_shel_cur.nml", "ww3_shel.nml"])
    
                #Make output directories
                #Move the output file to something not generically named
                save_path = "outputs/"+bc
                os.makedirs(save_path, exist_ok=True)
                save_path = save_path +"/"+cur_file+"/"
                os.makedirs(save_path, exist_ok=True)
                save_path_specs = save_path +"/specs/"
                os.makedirs(save_path_specs, exist_ok=True)

                print("checking if already run")
    
                fpath = Path(save_path+run+"_"+vel+".nc")
    
                if fpath.is_file():
                    print("Already Done!", save_path+run+"_"+vel+".nc")
                else:
                    #print("Oops gotta run")
                    print("running "+bc+" with "+cur_file + "km currents and " + run)
                    #Now go through and run everything...
                    ww3_grid = subprocess.run(["/WW3/model/exe/ww3_grid"])
                    ww3_bounc = subprocess.run(["/WW3/model/exe/ww3_bounc"])
                    ww3_prnc = subprocess.run(["/WW3/model/exe/ww3_prnc"])
                    ww3_shel = subprocess.run(["mpiexec", "-n", "40", "/WW3/model/exe/ww3_shel"])
                    ww3_ounf = subprocess.run(["/WW3/model/exe/ww3_ounf"])
                    ww3_ounp = subprocess.run(["/WW3/model/exe/ww3_ounp"])

                    subprocess.run(["rm", "current.ww3"])
                    subprocess.run(["rm", "nest.ww3"])
                    subprocess.run(["rm", "mod_def.ww3"])
                    subprocess.run(["rm", "mod_def.ww3"])
                    subprocess.run(["rm", "out_grd.ww3"])
    
    
                    move_out = subprocess.run(["mv", "ww3.2019.nc", save_path+run+"_"+vel+".nc"])
                    save_path_specs = save_path_specs + "/" + run+"_"+vel + "/"
                    os.makedirs(save_path_specs, exist_ok=True)
                    mv_string = "mv *spec.nc " + save_path_specs
                    move_out = subprocess.run(mv_string, shell=True)

                #unlink run files
                subprocess.run(["unlink", "ww3_grid.nml"])
                subprocess.run(["unlink", "ww3_shel.nml"])
            #Done all phys runs
            #Unlink Current file
            subprocess.run(["rm", "ww3_prnc.nml"])
