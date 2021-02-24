import os
import cv2
import numpy as np
from numpy.core.einsumfunc import _find_contraction
from scipy import fftpack
from matplotlib import pyplot as plt

class CV:
    def __init__(self, vid_path):
        self.video_feed = cv2.VideoCapture(vid_path)

    # Resize the frame
    @staticmethod
    def resize_frame(img, scale_percent=50):
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    def separate_background(self, filter_size=100):
        # Get frame
        ret, frame = self.video_feed.read()

        if not ret:
            print("Problem reading image")
            return

        def disp_fft(img):
            plt.figure()
            plt.imshow(np.log(1+np.abs(img)).real, "gray") 

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        im_fft = fftpack.fft2(frame)
        im_fft_shift = fftpack.fftshift(im_fft)

        r, c = im_fft_shift.shape
        mask = np.zeros_like(frame)
        cv2.circle(mask, (int(c/2), int(r/2)), filter_size, 255, -1)[0]
        high_pass = np.multiply(im_fft_shift, np.invert(mask))/255

        im_fft_ishift = fftpack.ifftshift(high_pass)
        ifft = np.abs(fftpack.ifft2(im_fft_ishift))

        min_val = np.min(ifft)
        max_val = np.max(ifft)
        gray2uint8 = lambda px: np.uint8(255*(px - min_val)/(max_val-min_val))
        mat = np.asarray(list(map(gray2uint8, ifft)))
        return mat

if __name__ == '__main__':
    os.system('cls')
    K = np.array([[1406.08415449821,                0, 0],
                  [2.20679787308599, 1417.99930662800, 0],
                  [1014.13643417416, 566.347754321696, 1]])

    cv = CV('Tag1.mp4')
    tag = cv.separate_background()
    edges = cv2.Canny(tag, 150, 200)

    cv2.imshow("edges", edges)
    cv2.waitKey(0)