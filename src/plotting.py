#!/usr/bin/env python3
from operator import rshift
import matplotlib.pyplot as plt
import numpy as np
from functions import orbit_RZ, orbit_3D
import mpl_toolkits.mplot3d.axes3d as p3
import time
from scipy.interpolate import UnivariateSpline as spline
from pathlib import Path
import os
from matplotlib import cm
import matplotlib.animation as animation

def make_plots(result, name, stel,r0,nstep,ncores,Animation,SaveMovie,ntheta,nphi,p_phi_error,boundaryR0):
    Path('results/').mkdir(parents=True, exist_ok=True)
    Path('results/'+name).mkdir(parents=True, exist_ok=True)
    os.chdir('results/'+name)

    fig=plt.figure(figsize=(10,6))
    plt.subplot(1, 2, 1)
    # Plot radial particle orbits
    [plt.plot(res[0],res[1]) for res in result]
    plt.xlabel('Time')
    plt.ylabel('r')

    plt.subplot(1, 2, 2)
    # Plot orbits and stellarator in the (R,Z) plane
    xParticleVec,yParticleVec,rParticleVec,zParticleVec,phiParticleVec,rSurf,zSurf,phiCylindrical=orbit_RZ(stel,result,boundaryR0,nstep,ncores)
    plt.savefig('orbit_rz_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('p_phi log10 error')
    [plt.plot(res[0][3::],p_phi_error[count][3::]) for count, res in enumerate(result)]
    plt.savefig('p_phi_error_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('Energy')
    [plt.plot(res[0],res[4]) for res in result]
    plt.savefig('energy_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('p_phi')
    [plt.plot(res[0],res[9]) for res in result]
    plt.savefig('p_phi_'+name+'.pdf')

    def B20(phi):
        sp=spline(stel.varphi, stel.B20, k=3, s=0)
        return sp(np.mod(phi,2*np.pi/stel.nfp))
        
    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('Relative error (Bfield Theory vs Gyronimo)')
    [plt.plot(res[0],abs(stel.B0*(1+stel.etabar*res[1]*np.cos(res[2]))+res[1]*res[1]*(B20(res[3])+stel.B2c*np.cos(2*res[2])+stel.B2s*np.sin(2*res[2]))-res[15])/res[15]) for res in result]
    plt.savefig('Bfield_comp_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Bfield Theory')
    plt.ylabel('Bfield Gyronimo')
    [plt.plot(stel.B0*(1+stel.etabar*res[1]*np.cos(res[2]))+res[1]*res[1]*(B20(res[3])+stel.B2c*np.cos(2*res[2])+stel.B2s*np.sin(2*res[2])),res[15]) for res in result]
    plt.savefig('Bfield_comp2_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('phi')
    [plt.plot(res[0],res[3]) for res in result]
    plt.savefig('phi_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('theta')
    [plt.plot(res[0],res[2]) for res in result]
    plt.savefig('theta_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('v_parallel')
    [plt.plot(res[0],res[14]) for res in result]
    plt.savefig('v_parallel_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('Bfield')
    [plt.plot(res[0],res[15]) for res in result]
    plt.savefig('Bfield_'+name+'.pdf')

    plt.figure()
    plt.xlabel('r')
    plt.ylabel('Bfield')
    [plt.plot(res[1],res[15]) for res in result]
    plt.savefig('Bfield_vs_r_'+name+'.pdf')

    plt.figure()
    plt.xlabel('r')
    plt.ylabel('p_phi')
    [plt.plot(res[1],res[9]) for res in result]
    plt.savefig('p_phi_vs_r_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('v_parallel dot')
    [plt.plot(res[0],res[13]) for res in result]
    plt.savefig('v_parallel_dot_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('phi dot')
    [plt.plot(res[0],res[12]) for res in result]
    plt.savefig('phi_dot_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('theta dot')
    [plt.plot(res[0],res[11]) for res in result]
    plt.savefig('theta_dot_'+name+'.pdf')

    plt.figure()
    plt.xlabel('Time')
    plt.ylabel('r dot')
    [plt.plot(res[0],res[10]) for res in result]
    plt.savefig('r_dot_'+name+'.pdf')

    fig = plt.figure(figsize=(6.5,6))
    ax = plt.axes(projection='3d')
    # Plot orbits and stellarator in 3D
    Xsurf, Ysurf, Zsurf, B_rescaled = orbit_3D(stel,boundaryR0,xParticleVec,yParticleVec,zParticleVec,rSurf,zSurf,ntheta,nphi,ax)
    plt.savefig('orbit_3D'+name+'.pdf')

    if Animation==1:
        fig = plt.figure(frameon=False)
        fig.set_size_inches(9,9)
        ax = p3.Axes3D(fig)
        # Create animation with orbits
        orbitLength=5 # number of points to display in each frame
        ani = orbit_3D_animation(Xsurf,Ysurf,Zsurf,B_rescaled,fig,ax,xParticleVec,yParticleVec,zParticleVec,orbitLength)
        if SaveMovie==1:
            print('Saving movie')
            start_time = time.time()
            ani.save('particle_Orbit_'+name+'.mp4', fps=30, dpi=300, codec="libx264", bitrate=-1, extra_args=['-pix_fmt', 'yuv420p'])
            print("--- %s seconds ---" % (time.time() - start_time))
    
    os.chdir("..")
    os.chdir("..")

    return rParticleVec,zParticleVec,phiParticleVec,rSurf,zSurf,phiCylindrical


def orbit_3D_animation(Xsurf,Ysurf,Zsurf,B_rescaled,fig,ax,xParticleVec,yParticleVec,zParticleVec,orbitLength):
    print("---------------------------------")
    print("Animation of particle orbits in 3D")
    start_time = time.time()
    ax.plot_surface(Xsurf, Ysurf, Zsurf, facecolors = cm.jet(B_rescaled), rstride=1, cstride=1, antialiased=False, linewidth=0, alpha=0.15)
    ax.auto_scale_xyz([Xsurf.min(), Xsurf.max()], [Xsurf.min(), Xsurf.max()], [Xsurf.min(), Xsurf.max()])  
    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.set_axis_off()
    ax.dist = 6.5

    ani = []
    def update(num, data, line):
        # line.set_data(data[:2, max(0,num-orbitLength):num])
        line.set_data(data[:2, 0:num])
        # line.set_3d_properties(data[2, max(0,num-orbitLength):num])
        line.set_3d_properties(data[2, 0:num])
    
    def update_all(num, data, line):
        for i in range(len(data)):
            dat  = data[i]
            lin, = line[i]
            update(num,dat,lin)

    data  = [np.array([xParticleVec[i],yParticleVec[i],zParticleVec[i]]) for i in range(len(xParticleVec))]
    lines = [ax.plot(xParticleVec[i][0:1], yParticleVec[i][0:1], zParticleVec[i][0:1]) for i in range(len(xParticleVec))]
    ani   = animation.FuncAnimation(fig, update_all, len(xParticleVec[0]), fargs=(data, lines), interval=0, blit=False)
    print("--- %s seconds ---" % (time.time() - start_time))
    return ani