# TODO: Create this list dynamically and define properties
# TODO: Improve DREF index
# TODO: Implement some value checking in the case it can be overriden
# TODO: Auto turn on or off aerodynamics, engine torques... (all overrides) depending on what is required by the user


class DREFs:
    AoA = 'sim/flightmodel/position/alpha'
    side_force = 'sim/flightmodel/forces/fside_aero'
    lift_force = 'sim/flightmodel/forces/fnrml_aero'
    override_aero = 'sim/operation/override/override_wing_forces'
    pitch_moment = 'sim/flightmodel/forces/M_aero'
    override_torque = 'sim/operation/override/override_torque_forces'
    engine_torque = 'sim/flightmodel/engine/ENGN_TRQ'
    aero_roll_moment = 'sim/flightmodel/forces/L_aero'
    aero_pitch_moment = 'sim/flightmodel/forces/M_aero'
    aero_yaw_moment = 'sim/flightmodel/forces/N_aero'
    yoke_pitch = 'sim/joystick/yoke_pitch_ratio'
    yoke_roll = 'sim/joystick/yoke_roll_ratio'
    yoke_yaw = 'sim/joystick/yoke_heading_ratio'
    TAS = 'sim/flightmodel/position/true_airspeed'
    right_aileron = 'sim/flightmodel/controls/rail1def'
    left_aileron = 'sim/flightmodel/controls/lail1def'
    elevator_angle = 'sim/flightmodel/controls/elev1_def'

