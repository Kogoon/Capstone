#-*-coding:utf-8-*-

import os
import threading
import time
import subprocess
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import tkinter.ttk as ttk
import tkinter.font as tkFont

from tkinter import filedialog
from tkinter import * 

global output
output = []

# ============================ Window1 =================================
"""
def delete_window():
    
    global delWin
    delWin = Tk()
    delWin.title("Finished Scan")
    delWin.geometry("200x120")
    delWin.resizable(0, 0)
    
    popUp_label = Label(delWin, text='Delete?')
    popUp_label.pack(pady=20)

    cancleBtn = Button(delWin, text='Cancle', command=delWin.destroy)
    cancleBtn.pack(side='bottom', pady=5)

    delBtn = Button(delWin, text='Delete', command=midDel)
    delBtn.pack(side='bottom')

    delWin.mainloop() 
"""
# ============================ Window2 =================================

def program_info():
    infoWindow = Tk()
    infoWindow.title("Program Information")
    infoWindow.geometry("640x480+100+100")
    infoWindow.resizable(0, 0)
    
    test_font = tkFont.Font(family="/usr/share/fonts/Wemakeprice/Wemakeprice-Regular", size=12)    

    # Project
    # Team name
    # About Project
    a = StringVar()
    project_name = StringVar()
    team_name = StringVar()
    #program_def = StringVar()
    #manual = StringVar()

    a.set("2021 정보보호학과 졸업작품")
    project_name.set("인공지능을 활용한 악성파일 탐지 시스템 ")
    team_name.set("팀명 : 네카라쿠배")
    #program_def.set("")
    program_def = '''윈도우의 PE 구조의 파일을 PE헤더, 4-gram(N-gram), 바이너리 이미지의
방법으로 특징을 추출하였고 분류 알고리즘을 이용하여 모델링을 진행,
가장 높은 정확도가 나오는 방법을 택해서 본 프로젝트를 진행하였다.
PE헤더와 check_packer 기능과 함께 추출한 특징을 RandomForest 알고리즘을
이용한 방법을 활용하여 Kicom 오픈소스 백신을 이용, GUI 프로그램을 만들어
프로젝트를 완료하였다.
'''
    #manual.set("")
    manual = '''1. 스캔하고자 하는 폴더를 선택합니다.
2. 선택된 경로를 확인하고 스캔 버튼을 눌러서 결과를 확인합니다.
3. 악성 확률을 확인하고 파일을 지울지 선택합니다. '''

    w1 = Label(infoWindow, textvariable=a).pack(side='top')
    w2 = Label(infoWindow, textvariable=project_name).pack(side='top')
    w3 = Label(infoWindow, textvariable=team_name).pack(side='top')
    w4 = Label(infoWindow, justify=LEFT, text=program_def, font=test_font ).pack(side='top')
    w5 = Label(infoWindow, justify=LEFT, text=manual, font=test_font ).pack(side='top')

    closeBtn = Button(infoWindow, text='Close', command=infoWindow.destroy)
    closeBtn.pack(side='bottom', pady=10)

    infoWindow.mainloop()

# ============================ Window3 =================================
def team_info():
    
    import webbrowser

    new = 1
    url = "http://www.nekabe.me"

    webbrowser.open(url, new=new)

# ============================ Function ================================
def delMal():
    comm = ['python', 'k2.py']
    comm.append('-l')
    comm.append(path)
    print comm
    p = subprocess.call(comm)
    '''
    while True:
        res = p.stdout.readline()
        if res == '' and p.poll() is not None: break
        if res:
            outputBox.insert('end', res.strip() + '\n')
            outputBox.see(END)
    '''
    popUp.destroy()

def midDel():
    t2 = threading.Thread(target=delMal)
    t2.start()

