"""
Dedalus script for Two fluid dust settling in a protoplanetary disc

"""
import numpy as np
import time
import h5py
from mpi4py import MPI
import dedalus.public as de
import logging
import math

from dedalus.extras import flow_tools
from pylab import*
from random import*
import os
import pathlib

rcParams['figure.figsize'] = 64,64

root = logging.root
for h in root.handlers:
    h.setLevel("INFO")
    
logger = logging.getLogger(__name__)

#Aspect ratio 2
Lx, Lz = (1.0, 1.0)
nx, nz = ($00,$01)

# Create bases and domain
x_basis = de.Fourier('x', nx, interval=(0, Lx), dealias=3/2)
z_basis = de.Chebyshev('z',nz, interval=(-Lz/2, Lz/2), dealias=3/2)
domain = de.Domain([x_basis, z_basis], grid_dtype=np.float64)

#Filters out higher oriders of the gaussian function
def filter_field(field,frac=0.5):
    dom = field.domain
    local_slice = dom.dist.coeff_layout.slices(scales=dom.dealias)
    coeff = []
    for i in range(dom.dim)[::-1]:
        coeff.append(np.linspace(0,1,dom.global_coeff_shape[i],endpoint=False))
    cc = np.meshgrid(*coeff)
        
    field_filter = np.zeros(dom.local_coeff_shape,dtype='bool')
    for i in range(dom.dim):
        field_filter = field_filter | (cc[i][local_slice] > frac)
    field['c'][field_filter] = 0j

#Disc Background Density
def Density(*args):
    Lambda2 = args[0].value
    z       = args[1].data
    ans     = - 0.5*z**2
    return ans

def Dense(*args, domain=domain, D=Density):
    return de.operators.GeneralFunction(domain, layout='g', func=D, args=args )

de.operators.parseables['logRho'] = Dense

#Disc Background Density
def Stoke(*args):
    Lambda2 = args[0].value
    z       = args[1].data
    ans     = exp(-0.0*Lambda2*z**2)
    return ans

def Stokes(*args, domain=domain, D=Stoke):
    return de.operators.GeneralFunction(domain, layout='g', func=D, args=args)

de.operators.parseables['St'] = Stokes

# Set problem variables
problem = de.IVP(domain, variables=['p','u','v','w','uz','vz','wz','ud','vd','wd','udz','vdz','wdz','bd','bdz'])

# Set problem parameters
Reynolds = $03
Schmidt  = $04
shear    = $05
St0      = $06
Lambda   = $07
Lambda2  = Lambda*Lambda
bd0      = $08
eta      = $09
St0      = St0/Lambda
problem.parameters['R']       = Reynolds
problem.parameters['F']       = F = Reynolds*Schmidt
problem.parameters['q']       = shear
problem.parameters['St0']     = St0
problem.parameters['Lambda']  = Lambda
problem.parameters['Lambda2'] = Lambda2
problem.parameters['bd0']     = bd0
problem.parameters['eta']     = eta
problem.parameters['Lx']      = Lx

# Incompressible Shearing-Box
#(Gas)
problem.add_equation("dx(u) + wz = -w*dz(logRho(Lambda2,z))")
problem.add_equation("dt(u) + dx(p) - R*(dx(dx(u)) + dz(uz)) = + 2*(v+eta)*Lambda                   - u*dx(u) - w*uz + bd*(ud-u)/(St0*exp(-0.0*z**2))")
problem.add_equation("dt(v)         - R*(dx(dx(v)) + dz(vz)) = - (2-q)*u*Lambda                     - u*dx(v) - w*vz + bd*(vd-v)/(St0*exp(-0.0*z**2))")
problem.add_equation("dt(w) + dz(p) - R*(dx(dx(w)) + dz(wz)) = -p*dz(logRho(Lambda2,z)) - Lambda2*z - u*dx(w) - w*wz + bd*(wd-w)/(St0*exp(-0.0*z**2))")
#(Dust)
problem.add_equation("dt(bd) - F*(dx(dx(bd)) + dz(bdz)) = - bd*(dx(ud) + wdz) - ud*dx(bd) - wd*bdz")
problem.add_equation("dt(ud) - R*(dx(dx(ud)) + dz(udz)) = + 2*vd*Lambda                   - ud*dx(ud) - wd*udz - (ud-u)/(St0*exp(-0.0*z**2))")
problem.add_equation("dt(vd) - R*(dx(dx(vd)) + dz(vdz)) = -(2-q)*ud*Lambda                - ud*dx(vd) - wd*vdz - (vd-v)/(St0*exp(-0.0*z**2))")
problem.add_equation("dt(wd) - R*(dx(dx(wd)) + dz(wdz)) = - Lambda2*z                     - ud*dx(wd) - wd*wdz - (wd-w)/(St0*exp(-0.0*z**2))")

problem.add_equation("uz  - dz(u)  = 0")
problem.add_equation("vz  - dz(v)  = 0")
problem.add_equation("wz  - dz(w)  = 0")
problem.add_equation("bdz - dz(bd) = 0")
problem.add_equation("udz - dz(ud) = 0")
problem.add_equation("vdz - dz(vd) = 0")
problem.add_equation("wdz - dz(wd) = 0")

