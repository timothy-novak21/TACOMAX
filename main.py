import numpy as np
from collections import namedtuple

from fields.magnetic_mirror import Mirror
from simulation import sim_pitch_sweep
from analysis.plotting import plot_crit_curve

# Constants: q = proton charge [C], m = proton mass [kg]
PhysicalConstants = namedtuple("PhysicalConstants", ["q","m"])
CONST = PhysicalConstants(q=1.602e-19, m=1.673e-27)

# Define mirror
length = 1 # mirror half length [m]
Rm = [1.5, 2, 3, 5, 10] # vector of mirror ratios [-]
Bmax = 0.5 # B field strength at mirror [T]

# Set up list of Mirror objects
mirror_list = []
for i in range(0,len(Rm)):
    temp_mirror = Mirror(length,Rm[i],Bmax) # create mirror object for current Rm
    mirror_list.append(temp_mirror) # add to mirror list

# Initial conditions
KE_eV = 5e3 # physically relevant kinetic energy for a proton in fusion experiments [eV]
v0 = (CONST.q * KE_eV / (0.5 * CONST.m))**0.5 # solve for particle velocity based on desired KE [m/s]
print(f"Initial particle kinetic energy: {KE_eV/1e3:.1f} keV, Initial particle velocity: {v0/1e6:.2f}e6 m/s")

T_ref_est = 4 * length / v0 # estimate reflection period [s] 
t_span = [0,4 * T_ref_est] # integration time bounds [s]

# Setup conditions for pitch angle sweep
N = 500 # number of pitch angles to sweep [-]

# Run pitch sweep for all Rm
theta_c_sim = np.zeros(len(Rm))
for j in range(0,len(mirror_list)):
    print(f"Running sweep {j + 1:.0f}/{len(mirror_list):.0f}")
    theta_c_sim[j] = sim_pitch_sweep(mirror_list[j],v0,t_span,N,CONST) # find simulated critical pitch angle for current mirror/Rm [deg]

#print(f"Simulated Critical Pitch Angle: {theta_c_sim:.2f} deg, Analytical Critical Pitch Angle: {mirror_list[0].theta_c:.2f} deg")
#print(f"Error in Critical Pitch Angle: {abs((mirror_list[0].theta_c - theta_c_sim) / mirror_list[0].theta_c) * 100:.2f}%")

plot_crit_curve(Rm,theta_c_sim)