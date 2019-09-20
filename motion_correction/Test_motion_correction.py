

import numpy as np
import caiman_motion_correction as mc


def test_motion_correction():
    fnames = '/home/jian/caiman_data/example_movies/Sue_2x_3000_40_-46.tif'
    images = mc.piecewise_rigid_registration(fnames)
    print(images.shape)

def test_high_pass_filtering():
    filepath = '/home/jian/Dropbox/LiamPaninski/locaNMF.git/locanmf/cnmfe_init_output.npz'
    data = np.load(filepath)
    print(data.files)
    U = data['arr_0']
    V = data['arr_1']
    # A = data['arr_2']
    # X = data['arr_3']
    # d1, d2, T, r = data['arr_4']
    # print(d1, d2, r, T)

    Y = np.matmul(U, V)
    Yh = mc.high_pass_filtering(Y)




if __name__ == '__main__':
    # test_motion_correction()
    test_high_pass_filtering()