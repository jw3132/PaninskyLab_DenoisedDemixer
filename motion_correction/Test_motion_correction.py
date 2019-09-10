

import caiman_motion_correction as mc


def test_motion_correction():
    fnames = '/home/jian/caiman_data/example_movies/Sue_2x_3000_40_-46.tif'
    images = mc.piecewise_rigid_registration(fnames)
    print(images.shape)




if __name__ == '__main__':
    test_motion_correction()