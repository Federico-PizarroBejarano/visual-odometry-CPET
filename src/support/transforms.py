import numpy as np
from scipy.spatial.transform import Rotation as R


def transform_robot_to_camera(Erobot):
    TR_O = np.zeros((4, 4))
    TR_O[0:3, [3]] = np.array([[0.236, -0.129, 0.845]]).T 
    TR_O[0:3, 0:3] = R.from_quat([-0.630,-0.321,0.321,0.630]).as_matrix()
    TR_O[3, 3] = 1

    TO_4 = np.zeros((4, 4))
    TO_4[0:3, [3]] = np.array([[0.030, 0.013, -0.046]]).T 
    TO_4[0:3, 0:3] = R.from_quat([0.006, 0.950, -0.002, 0.311]).as_matrix()
    TO_4[3, 3] = 1

    TR_4 = TR_O @ TO_4
    
    T_R = hpose_from_epose(Erobot)
    T_4 = T_R @ TR_4

    return epose_from_hpose(T_4)


def transform_camera_to_robot(Ecamera):
    TR_O = np.zeros((4, 4))
    TR_O[0:3, [3]] = np.array([[0.236, -0.129, 0.845]]).T 
    TR_O[0:3, 0:3] = R.from_quat([-0.630,-0.321,0.321,0.630]).as_matrix()
    TR_O[3, 3] = 1

    TO_4 = np.zeros((4, 4))
    TO_4[0:3, [3]] = np.array([[0.030, 0.013, -0.046]]).T 
    TO_4[0:3, 0:3] = R.from_quat([0.006, 0.950, -0.002, 0.311]).as_matrix()
    TO_4[3, 3] = 1

    TR_4 = TR_O @ TO_4
    T4_R = np.linalg.inv(TR_4)

    T_4 = hpose_from_epose(Ecamera)
    T_R = T_4 @ T4_R

    return epose_from_hpose(T_R)
    

def epose_from_hpose(T):
    """Covert 4x4 homogeneous pose matrix to x, y, z, roll, pitch, yaw."""
    E = np.zeros((6, 1))
    E[0:3] = np.reshape(T[0:3, 3], (3, 1))
    E[3:6] = rpy_from_dcm(T[0:3, 0:3])
  
    return E

def hpose_from_epose(E):
    """Covert x, y, z, roll, pitch, yaw to 4x4 homogeneous pose matrix."""
    T = np.zeros((4, 4))
    T[0:3, 0:3] = dcm_from_rpy(E[3:6])
    T[0:3, 3] = np.reshape(E[0:3], (3,))
    T[3, 3] = 1
  
    return T

def dcm_from_rpy(rpy):
    """
    Rotation matrix from roll, pitch, yaw Euler angles.

    The function produces a 3x3 orthonormal rotation matrix R
    from the vector rpy containing roll angle r, pitch angle p, and yaw angle
    y.  All angles are specified in radians.  We use the aerospace convention
    here (see descriptions below).  Note that roll, pitch and yaw angles are
    also often denoted by phi, theta, and psi (respectively).

    The angles are applied in the following order:

     1.  Yaw   -> by angle 'y' in the local (body-attached) frame.
     2.  Pitch -> by angle 'p' in the local frame.
     3.  Roll  -> by angle 'r' in the local frame.  

    Note that this is exactly equivalent to the following fixed-axis
    sequence:

     1.  Roll  -> by angle 'r' in the fixed frame.
     2.  Pitch -> by angle 'p' in the fixed frame.
     3.  Yaw   -> by angle 'y' in the fixed frame.

    Parameters:
    -----------
    rpy  - 3x1 np.array of roll, pitch, yaw Euler angles.

    Returns:
    --------
    R  - 3x3 np.array, orthonormal rotation matrix.
    """
    cr = np.cos(rpy[0]).item()
    sr = np.sin(rpy[0]).item()
    cp = np.cos(rpy[1]).item()
    sp = np.sin(rpy[1]).item()
    cy = np.cos(rpy[2]).item()
    sy = np.sin(rpy[2]).item()

    return np.array([[cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
                     [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
                     [  -sp,            cp*sr,            cp*cr]])


def rpy_from_dcm(R):
    """
    Roll, pitch, yaw Euler angles from rotation matrix.

    The function computes roll, pitch and yaw angles from the
    rotation matrix R. The pitch angle p is constrained to the range
    (-pi/2, pi/2].  The returned angles are in radians.

    Inputs:
    -------
    R  - 3x3 orthonormal rotation matrix.

    Returns:
    --------
    rpy  - 3x1 np.array of roll, pitch, yaw Euler angles.
    """
    rpy = np.zeros((3, 1))

    # Roll.
    rpy[0] = np.arctan2(R[2, 1], R[2, 2])

    # Pitch.
    sp = -R[2, 0]
    cp = np.sqrt(R[0, 0]*R[0, 0] + R[1, 0]*R[1, 0])

    if np.abs(cp) > 1e-15:
      rpy[1] = np.arctan2(sp, cp)
    else:
      # Gimbal lock...
      rpy[1] = np.pi/2
  
      if sp < 0:
        rpy[1] = -rpy[1]

    # Yaw.
    rpy[2] = np.arctan2(R[1, 0], R[0, 0])

    return rpy