def run():
    comm = ['python', 'k2.py']
    comm.append('-f')
    comm.append(path)
    print comm
    p = subprocess.Popen(comm, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    while True:
        res = p.stdout.readline()
        if res == '' and p.poll() is not None: break
        if res:
            outputBox.insert('end', res.strip() + '\n')
            outputBox.see(END)
    rc = p.poll()

    global popUp
    popUp = Tk()
    popUp.title('Result Scan')
    popUp.geometry("200x120+200+200")
    popUp.resizable(0,0)

    popUp_label = Label(popUp, text='Delete?')
    popUp_label.pack(pady=20)

    cancleBtn = Button(popUp, text='Cancle', command=popUp.destroy)
    cancleBtn.pack(side='bottom', pady=5)

    delBtn = Button(popUp, text='Delete', command=midDel)
    delBtn.pack(side='bottom')
    popUp.mainloop()
    
def midRun():
    t1 = threading.Thread(target=run)
    t1.start()

# ============================ Function ================================
def openDir():
    global path
    dir_path = filedialog.askdirectory(parent=root, initialdir="/home/stud/Deskop/", title="Select Dir")
    path = dir_path
    lblText.set('Selected\n' + path)

def force_quit():
    pass

# ============================== Main ==================================
root = Tk()
root.geometry('640x480+200+200')
root.resizable(0, 0)
root.title("네카라쿠배 v1.0")

# ============================= Frame1 =================================
top_frame = Frame(root, width=640, height=100)
top_frame.pack(side='top', fill='x')

title_font = tkFont.Font(size=16)

# Frame_left, Frame_right
frame_left  = Frame(top_frame, width=240, height=100)
frame_right = Frame(top_frame, width=400, height=100)
frame_left.pack(side='left', fill='x')
frame_right.pack(side='right', fill='x') 

# logo_img 
#jbu_logo = Image.open("./jbu.png")
image = PhotoImage(file='jbu.png')
logo_label = Label(frame_left, image=image)
logo_label.place(x=130, y=0)

# Title_label
title_text = StringVar()
#title_text.set("2021 정보보호학과")
#title_text.set("2021 정보보호학과 졸업작품")
#title_text.set("정보보호학과 네카라쿠배")
title_text.set("MalWare Scanner")

title_label = Label(frame_right, textvariable=title_text, font=("Verdana", 24,))
title_label.place(x=0, y=40)

# ============================= Frame1-2 =================================
top2_frame = Frame(root, width=600, height=40)
top2_frame.pack(side='top', fill='x', ipadx=35)

# result_label
result_text = StringVar()
#result_text.set("[  결 과 창  ]")
result_text.set("[ Result ]")

#result_label = Label(top2_frame, textvariable=result_text, font=('Times', 8))
result_label = Label(top2_frame, textvariable=result_text)
result_label.pack(side='left', padx=35)

test_label = Label(top2_frame, text='')
test_label.pack(side='right', padx=15)

# team_info_button
#tInfoBtn = Button(top2_frame, width=14, text="만든 사람들", font=("Times", 8), command=team_info)
tInfoBtn = Button(top2_frame, width=12, text="CREDIT", command=team_info)
tInfoBtn.pack(side='right', padx=5, pady=2)

# program_info_button
#pInfoBtn = Button(top2_frame, width=14, text="프로그램 정보", font=("Times", 8), command=None)
pInfoBtn = Button(top2_frame, width=12, text="PROGRAM INFO", command=program_info)
pInfoBtn.pack(side='right')

# ============================== Frame2 ================================
middle_frame = Frame(root, width=640, height=280)
middle_frame.pack(side='top')

# Result
outputBox = Text(middle_frame)
outputBox.pack(expand=True)

# ============================== Frame3 ================================
bottom_frame = Frame(root, width=640, height=80)
bottom_frame.pack(side='bottom', fill='x')

lblText = StringVar()
lblText.set("Not Search <Dir>")
#label font

# Path Label
path_lbl = Label(bottom_frame, textvariable = lblText) #font=font
path_lbl.pack(pady=5)

# Quit Button -> 3
quitBtn = Button(bottom_frame, width=12, text="Quit", command=root.destroy)
#quitBtn.pack(side="right", padx=5, pady=10)
quitBtn.pack(side="right", padx=5, pady=7)

# Scan Button -> 2
scanBtn = Button(bottom_frame, width=12, text="Scan", command=midRun)
scanBtn.pack(side="right", padx=5)

# Select Folder Button -> 1
openBtn = Button(bottom_frame, width=12, text="Select Folder", command=openDir)
openBtn.pack(side="right", padx=5)

copyright = StringVar()
#copyright.set("Copyright 2021 네카라쿠배")
copyright.set("Copyright 2021 Nekalikube")
copyrightLabel = Label(bottom_frame, textvariable=copyright).pack(side='left', padx=5)
# ============================== END CODE ==============================
root.mainloop()

