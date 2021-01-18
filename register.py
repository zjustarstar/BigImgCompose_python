import os
import sys
import netifaces
import hashlib
from tkinter import *
import tkinter.font as tkFont
import pyperclip
import tkinter.messagebox


def get_password(register_number, password_):
    result = hashlib.md5()
    result.update(register_number.encode(encoding='utf-8'))
    password_.set(result.hexdigest())
    pyperclip.copy(result.hexdigest())
    tkinter.messagebox.showinfo("提示", "密码已复制！")


if __name__ == '__main__':
    root = Tk()
    root.title("注册密码")

    password = StringVar()
    register_number = StringVar()  # 注册码

    ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)

    Label(root, text="输入注册码:", font=ft).grid(row=0, column=0)
    Entry(root, textvariable=register_number, width=30).grid(row=0, column=1)
    Label(root, text="密码:", font=ft).grid(row=1, column=0)
    Entry(root, textvariable=password, width=30).grid(row=1, column=1)
    Button(root, text="获得密码", command=lambda: get_password(register_number.get(), password)).grid(row=2, column=1)

    root.mainloop()
