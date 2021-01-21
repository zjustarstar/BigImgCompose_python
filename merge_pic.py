import numpy as np
import math
import os
import tkinter.messagebox
from tkinter import *
from copy import deepcopy
import pandas as pd

try:
    from PIL import Image
except ImportError:
    import Image


def func(string):
    return string.split('.')[0]


def merge_pic(images, col_num, col_spacing, row_spacing, output_path, index, n, progress_text, dpi):
    """
    将多张图片合成一张
    :param images: 源图片数组
    :param col_num: 列数
    :param col_spacing: 列间距数组
    :param row_spacing: 行间距数组
    :param output_path: 输出路径
    :return: 合成的图片
    """

    img_num = len(images)
    row_num = math.ceil(img_num/col_num)
    small_h, small_w = images[0].shape[:2]
    # 计算图片大小
    row_size = small_h*row_num+sum(row_spacing)
    col_size = small_w*col_num+sum(col_spacing)

    # 合并
    merge_img = np.zeros((row_size, col_size, 3), images[0].dtype)
    merge_img.fill(255)
    count = 0
    for i in range(row_num):
        if count >= img_num:
            break
        for j in range(col_num):
            if count >= img_num:
                break
            else:
                im = images[count]
                t_h_end = row_size - i * small_h - sum(row_spacing[0:i+1])
                t_w_start = j * small_w + sum(col_spacing[0:j+1])
                t_h_start = t_h_end - im.shape[0]
                t_w_end = t_w_start + im.shape[1]
                merge_img[t_h_start:t_h_end, t_w_start:t_w_end] = im
                count = count + 1

    try:
        merge_img = Image.fromarray(np.uint8(merge_img))
        merge_img.save(output_path, dpi=(dpi, dpi))
    except:
        tkinter.messagebox.showwarning("警告", "写入错误")

    progress_text.config(state=tkinter.NORMAL)
    progress_text.insert(END, "完成" + str(index + 1) + "/" + str(n) + "\n")
    progress_text.config(state=tkinter.DISABLED)

    return merge_img


def read_dir(path, pic_num, size, output_path, file_list=None, progress_text=None):
    """
    :param path: 文件夹路径
    :param pic_num: 子文件夹中的图片个数
    :param size: 读取图片大小
    :param output_path: 输出文件夹
    :param file_list: 子文件夹名称列表
    :param progress_text: 进度
    :return: 图片列表
    """
    images = []
    for i in range(pic_num):
        images.append([])

    if not file_list:
        file_list = os.listdir(path)

    file_list.sort()
    new_file_list = deepcopy(file_list)

    for i in range(len(file_list)):
        if "@" in file_list[i]:
            repeat_num = file_list[i].split("@")[1]
            for j in range(int(repeat_num)-1):
                new_file_list.insert(i, file_list[i])

    new_file_list.sort(key=func)
    file_list = new_file_list

    file_list_index = [i for i in range(1, len(file_list)+1)]

    df_info = pd.DataFrame(file_list, columns=["子文件夹"])
    df_info.index = file_list_index
    df_info.to_csv(output_path+"/子文件夹记录.csv", header=False, encoding="utf_8_sig")

    now = 1
    sum_dir = len(file_list)

    progress_text.config(state=tkinter.NORMAL)
    progress_text.insert('end', "开始读取图片....\n")
    progress_text.config(state=tkinter.DISABLED)

    for file in file_list:
        file_with_path = os.path.join(path, file)
        image_file_list = os.listdir(file_with_path)
        image_file_list.sort(key=func)
        if len(image_file_list) != pic_num:
            tkinter.messagebox.showwarning("警告", file + "子文件夹图片数错误")
            return None
        for i in range(pic_num):
            image_file_with_path = os.path.join(file_with_path, image_file_list[i])
            img = Image.open(image_file_with_path)
            img = img.convert("RGB")
            img = img.resize(size, Image.ANTIALIAS)
            images[i].append(np.array(img))
        progress_text.config(state=tkinter.NORMAL)
        progress_text.insert('end', "读取完成" + str(now) + "/" + str(sum_dir)+"\n")
        progress_text.config(state=tkinter.DISABLED)
        now = now+1

    return images


