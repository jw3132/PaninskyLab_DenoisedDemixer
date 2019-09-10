
import numpy as np

import caiman as cm
from caiman.motion_correction import MotionCorrect


def piecewise_rigid_registration(fnames,
                                 max_shifts=(6, 6),
                                 strides=(48, 48),
                                 overlaps=(24, 24),
                                 num_frames_split=100,
                                 max_deviation_rigid=3,
                                 pw_rigid=False,
                                 shifts_opencv=True,
                                 border_nan='copy'):
    '''Apply CaImAn piecewise rigid registration on raw imaging data

    :param fnames: full path filename for motion correction, possible extensions are tif, avi, npy
    :param max_shifts: maximum allowed rigid shift in pixels (view the movie to get a sense of motion)
    :param strides: create a new patch every x pixels for pw-rigid correction
    :param overlaps: overlap between pathes (size of patch strides+overlaps)
    :param num_frames_split: length in frames of each chunk of the movie (to be processed in parallel)
    :param max_deviation_rigid: maximum deviation allowed for patch with respect to rigid shifts
    :param pw_rigid: flag for performing rigid or piecewise rigid motion correction
    :param shifts_opencv: flag for correcting motion using bicubic interpolation (otherwise FFT interpolation is used)
    :param border_nan: replicate values along the boundary (if True, fill in with NaN)

    :return: motion corrected image in numpy
    '''

    fnames = [fnames]
    m_orig = cm.load_movie_chain(fnames)
    if 'dview' in locals():
        cm.stop_server(dview=dview)
    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local', n_processes=None, single_thread=False)

    # create a motion correction object
    mc = MotionCorrect(fnames, dview=dview, max_shifts=max_shifts,
                       strides=strides, overlaps=overlaps,
                       max_deviation_rigid=max_deviation_rigid,
                       shifts_opencv=shifts_opencv, nonneg_movie=True,
                       border_nan=border_nan)

    # correct for rigid motion correction and save the file (in memory mapped form)
    mc.motion_correct(save_movie=True)

    # load motion corrected movie and apply piece-wise rigid registration
    m_rig = cm.load(mc.mmap_file)
    mc.pw_rigid = True  # turn the flag to True for pw-rigid motion correction
    mc.template = mc.mmap_file  # use the template obtained before to save in computation (optional)
    mc.motion_correct(save_movie=True, template=mc.total_template_rig)
    cm.stop_server(dview=dview)  # stop the server
    m_els = cm.load(mc.fname_tot_els)

    return np.array(m_els.tolist())




