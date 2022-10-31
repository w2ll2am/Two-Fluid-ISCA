from dedalus.extras import plot_tools
import numpy as np
import os
import h5py
import matplotlib.pyplot as plt
import matplotlib

#Plot settings
dpi    = $00
ext    = '.h5'
outdir = 'plots'
start  = 0
num    = 0
if not os.path.exists(outdir):
    os.mkdir(outdir)

#Plot all data
all_files = sorted(os.listdir("snapshots/"))
for files in all_files:
    if (files[-3:] == ext):
        filenumber = files[files.find("_s")+2:files.find(".")]
        if int(filenumber)%1 == 0:
            print("Plotting " + files)
            
            #Read data
            num = num + 1
            existing = outdir + '/' + 'plot{:04d}'.format(int(filenumber)+start) + '.png'
            print(existing)
            if not os.path.isfile(existing):
                file  = h5py.File("snapshots/"+files,"r")
                x     = file['scales/x/1']
                y     = file['scales/z/1']
                x,y   = plot_tools.quad_mesh(x,y)
                logb  = file['tasks/bd']
                u     = file['tasks/ud']
                v     = file['tasks/vd']
                w     = file['tasks/wd']
                time  = file['scales/sim_time'][0]
                
                #Plot data	
                cmap    = plt.get_cmap('$01') # Can change colour scheme
                fig     = plt.figure(figsize=(24,12))
                lambda1 = 1
                fig.suptitle("t = {:4.3f}$T_0$".format((0.5*lambda1/np.pi)*time), fontsize=24)
                
                ax1 = fig.add_subplot(222)
#                 ax1.pcolormesh(x,y,logb[0].T, cmap=cmap, vmin=0.01, vmax=3)
#                 im = ax1.pcolormesh(x,y,logb[0].T, cmap=cmap, vmin=0.01, vmax=3)
                ax1.pcolormesh(x,y,logb[0].T, cmap=cmap)
                im = ax1.pcolormesh(x,y,logb[0].T, cmap=cmap)
                
                cb = plt.colorbar(im,shrink=0.75,format='%.1f')
                cb.ax.tick_params(labelsize=20)
                cb.set_label('Density / $kgm^{-3}$',labelpad=40,fontsize=25, rotation=270)
                ax1.set_xticks([])
                ax1.set_yticks([])
                
                ax2 = fig.add_subplot(224)
                ax2.pcolormesh(x,y,u[0].T, cmap=cmap)
                im = ax2.pcolormesh(x,y,u[0].T, cmap=cmap)
                cb = plt.colorbar(im,shrink=0.75,format='%.0e')
                cb.ax.tick_params(labelsize=20)
                cb.set_label('$u$', rotation=0,labelpad=40, fontsize=40)
                ax2.set_xticks([])
                ax2.set_yticks([])
                
                ax3 = fig.add_subplot(221)
                ax3.pcolormesh(x,y,v[0].T*10e3, cmap=cmap)
                im = ax3.pcolormesh(x,y,v[0].T*10e3, cmap=cmap)
                cb = plt.colorbar(im,shrink=0.75, format='%.0f')
                cb.ax.tick_params(labelsize=20)
                cb.set_label('Radial Velocity / $ms^{-1}$', rotation=270,labelpad=40, fontsize=25)
                ax3.set_xticks([])
                ax3.set_yticks([])
                
                ax4 = fig.add_subplot(223)
                ax4.pcolormesh(x,y,w[0].T, cmap=cmap)
                im = ax4.pcolormesh(x,y,w[0].T, cmap=cmap)
                cb = plt.colorbar(im,shrink=0.75,format='%.0e')
                cb.ax.tick_params(labelsize=20)
                cb.set_label('$w$', rotation=0,labelpad=40, fontsize=40)
                ax4.set_xticks([])
                ax4.set_yticks([])
                
                #Save the plot
                #fig.tight_layout()
                #plt.subplots_adjust(left=-0.5, bottom=0, right=1, top=1, wspace=-0.6, hspace=-0.45)
                #plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
                fig.savefig(outdir + '/' + 'plot{:04d}'.format(int(filenumber)+start), dpi=dpi)
                plt.close(fig)
