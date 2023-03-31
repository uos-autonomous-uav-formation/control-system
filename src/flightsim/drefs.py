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
    lat = "sim/flightmodel/position/latitude"
    long = "sim/flightmodel/position/longitude"
    alt = "sim/flightmodel/position/elevation"  # elevation above MSL
    cs_roll = "sim/joystick/yolk_roll_ratio"
    cs_hdg = "sim/joystick/yolk_heading_ratio"
    cs_pitch = "sim/joystick/yolk_pitch_ratio"

    # The following values are with respect to the ground below
    true_heading = "sim/flightmodel/position/true_psi"
    true_roll = "sim/flightmodel/position/true_phi"
    true_pitch = "sim/flightmodel/position/true_theta"

    class grafics:
        openglref_lat: str = "sim/flightmodel/position/lat_ref"
        openglref_lon: str = "sim/flightmodel/position/lon_ref"
        opengl_x: str = "sim/flightmodel/position/local_x"
        opengl_y: str = "sim/flightmodel/position/local_y"
        opengl_z: str = "sim/flightmodel/position/local_z"
        opengl_vx: str = "sim/flightmodel/position/local_vx"
        opengl_vy: str = "sim/flightmodel/position/local_vy"
        opengl_vz: str = "sim/flightmodel/position/local_vz"
        opengl_roll: str = "sim/flightmodel/position/phi"
        opengl_pitch: str = "sim/flightmodel/position/theta"  # True pitch
        opengl_hdg: str = "sim/flightmodel/position/psi"  # OpenGL heading

    class multiplayer:
        """
        Up to 19 multiplayer aircraft can be generated using DREFs.

        To avoid having a string for each aircraft, formatting is taken advantage off. To modify DREF for a aircraft
        with id i use:

        ```multiplayer.[DREF].format(i)```
        """
        lon = "sim/multiplayer/position/plane1_lon"
        lat = "sim/multiplayer/position/plane1_lat"
        elev = "sim/multiplayer/position/plane1_el"
        opengl_x: str = "sim/multiplayer/position/plane{0}_x"
        opengl_vx: str = "sim/multiplayer/position/plane{0}_v_x"
        opengl_y: str = "sim/multiplayer/position/plane{0}_y"
        opengl_vy: str = "sim/multiplayer/position/plane{0}_v_y"
        opengl_z: str = "sim/multiplayer/position/plane{0}_z"
        opengl_vz: str = "sim/multiplayer/position/plane{0}_v_z"
        opengl_pitch: str = "sim/multiplayer/position/plane{0}_the"
        opengl_roll: str = "sim/multiplayer/position/plane{0}_phi"
        opengl_hdg: str = "sim/multiplayer/position/plane{0}_psi"
        flap: str = "sim/multiplayer/controls/flap_request[{0}]"
        cs_pitch: str = "sim/multiplayer/controls/yoke_pitch_ratio[{0}]"
        cs_roll: str = "sim/multiplayer/controls/yoke_roll_ratio[{0}]"
        cs_hdg: str = "sim/multiplayer/controls/yoke_heading_ratio[{0}]"
        engine_throttle = "sim/multiplayer/controls/engine_throttle_request[{0}]"
        engine_mixture = "sim/multiplayer/controls/engine_mixture_request[{0}]"

