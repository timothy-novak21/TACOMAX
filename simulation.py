import numpy as np
import scipy.integrate as integrate

from physics.lorentz import accel
from analysis.plotting import plot_pitch_sweep
from physics.adiabaticity import invariance_check

def single_sim(mirror,theta,v0,t_span,CONST):
    """
    Run a single particle magnetic mirror simulation

    Parameters
    ----------
    mirror : Mirror object
        Magnetic mirror object belonging to the Mirror class stored in B_field.py

    theta : scalar
        Particle pitch angle in radians

    v0 : scalar
        Initial particle speed in meters per second

    t_span : array, shape (2,)
        Integration time bounds in seconds

    CONST : named tuple, shape (2,)
        Named tuple containing the physical constants q (proton charge) in Coulombs and m (proton mass) in kilograms
        
    Returns
    -------
    state : OdeResult
        Solution object from solve_ivp. state.t_events[0] == 1 indicates particle escape
        state.t_events[1] == 1 indicates particle was reflected and remained in the mirror
    """

    # Initial conditions
    v0_perp = v0 * np.sin(theta) # initial particle velocity perpendicular to B field [m/s]
    v0_par = v0 * np.cos(theta) # initial particle velocity parallel to B field [m/s]

    # Package inital state vector
    state0 = [0.0, 0.0, 0.0, # initial position [m]
              v0_perp, 0.0, v0_par] # initial velocity [m/s]
    
    # Integration time conditions
    omega_c = CONST.q * mirror.Bmax / CONST.m # cyclotron angular frequency [rad/s]
    T_cyclotron = 2 * np.pi / omega_c # cyclotron period [s]
    max_step = T_cyclotron / 200 # 200 steps per gyration for max timestep [s]

    # Define event to terminate solver if particle escapes mirror
    def escaped(t,state,mirror,CONST):
        return abs(state[2]) - mirror.length # particle crosses when z is at either mirror boundary

    escaped.terminal = True # stop integration upon escape
    escaped.direction = 1 # stop integration when moving outward

    # Define event to terminate solver if particle is reflected (v_par = 0)
    def reflected(t,state,mirror,CONST):
        return state[5] # particles reflects when v_par changes sign
    
    reflected.terminal = True # stop integration if particle velocity changes sign
    reflected.direction = -1 # stop integration when v_par crosses zero going negative
    
    # Solve ODE
    state = integrate.solve_ivp(accel, t_span, state0,
                                method="RK45", max_step=max_step,
                                rtol=1e-10, atol=1e-12,
                                args=(mirror,CONST),
                                events=[escaped,reflected])
    
    return state

def sim_pitch_sweep(mirror,v0,t_span,N,CONST):
    theta = np.linspace(np.radians(1), np.radians(89), N) # particle pitch angle [rad]
    esc = np.zeros(len(theta)) # initialize an array to track which pitch angles escape

    [epsilon,invariant] = invariance_check(v0,mirror,CONST) # adiabaticity condition for given mirror and v0

    # Run simulations
    for i in range(0,len(theta)):
        print(f"Running simulation {i+1}/{N}: theta = {np.degrees(theta[i]):.1f} deg")
        state = single_sim(mirror,theta[i],v0,t_span,CONST)
        esc[i] = len(state.t_events[0]) > 0 # t_events[0] == 1 when particle escapes mirror
        
    # calc simulated critical pitch angle to compare to analytical
    if np.any(esc == 0) and np.any(esc == 1):
        high_esc = theta[esc == 1][-1]
        low_ref = theta[esc == 0][0]
        theta_c_sim = np.degrees((high_esc + low_ref) / 2)
    else:
        print("Warnign: no clean transition found in sweep")
        theta_c_sim = None

    # Print adiabaticity condition
    if invariant == True:
        print(f"Adiabatically Invariant, Epsilon = {epsilon:.3f}")
    else:
        print(f"Not Adiabatically Invariant, Epsilon = {epsilon:.3f}")

    # plot_pitch_sweep(theta,esc,mirror)
    return theta_c_sim