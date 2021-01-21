from tkinter import *
import tkinter.scrolledtext
import json
from merge_pic import *
from tkinter.filedialog import askdirectory, askopenfilename
import tkinter.messagebox
import pandas as pd
import threading
import netifaces
import hashlib
import tkinter.font as tkFont
import pyperclip
import os
import sys
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']


def is_number(string):
    try:
        float(string)
    except ValueError:
        return False
    return True


def select_path(path, image_num_info=None):
    path_ = askdirectory()
    path.set(path_)
    if image_num_info:
        dir_num, img_num = check_dir_num(path_)
        image_num_info.set("子文件夹数目(展开@后):" + str(dir_num) + "\t\t\t总图片数(展开@后):" + str(img_num))


def select_file(file):
    file_ = askopenfilename()
    file.set(file_)


def set_image_size_(col_num, dir_num, row_spacing, col_spacing, small_h, small_w, image_size):
    large_h, large_w = get_large_image_size(col_num, dir_num, row_spacing, col_spacing, small_h, small_w)
    image_size.set("("+str(large_w)+","+str(large_h)+")")
    return 1


def get_large_image_size(col_num, dir_num, row_spacing, col_spacing, small_h, small_w):
    """
    获得大图尺寸
    :param col_num:
    :param dir_num:
    :param row_spacing:
    :param col_spacing:
    :param small_h:
    :param small_w:
    :return:
    """
    row_num = math.ceil(dir_num / col_num)
    row_size = small_h * row_num + sum(row_spacing)
    col_size = small_w * col_num + sum(col_spacing)

    return row_size, col_size


def open_ouput_dir(output_path):
    os.startfile(output_path)


def check_dir_num(path, pic_num=-1, file_list=None):
    """
    检查子文件夹个数和总图片数
    :param path:
    :param pic_num:
    :param file_list:
    :return:
    """
    if not os.path.exists(path):
        return None
    if not file_list:
        file_list = os.listdir(path)

    file_list.sort()
    new_file_list = deepcopy(file_list)

    for i in range(len(file_list)):
        if "@" in file_list[i]:
            repeat_num = file_list[i].split("@")[1]
            for j in range(int(repeat_num)-1):
                new_file_list.insert(i, file_list[i])

    new_file_list.sort()
    file_list = new_file_list

    image_total = 0  # 图片总数

    for file in file_list:
        file_with_path = os.path.join(path, file)
        image_file_list = os.listdir(file_with_path)
        image_file_list.sort()
        image_total = image_total + len(image_file_list)
        if len(image_file_list) != pic_num and pic_num > 0:
            tkinter.messagebox.showwarning("警告", file + "子文件夹图片数错误")
            return None

    return len(file_list), image_total


def get_spacing_list(spacing, image_length, image_num):
    """
    获得间距列表
    :param spacing: 原间距
    :param image_length: 图片高度或宽度
    :param image_num: 图片数
    :return:
    """
    # 整数值(四舍五入)
    spacing_int = round(spacing)
    image_length_int = round(image_length)
    # 小数部分
    spacing_dec = spacing - spacing_int
    image_length_dec = image_length - image_length_int
    # 累计值
    total = 0

    # 间距列表
    spacing_list = [0]

    for i in range(image_num-1):
        if i == 0:
            total = total + image_length_dec
        else:
            total = total + image_length_dec + spacing_dec

        # 根据累计值处理
        if total >= 1:
            total = total - 1
            spacing_list.append(spacing_int+1)
        elif total <= -1:
            total = total + 1
            spacing_list.append(spacing_int-1)
        else:
            spacing_list.append(spacing_int)
    return spacing_list


def change_mm_pixel(number, dpi):
    return number/25.4 * dpi


