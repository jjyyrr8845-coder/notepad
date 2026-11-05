import tkinter as tk
from tkinter import messagebox

# 단축키로 호출되면 event 인자가 넘어오므로 event=None을 받아줘야 해요
def new_file(event=None):
    messagebox.showinfo("새파일", "새파일 메뉴 선택", parent=root)
    return "break"

def open_file(event=None):
    messagebox.showinfo("열기", "열기 메뉴 선택", parent=root)
    return "break"

def save_file(event=None):
    messagebox.showinfo("저장", "저장 메뉴 선택", parent=root)
    return "break"

def exit_app(event=None):
    root.destroy()
    return "break"

# Text 위젯이 이미 Ctrl+X/C/V를 처리하므로, 가상 이벤트를 발생시켜 실제로 동작하게 해요
def cut_file():
    text.event_generate("<<Cut>>")

def copy_file():
    text.event_generate("<<Copy>>")

def paste_file():
    text.event_generate("<<Paste>>")

def about_file():
    messagebox.showinfo("프로그램 정보", "프로그램 정보 메뉴 선택", parent=root)

root = tk.Tk()
root.title("첫 메모장")
root.geometry("800x500")

text = tk.Text(root, wrap="word")
text.pack(fill=tk.BOTH, expand=True)
text.focus_set()   # 괄호 ()가 빠져 있었어요!

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# 파일 메뉴 (underline=3 → "(F)"의 F에 밑줄 → Alt+F로 메뉴 열기)
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="파일(F)", underline=3, menu=file_menu)
file_menu.add_command(label="새파일", accelerator="Ctrl+N", command=new_file)
file_menu.add_command(label="열기", accelerator="Ctrl+O", command=open_file)
file_menu.add_command(label="저장", accelerator="Ctrl+S", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="종료", accelerator="Ctrl+Q", command=exit_app)

# 편집 메뉴
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="편집(E)", underline=3, menu=edit_menu)
edit_menu.add_command(label="잘라내기", accelerator="Ctrl+X", command=cut_file)
edit_menu.add_command(label="복사하기", accelerator="Ctrl+C", command=copy_file)
edit_menu.add_command(label="붙여넣기", accelerator="Ctrl+V", command=paste_file)

# 도움말 메뉴
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="도움말(H)", underline=4, menu=help_menu)
help_menu.add_command(label="프로그램 정보", command=about_file)

# 단축키 배선 (대소문자 모두, Caps Lock 대비)
shortcuts = {
    "n": new_file,
    "o": open_file,
    "s": save_file,
    "q": exit_app,
}
for key, func in shortcuts.items():
    text.bind(f"<Control-{key}>", func)
    text.bind(f"<Control-{key.upper()}>", func)

root.mainloop()