# Boundary conditions
#(Gas)
problem.add_bc("left(uz)     = 0")
problem.add_bc("right(uz)    = 0")
problem.add_bc("left(vz)     = 0")
problem.add_bc("right(vz)    = 0")
problem.add_bc("left(w)      = 0")
problem.add_bc("right(w)     = 0", condition="(nx != 0)")
problem.add_bc("integ(p,'z') = 0", condition="(nx == 0)")
#(Dust)
problem.add_bc("left(udz)    = 0")
problem.add_bc("right(udz)   = 0")
problem.add_bc("left(vdz)    = 0")
problem.add_bc("right(vdz)   = 0")
problem.add_bc("left(bd)     = 0")
problem.add_bc("right(bd)    = 0")
problem.add_bc("left(wd)     = 0")
problem.add_bc("right(wd)    = 0")

# Time-stepping
ts = de.timesteppers.RK443

#IVP
solver =  problem.build_solver(ts)

#Restart Condition
if not pathlib.Path('restart.h5').exists():
    x  = domain.grid(0)
    z  = domain.grid(1)

#(Gas)
    u  = solver.state['u']
    uz = solver.state['uz']
    v  = solver.state['v']
    vz = solver.state['vz']
    w  = solver.state['w']
    wz = solver.state['wz']
    #(Dust)
    ud  = solver.state['ud']
    udz = solver.state['udz']
    vd  = solver.state['vd']
    vdz = solver.state['vdz']
    wd  = solver.state['wd']
    wdz = solver.state['wdz']
    bd  = solver.state['bd']
    bdz = solver.state['bdz']

    #Initial conditions
    #(Random perturbations, initialized globally for same results in parallel)
    gshape = domain.dist.grid_layout.global_shape(scales=1)
    slices = domain.dist.grid_layout.slices(scales=1)
    rand   = np.random.RandomState(seed=23)
    noise  = rand.standard_normal(gshape)[slices]
    zb, zt = z_basis.interval
    pert   = 1e2 * noise * (zt - z) * (z - zb)
    amp    = 5e-3
    a      = 0.5
    kx     = 1.0
    kz     = 3.0

    #(Gas)
    u['g'] = (1 + amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz))*2*bd0*St0*np.exp(-0.5*z**2)*eta/((1+bd0)**2+(St0*exp(-0.5*z**2))**2)
    v['g'] = (1 + amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz))*(bd0*(1+bd0)/((1+bd0)**2+(St0*exp(-0.5*z**2))**2)-1)*eta 
    #u['g'] = (1 + amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz))*2*bd0*St0*eta/((1+bd0)**2 + St0**2)
    #v['g'] = (1 + amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz))*(bd0*(1+bd0)/((1+bd0)**2  + St0**2)-1)*eta 
    #u['g'] = amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz)
    #v['g'] = amp*np.cos(2.0*np.pi*kx*x/Lx)*np.cos(2.0*np.pi*kz*z/Lz)
    w['g'] = 0.0
    
    #(Dust)
    ud['g'] = -2*St0*eta/((1+bd0)**2 + St0**2)
    vd['g'] = -(1+bd0)*eta/((1+bd0)**2 + St0**2)
    #ud['g'] = 0
    #vd['g'] = 0
    wd['g'] = 0
    bd['g'] = bd0*(1+0.1*pert)*(1-0.99*np.tanh(abs(z/a)))
    filter_field(bd)

    #(Gas)
    u.differentiate('z',out=uz)
    v.differentiate('z',out=vz)
    w.differentiate('z',out=wz)

    #(Dust)
    ud.differentiate('z',out=udz)
    vd.differentiate('z',out=vdz)
    wd.differentiate('z',out=wdz)
    bd.differentiate('z',out=bdz)

    dt = $10
    fh_mode = 'overwrite'

else:
    write, last_dt = solver.load_state('restart.h5', -1)
    dt = last_dt
    fh_mode = 'append'

#Integration parameters and CFL
solver.stop_sim_time  = $02
solver.stop_wall_time = np.inf
solver.stop_iteration = np.inf

initial_dt = 0.02*Lx/nx
#cfl        = flow_tools.CFL(solver,initial_dt=0.01,cadence=10,safety=1.5,max_change=1.0,min_change=0.1,max_dt=0.1)
cfl        = flow_tools.CFL(solver,initial_dt=0.01,safety=1.5,max_change=1.0,min_change=0.1,max_dt=0.1)
cfl.add_velocities(('u','w'))
cfl.add_velocities(('ud','wd'))

# Analysis
snap = solver.evaluator.add_file_handler('snapshots', sim_dt=1.0, max_writes=1)
snap.add_task("bd", scales=1, name='bd')
snap.add_task("bdz", scales=1, name='bdz')

snap.add_task("ud", scales=1, name='ud')
snap.add_task("udz", scales=1, name='udz')

snap.add_task("vd", scales=1, name='vd')
snap.add_task("vdz", scales=1, name='vdz')

snap.add_task("wd", scales=1, name='wd')
snap.add_task("wdz", scales=1, name='wdz')

snap.add_task("p" , scales=1, name='p')

snap.add_task("u" , scales=1, name='u')
snap.add_task("uz" , scales=1, name='uz')

snap.add_task("v", scales=1, name='v')
snap.add_task("vz", scales=1, name='vz')

snap.add_task("w" , scales=1, name='w')
snap.add_task("wz" , scales=1, name='wz')

snap.add_task("dx(bd)*dz(p) - dx(p)*dz(bd)" , scales=1, name='baro')

#Main loop
n = 1
logger.info('Starting loop')
start_time = time.time()
while solver.ok:
    dt = cfl.compute_dt()
    solver.step(dt)
    if solver.iteration % 10 == 0:
       logger.info('Iteration: %i, Time: %e, dt: %e' %(solver.iteration, solver.sim_time, dt))
end_time = time.time()

# Print statistics
logger.info('Run time: %f' %(end_time-start_time))
logger.info('Iterations: %i' %solver.iteration)
