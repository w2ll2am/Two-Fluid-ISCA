from dedalus.extras import plot_tools
import numpy as np
import os
import h5py
import matplotlib.pyplot as plt

#Plot settings
dpi    = $00
ext    = '.h5'
outdir = 'plots'
start  = 0
number = 0
lambda1 = 1 # Change lambda to the paramater asigned to you!
if not os.path.exists(outdir):
    os.mkdir(outdir)

#Plot all data
all_files = os.listdir("snapshots/")
for files in all_files:
    if (files[-3:] == ext):
        filenumber = files[files.find("_s")+2:files.find(".")]
        print("Plotting " + files)
        #Read data
        number = number + 1
        existing = outdir + '/' + 'plot{:04d}'.format(int(filenumber)+start) + '.png'
        print(existing)
        if not os.path.isfile(existing) and number%1 == 0:
            #Read data
            file     = h5py.File("snapshots/"+files,"r")
            x        = file['scales/x/1']
            y        = file['scales/z/1']
            x,y      = plot_tools.quad_mesh(x,y)
            s        = file['tasks/bd']
            time = file['scales/sim_time'][0]
            
            #Plot data	
            cmap    = plt.get_cmap('$01') 
            fig     = plt.figure(figsize=(24,24))
            plt.gca().set_aspect('equal', adjustable='box')
            fig.suptitle("t = {:4.3f}$T_0$".format((lambda1*0.5*time/np.pi)), fontsize=24)
            # plt.pcolormesh(x,y,s[0].T, cmap=cmap, vmin=0.01, vmax=3.0)
            # im = plt.pcolormesh(x,y,s[0].T, cmap=cmap,  vmin=0.01, vmax=3.0)
            plt.pcolormesh(x,y,s[0].T, cmap=cmap)
            im = plt.pcolormesh(x,y,s[0].T, cmap=cmap)
            cb = plt.colorbar(im,shrink=0.8)
            cb.ax.tick_params(labelsize=30)
            cb.set_label('Dust to gas ratio', rotation=270, labelpad=100, fontsize=50)
            #Save the plot
            #plt.axis('off')
            plt.xticks(fontsize=25)
            plt.yticks(fontsize=25)
            plt.xlabel('', fontsize=40)
            plt.ylabel('', fontsize=40)
            fig.savefig(outdir + '/' + 'plot{:04d}'.format(int(filenumber)+start), dpi=dpi)
            plt.close(fig)