def check(input_path, output_path, image_number, col_num, row_spacing, col_spacing, small_h, small_w, select_excel, col_name):
    """
    :param input_path: 用户选择文件夹路径
    :param output_path: 用户选择输出路径
    :param image_number: 每个子文件夹中的图片数目
    :param col_num: 大图列数
    :param row_spacing: 行间距
    :param col_spacing: 列间距
    :param small_h: 小图高度
    :param small_w: 小图宽度
    :return:
    """
    if not os.path.exists(input_path):
        tkinter.messagebox.showwarning("警告", "输入路径不存在")
        return 0
    if not os.path.exists(output_path):
        tkinter.messagebox.showwarning("警告", "输出路径不存在")
        return 0
    if not image_number:
        tkinter.messagebox.showwarning("警告", "缺少子文件夹中的图片数目")
        return 0
    if not image_number.isdigit():
        tkinter.messagebox.showwarning("警告", "子文件夹中的图片数目需要输入整数")
        return 0
    if not col_num:
        tkinter.messagebox.showwarning("警告", "缺少拼图列数")
        return 0
    if not col_num.isdigit():
        tkinter.messagebox.showwarning("警告", "拼图列数需要输入整数")
        return 0
    if not row_spacing:
        tkinter.messagebox.showwarning("警告", "缺少行间距")
        return 0
    if not is_number(row_spacing):
        tkinter.messagebox.showwarning("警告", "行间距需要输入数字")
        return 0
    if not col_spacing:
        tkinter.messagebox.showwarning("警告", "缺少列间距")
        return 0
    if not is_number(col_spacing):
        tkinter.messagebox.showwarning("警告", "列间距需要输入数字")
        return 0
    if not small_h:
        tkinter.messagebox.showwarning("警告", "缺少魔方高度")
        return 0
    if not is_number(small_h):
        tkinter.messagebox.showwarning("警告", "魔方高度需要输入数字")
        return 0
    if not small_w:
        tkinter.messagebox.showwarning("警告", "缺少魔方宽度")
        return 0
    if not is_number(small_w):
        tkinter.messagebox.showwarning("警告", "魔方宽度需要输入数字")
        return 0

    return 1


def init_window(input_path, output_path, image_number, col_num, row_spacing, col_spacing, small_h, small_w, dpi,
                select_excel, col_name, image_num_info):

    if os.path.exists("data/history.csv"):
        df_last = pd.read_csv("data/history.csv")
        input_path.set(df_last["最近记录"][0])
        output_path.set(df_last["最近记录"][1])
        image_number.set(df_last["最近记录"][2])
        col_num.set(df_last["最近记录"][3])
        row_spacing.set(df_last["最近记录"][4])
        col_spacing.set(df_last["最近记录"][5])
        small_h.set(df_last["最近记录"][6])
        small_w.set(df_last["最近记录"][7])
        dpi.set(df_last["最近记录"][8])
        select_excel.set(df_last["最近记录"][9])
        col_name.set(df_last["最近记录"][10])
        if check_dir_num(df_last["最近记录"][0]):
            dir_num, img_num = check_dir_num(df_last["最近记录"][0])
            image_num_info.set("子文件夹数目(展开@后):" + str(dir_num) + "\t\t\t总图片数(展开@后):" + str(img_num))


