import numpy as np


def orbit_width(state):
    """
    Measure the width of a particle orbit projection in the RZ plane
    
    Parameters
    ----------
    state : OdeResult
        Solution object from solve_ivp

    Returns
    -------
    width : scalar
        Measured orbit width in meters
    """

    x,y = state.y[0:2] # extract Cartesian positions [m]
    R = (x**2 + y**2)**0.5 # convert to radial positions [m]

    width = max(R) - min(R) # orbit width [m]

    return width


def classify_analytic_orbit(tokamak,theta,v0,CONST):
    """
    Determine the analytic orbit classification under a given set of parameters

    Parameters
    ----------
    tokamak : Tokamak object
        Magnetic field object for a tokamak

    theta : scalar
        Particle pitch angle in radians

    v0 : scalar
        Initial particle speed in meters per second

    CONST : named tuple, shape (2,)
        Named tuple containing the physical constants q (proton charge) in Coulombs and m (proton mass) in kilograms
        
    Returns
    -------
    orbit_class : scalar
        Value denoting the classification of a particle orbit
        orbit_class = 1 for passing orbits
        orbit_class = 0 for trapped orbits
    """
        
    v0_perp = v0*np.sin(theta) # perpendicular velocity [m/s]
    mu = (CONST.m * v0_perp**2) / (2 * tokamak.B0) # magnetic moment [A*m^2]
    KE = 0.5 * CONST.m * v0**2 # particle kinetic energy [J]
    gamma = mu * tokamak.B0 / KE # constant of motion

    if gamma < (1 - tokamak.epsilon):
        orbit_class = 1 # set orbit_class to 1 for passing orbits
    else: # if gamma <= (1 + tokamak.epsilon)
        orbit_class = 0 # set orbit class to 0 for trapped orbits
    
    return orbit_class



def classify_sim_orbit(state):
    """
    Classify what type of orbit a simulated particle is in

    Parameters
    ----------
    state : OdeResult
        Solution object from solve_ivp

    Returns
    -------
    orbit_class : scalar
        Value denoting the classification of a particle orbit
        orbit_class = 1 for passing orbits
        orbit_class = 0 for trapped orbits
    """
    
    x,y,z = state.y[0:3] # extract Cartesian positions [m]
    R = (x**2 + y**2)**0.5 # convert to radial positions [m]

    R_span = max(R) - min(R) # radial position span
    z_span = max(z) - min(z) # z position span

    tol = 5 # allowable percent tolerance for difference in R and z span for passing orbits

    if abs(R_span - z_span) / z_span * 100 < tol:
        orbit_class = 1 # set orbit_class to 1 for passing orbits
    else:
        orbit_class = 0 # set orbit_class to 0 for trapped orbits
    
    return orbit_class
    
