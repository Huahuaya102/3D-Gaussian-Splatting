import cv2
import numpy as np
import os
import argparse
import sys

# 高斯滤波图像去噪 + 图像锐化
def denoise_image(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    # 应用高斯滤波去噪
    denoised_image = cv2.GaussianBlur(image, (5, 5), 0)
    # 定义拉普拉斯核
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]], dtype=np.float32)
    # 应用拉普拉斯核进行卷积
    sharpened_image = cv2.filter2D(denoised_image, -1, kernel)
    return sharpened_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Preprocess parameters")
    parser.add_argument('-r', '--rootpath', type=str, default='/home/ubuntu/yjh/gaussian-splatting/data/state_grid_0328/', help='Root path of input images')
    args = parser.parse_args()
    if not os.path.exists(args.rootpath):
        try:
            os.makedirs(args.rootpath)
            print("Path created successfully!")
        except FileExistsError:
            print(" Path was created by another process during the creation.")
        except PermissionError:
            print(" Permission denied to create the path.")
        except Exception as e:
            print(" An error occurred while creating the path:", e)
    filenames = os.listdir(args.rootpath)
    for filename in filenames:
        imagepath = args.rootpath + filename
        outimgpath = args.rootpath + filename
        im_out =denoise_image(imagepath)
        print("The image " + filename + " is processed successfully!")
        sys.stdout.flush()
        cv2.imwrite(outimgpath, im_out)