def create_img(input_path, output_path, image_number, col_num, row_spacing_mm, col_spacing_mm, small_h_mm, small_w_mm, select_excel,
               col_name, dpi, progress_text):
    if not check(input_path, output_path, image_number, col_num, row_spacing_mm, col_spacing_mm, small_h_mm, small_w_mm,
                 select_excel, col_name):
        return 0

    # 参数处理
    image_number = int(image_number)
    col_num = int(col_num)
    dpi = int(dpi)
    small_h = change_mm_pixel(float(small_h_mm), dpi)
    small_w = change_mm_pixel(float(small_w_mm), dpi)
    row_spacing = change_mm_pixel(float(row_spacing_mm), dpi)
    col_spacing = change_mm_pixel(float(col_spacing_mm), dpi)

    # 子文件夹检查
    if select_excel != '' and select_excel != 'nan':
        if not os.path.exists(select_excel):
            tkinter.messagebox.showwarning("警告", "excel生产任务表不存在")
            return 0
        try:
            df_excel = pd.read_excel(select_excel)
            file_list = list(df_excel[col_name])
        except:
            tkinter.messagebox.showwarning("警告", "产品编号列错误")
            return 0
        try:
            dir_num, img_sum_num = check_dir_num(input_path, image_number, file_list)
        except Exception as e:
            tkinter.messagebox.showwarning("警告", e)
            return 0

    else:
        dir_num, img_sum_num = check_dir_num(input_path, image_number)

    row_num = math.ceil(dir_num / col_num)  # 行数
    row_spacing_list = get_spacing_list(row_spacing, small_h, row_num)
    col_spacing_list = get_spacing_list(col_spacing, small_w, col_num)

    small_h = round(small_h)
    small_w = round(small_w)

    # 最后确认
    large_h, large_w = get_large_image_size(col_num, dir_num, row_spacing_list, col_spacing_list, small_h, small_w)
    msg_yes_no = tkinter.messagebox.askyesno("提示", "总文件夹数(展开@后):"+str(dir_num)+"\n总图片数(展开@后):" +
                                             str(img_sum_num)+"\n行数:"+str(row_num)+"\n列数:" +
                                             str(col_num)+"\n合成图片大小:("+str(large_w)+"*"+str(large_h) +
                                             ")\n是否开始拼图？")
    if msg_yes_no:
        if select_excel != '' and select_excel != 'nan':
            df_excel = pd.read_excel(select_excel)
            file_list = list(df_excel[col_name])
            imgs = read_dir(input_path, image_number, (small_w, small_h), output_path, file_list, progress_text)
        else:
            imgs = read_dir(input_path, image_number, (small_w, small_h), output_path, progress_text=progress_text)
        if imgs:
            data = [
                [input_path],
                [output_path],
                [str(image_number)],
                [str(col_num)],
                [str(row_spacing_mm)],
                [str(col_spacing_mm)],
                [str(small_h_mm)],
                [str(small_w_mm)],
                [str(dpi)],
                [str(select_excel)],
                [str(col_name)]
            ]
            df_history = pd.DataFrame(data, index=['选择文件夹', '拼图输出文件夹', '子文件夹中图片数量', '拼图列数',
                                                   '行间距', '列间距', '魔方高度', '魔方宽度', '打印分辨率', 'excel生产任务表', 'excel产品编号列'],
                                      columns=['最近记录'])
            if not os.path.exists("data"):
                os.makedirs("data")
            df_history.to_csv("data/history.csv", encoding="utf_8_sig")
            progress_text.config(state=tkinter.NORMAL)
            progress_text.insert('end', "开始拼图....\n")
            progress_text.config(state=tkinter.DISABLED)
            for i in range(len(imgs)):
                th_merge = threading.Thread(target=merge_pic, args=(imgs[i], col_num, col_spacing_list,
                                                                           row_spacing_list, output_path + "/" + str(i+1)
                                                                           + ".jpg", i, len(imgs), progress_text, dpi,))
                th_merge.setDaemon(True)
                th_merge.start()
                th_merge.join()

            tkinter.messagebox.showinfo("提示", "合并完成")


def start(input_path, output_path, image_number, col_num, row_spacing, col_spacing, small_h, small_w, select_excel, col_name, dpi, progress_text):
    """
    :param input_path: 用户选择文件夹路径
    :param output_path: 用户选择输出路径
    :param image_number: 每个子文件夹中的图片数目
    :param col_num: 大图列数
    :param row_spacing: 行间距
    :param col_spacing: 列间距
    :param small_h: 小图高度
    :param small_w: 小图宽度
    :param select_excel:
    :param col_name:
    :param dpi:
    :param progress_text:
    :return:
    """
    progress_text.config(state=tkinter.NORMAL)
    progress_text.delete(1.0, END)
    progress_text.config(state=tkinter.DISABLED)
    th = threading.Thread(target=create_img, args=(input_path, output_path, image_number, col_num, row_spacing,
                                                   col_spacing, small_h, small_w, select_excel, col_name, dpi,
                                                   progress_text,))
    th.setDaemon(True)
    th.start()


class LoginPage(object):
    """
    登陆页面
    """

    def check_password(self, password_):
        routingNicName = netifaces.gateways()['default'][netifaces.AF_INET][1]
        result = hashlib.md5()
        result.update(routingNicName.encode(encoding='utf-8'))
        if password_ == result.hexdigest():
            tkinter.messagebox.showinfo("提示", "登录成功！")
            password_dir = {"password": password_}
            if not os.path.exists("data/"):
                os.mkdir("data/")
            with open("data/password.json", "w") as f:
                json.dump(password_dir, f)
            self.root.destroy()
            MainPage()
        else:
            tkinter.messagebox.showwarning("警告", "密码错误！")
            return False


    def __init__(self):

        flag = True
        if os.path.exists("data/password.json"):
            with open("data/password.json", 'r') as load_f:
                password_str = json.load(load_f)
            routingNicName = netifaces.gateways()['default'][netifaces.AF_INET][1]
            result = hashlib.md5()
            result.update(routingNicName.encode(encoding='utf-8'))
            if password_str['password'] == result.hexdigest():
                flag = False
                MainPage()

        if flag:
            self.root = Tk()
            self.root.title("登录")

            password = StringVar()
            password.set(pyperclip.paste())

            register_number = StringVar()  # 注册码
            register_number.set(netifaces.gateways()['default'][netifaces.AF_INET][1])

            ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)
            Label(self.root, text="注册码:", font=ft).grid(row=0, column=0)
            Entry(self.root, textvariable=register_number, width=50, state='readonly').grid(row=0, column=1)
            Label(self.root, text="输入密码:", font=ft).grid(row=1, column=0)
            Entry(self.root, textvariable=password, width=50).grid(row=1, column=1)
            Button(self.root, text="登录", command=lambda: self.check_password(password.get())).grid(row=2, column=0)

            self.root.mainloop()


