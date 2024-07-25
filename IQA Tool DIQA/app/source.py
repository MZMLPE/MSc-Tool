# @title Functions to detect issue
import numpy as np
import cv2 as cv
import math

from skimage import feature
import os.path
import tensorflow as tf
import glob
import math
import xlsxwriter
import os
import time
from datetime import datetime, timezone, timedelta
from tensorflow.keras.layers import Conv2D, Dense, GlobalAveragePooling2D
from .log import LOG


# Constantes
root_path = 'app/images/'
model_path = 'app/model.h5'
fuso_horario = timezone(timedelta(hours=-3))
SCORE_RUIM = 0.7

# title Functions to image evaluation

def normalize_kernel(kernel: tf.Tensor) -> tf.Tensor:
    return kernel / tf.reduce_sum(kernel)


def gaussian_kernel2d(kernel_size: int, sigma: float, dtype=tf.float32) -> tf.Tensor:
    _range = tf.range(kernel_size)
    x, y = tf.meshgrid(_range, _range)
    constant = tf.cast(tf.round(kernel_size / 2), dtype=dtype)
    x = tf.cast(x, dtype=dtype) - constant
    y = tf.cast(y, dtype=dtype) - constant
    kernel = 1 / (2 * math.pi * sigma ** 2) * tf.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
    return normalize_kernel(kernel)


def gaussian_filter(image: tf.Tensor, kernel_size: int, sigma: float, dtype=tf.float32) -> tf.Tensor:
    kernel = gaussian_kernel2d(kernel_size, sigma)
    if image.get_shape().ndims == 3:
        image = image[tf.newaxis, :, :, :]
    image = tf.cast(image, tf.float32)
    image = tf.nn.conv2d(image, kernel[:, :, tf.newaxis, tf.newaxis], strides=1, padding='SAME')
    return tf.cast(image, dtype)


def image_shape(image: tf.Tensor, dtype=tf.int32) -> tf.Tensor:
    shape = tf.shape(image)
    shape = shape[:2] if image.get_shape().ndims == 3 else shape[1:3]
    return tf.cast(shape, dtype)


def scale_shape(image: tf.Tensor, scale: float) -> tf.Tensor:
    shape = image_shape(image, tf.float32)
    shape = tf.math.ceil(shape * scale)
    return tf.cast(shape, tf.int32)


def rescale(image: tf.Tensor, scale: float, dtype=tf.float32, **kwargs) -> tf.Tensor:
    assert image.get_shape().ndims in (3, 4), 'The tensor must be of dimension 3 or 4'
    image = tf.cast(image, tf.float32)
    rescale_size = scale_shape(image, scale)
    rescaled_image = tf.image.resize(image, size=rescale_size, **kwargs)
    return tf.cast(rescaled_image, dtype)


def image_preprocess(image: tf.Tensor) -> tf.Tensor:
    image = tf.cast(image, tf.float32) / 255.0
    image = tf.image.rgb_to_grayscale(image)
    image_low = gaussian_filter(image, 16, 7 / 6)
    image_low = rescale(image_low, 1 / 4, method=tf.image.ResizeMethod.BICUBIC)
    image_low = tf.image.resize(image_low, size=image_shape(image), method=tf.image.ResizeMethod.BICUBIC)
    return image - tf.cast(image_low, image.dtype)


def read_image(filename: str, **kwargs) -> tf.Tensor:
    stream = tf.io.read_file(filename)
    return tf.image.decode_image(stream, **kwargs)


def printProgressBar(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=50, fill='█',
                     printEnd=""):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    LOG(f'\r{prefix} |{bar}| {percent}% {suffix}')
    #print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        LOG(' ')


def calculate_score(imagens_folder_path):
    model = tf.keras.models.load_model(model_path)

    result_list = []
    image_list = glob.glob(imagens_folder_path + '/*.jpg')
    max_iteration = len(image_list)

    if max_iteration > 0:
        n = imagens_folder_path.replace(root_path, '')
        LOG(f'\nFolder: {n}, ({max_iteration} images) ')
        printProgressBar(0, max_iteration)

    for iteration, image_path in enumerate(image_list):
        image = read_image(image_path)
        prediction = model.predict(image_preprocess(image))[0][0]
        prediction = 1 if prediction > 1 else prediction
        result = {
            'path': f'{image_path}',
            'prediction': prediction,
        }
        result_list.append(result)
        printProgressBar(iteration + 1, max_iteration)
    return result_list


def write_results(worksheet, result_folder, index, format_default, folder_name):
    max_width0 = 5
    max_width1 = 6
    max_width2 = 4

    max_iteration = 1
    iteration = 0
    LOG(f'\nFixing score and writing results: {max_iteration} folders')  # muito lento
    printProgressBar(iteration, max_iteration)

    i = 0
    while i < len(result_folder):
        filename_1 = result_folder[i].get('path').split(os.path.sep)[-1]
        max_width0 = max(len(filename_1), max_width0)
        max_width2 = max(len(folder_name), max_width2)

        result1 = result_folder[i].get('prediction')

        col_index = 0
        worksheet.write(index, col_index, filename_1)
        col_index += 1
        worksheet.write(index, col_index, folder_name)
        col_index += 1
        worksheet.write(index, col_index, result1,
                         format_default)
        col_index += 1
        index += 1
        i += 1       

    return max_width0, max_width1, max_width2


def auto_fit(worksheet, width0, width1, width2):
    # image, folder, type
    worksheet.set_column(0, 0, width0 + 5)
    worksheet.set_column(1, 1, width1 + 5)
    worksheet.set_column(2, 2, width2 + 5)
    # scores
    worksheet.set_column(3, 3, 11)
    # result, issue
    worksheet.set_column(4, 4, 6)
    worksheet.set_column(5, 5, 38)


#   worksheet.set_column('J:J', None, None, {'hidden': True})

def main_source(folder_path, workbook, tab_name):
    LOG(f'\n...Starting device...\n')
    start_time = time.time()
    result = {}

    # workbook cell formats
    format_default = workbook.add_format({'num_format': '#,##0.0000'})

    result = calculate_score(folder_path)
    result.sort(key=lambda x: (x.get('path')))
    
    folder_name = folder_path.split('/')[-1].upper()

    worksheet = workbook.add_worksheet('{}'.format(tab_name))
    index = 0
    worksheet.write(index, 0, 'Image')
    worksheet.write(index, 2, 'Score')
    index += 1
    w0, w1, w2 = write_results(worksheet, result, index, format_default, folder_name)
    auto_fit(worksheet, w0, w1, w2)

    end_time = time.time()
    t = int(end_time - start_time)
    LOG(f'Tab {tab_name} added, duration {t} seconds')
    return result
