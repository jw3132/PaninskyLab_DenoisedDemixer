
import numpy as np

import scipy
from scipy.ndimage import gaussian_filter

import caiman as cm
from caiman.motion_correction import MotionCorrect


def matlab_style_gauss2D(shape=(3,3),sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])

    :param shape: vector tuple contains 2D shape of gaussian filter
    :param sigma: gaussian filter sigma value
    :return: low pass gaussian filter
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h


def high_pass_filtering(Y, sigma=7):
    """
    High pass filtering

    :param Y: raw image data of shape (d1, d2, T)
    :param sigma: gaussian filter sigma value
    :return: high pass filtered image data
    """

    gSig = sigma
    gSize = 3 * gSig
    psf = matlab_style_gauss2D((gSize, gSize), gSig)
    ind_nonzero = psf >= np.amax(psf, 0)
    psf = psf - np.mean(psf[ind_nonzero])
    psf[psf < np.amax(psf, 0)] = 0
    T = Y.shape[2]
    Yh = np.zeros_like(Y)
    for t in range(T):
        Yh[:, :, t] = scipy.ndimage.correlate(Y[:, :, t], psf, mode='mirror')
    return Yh


def piecewise_rigid_registration(fnames,
                                 max_shifts=(6, 6),
                                 strides=(48, 48),
                                 overlaps=(24, 24),
                                 num_frames_split=100,
                                 max_deviation_rigid=3,
                                 pw_rigid=False,
                                 shifts_opencv=True,
                                 border_nan='copy',
                                 highPassFilter='False',
                                 sigma=7):
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
    :param highPassFilter: whether applying high pass filter
    :param sigma: lowpass gaussian filter sigma value

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

    Y = np.array(m_els.tolist())
    if highPassFilter:
        Y = high_pass_filtering(Y.sigma)

    return Y