class MainPage(object):
    """
    主界面
    """

    def __init__(self):
        self.root = Tk()
        self.root.title("有魔有样自动拼图软件")

        input_path = StringVar()  # 用户选择文件夹路径
        image_num_info = StringVar()  # 文件夹中图片信息提示
        output_path = StringVar()  # 用户选择输出路径
        image_number = StringVar()  # 每个子文件夹中的图片数目
        col_num = StringVar()  # 大图列数
        row_spacing = StringVar()  # 行间距
        col_spacing = StringVar()  # 列间距
        small_h = StringVar()  # 小图高度
        small_w = StringVar()  # 小图宽度
        dpi = StringVar()  # 大图尺寸
        select_excel = StringVar()  # 指定子文件夹的excel文件
        col_name = StringVar()  # 指定文件中选择的列

        init_window(input_path, output_path, image_number, col_num, row_spacing, col_spacing, small_h, small_w, dpi,
                    select_excel, col_name, image_num_info)

        Label(self.root, text="选择文件夹:").grid(row=0, column=0)
        Entry(self.root, textvariable=input_path).grid(row=0, column=1)
        Button(self.root, text="浏览", command=lambda: select_path(input_path, image_num_info)).grid(row=0, column=2)
        Label(self.root, textvariable=image_num_info).grid(row=1, columnspan=2)
        Label(self.root, text="选择拼图输出文件夹:").grid(row=2, column=0)
        Entry(self.root, textvariable=output_path).grid(row=2, column=1)
        Button(self.root, text="浏览", command=lambda: select_path(output_path)).grid(row=2, column=2)
        Label(self.root, text="子文件夹中图片数量:").grid(row=3, column=0)
        Entry(self.root, textvariable=image_number).grid(row=3, column=1)
        Label(self.root, text="拼图列数:").grid(row=4, column=0)
        Entry(self.root, textvariable=col_num).grid(row=4, column=1)
        Label(self.root, text="行间距(mm):").grid(row=5, column=0)
        Entry(self.root, textvariable=row_spacing).grid(row=5, column=1)
        Label(self.root, text="列间距(mm):").grid(row=6, column=0)
        Entry(self.root, textvariable=col_spacing).grid(row=6, column=1)
        Label(self.root, text="魔方高度(mm):").grid(row=7, column=0)
        Entry(self.root, textvariable=small_h).grid(row=7, column=1)
        Label(self.root, text="魔方宽度(mm):").grid(row=8, column=0)
        Entry(self.root, textvariable=small_w).grid(row=8, column=1)
        Label(self.root, text="打印分辨率(像素/英寸):").grid(row=9, column=0)
        Entry(self.root, textvariable=dpi).grid(row=9, column=1)
        Label(self.root, text="excel生产任务表:").grid(row=10, column=0)
        Entry(self.root, textvariable=select_excel).grid(row=10, column=1)
        Button(self.root, text="浏览", command=lambda: select_file(select_excel)).grid(row=10, column=2)
        Label(self.root, text="excel产品编号列:").grid(row=11, column=0)
        Entry(self.root, textvariable=col_name).grid(row=11, column=1)
        progress_text = tkinter.scrolledtext.ScrolledText(self.root, state=tkinter.DISABLED)
        progress_text.grid(row=13, columnspan=2)
        Button(self.root, text="打开结果文件夹", command=lambda: open_ouput_dir(output_path.get())).grid(row=12, column=0)
        Button(self.root, text="开始拼图", command=lambda: start(input_path.get(), output_path.get(), image_number.get(),
                                                             col_num.get(), row_spacing.get(), col_spacing.get(),
                                                             small_h.get(), small_w.get(), select_excel.get(),
                                                             col_name.get(), dpi.get(), progress_text)).grid(row=12, column=1)

        self.root.mainloop()


if __name__ == '__main__':
    LoginPage()
    # MainPage()
    # for i in range(4, 30):
    # print(len(get_spacing_list(5, 56.6, 20)))
    # print(change_mm_pixel(56.6, 300))
