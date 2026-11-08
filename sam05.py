import tkinter as tk
from tkinter import messagebox

# ---------- 파일 메뉴 ----------
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

# ---------- 편집 메뉴 ----------
def cut_file():
    text.event_generate("<<Cut>>")

def copy_file():
    text.event_generate("<<Copy>>")

def paste_file():
    text.event_generate("<<Paste>>")

def about_file():
    messagebox.showinfo("프로그램 정보", "프로그램 정보 메뉴 선택", parent=root)

# ---------- 찾기 / 바꾸기 ----------
find_win = None      # 찾기 창 (없으면 None)
find_entry = None    # 찾을 내용 입력칸

def dialog_parent():
    """메시지 박스를 띄울 부모 창 (찾기 창이 열려 있으면 그 위에)"""
    if find_win is not None and find_win.winfo_exists():
        return find_win
    return root

def find_next(event=None):
    keyword = find_var.get()
    if not keyword:
        return "break"

    text.tag_remove("found", "1.0", tk.END)       # 이전 형광펜 지우기
    ignore_case = not case_var.get()
    start = text.index(tk.INSERT)                 # 현재 커서부터 검색

    pos = text.search(keyword, start, stopindex=tk.END, nocase=ignore_case)
    if not pos:                                   # 끝까지 없으면 처음부터 다시
        pos = text.search(keyword, "1.0", stopindex=start, nocase=ignore_case)
    if not pos:
        messagebox.showinfo("찾기", f"'{keyword}'을(를) 찾을 수 없어요.",
                            parent=dialog_parent())
        return "break"

    end = f"{pos}+{len(keyword)}c"
    text.tag_add("found", pos, end)               # 형광펜 칠하기
    text.mark_set(tk.INSERT, end)                 # 커서를 찾은 글자 뒤로
    text.see(pos)                                 # 화면에 보이도록 스크롤
    return "break"

def replace_one():
    ranges = text.tag_ranges("found")
    if ranges:                                    # 현재 형광펜 칠한 곳이 있으면 교체
        start = str(ranges[0])
        rep = replace_var.get()
        text.delete(ranges[0], ranges[1])
        text.insert(start, rep)
        text.mark_set(tk.INSERT, f"{start}+{len(rep)}c")
        text.tag_remove("found", "1.0", tk.END)
    find_next()                                   # 다음 항목으로 이동

def replace_all():
    keyword = find_var.get()
    rep = replace_var.get()
    if not keyword:
        return

    text.tag_remove("found", "1.0", tk.END)
    ignore_case = not case_var.get()
    count = 0
    pos = "1.0"
    while True:
        pos = text.search(keyword, pos, stopindex=tk.END, nocase=ignore_case)
        if not pos:
            break
        text.delete(pos, f"{pos}+{len(keyword)}c")
        text.insert(pos, rep)
        pos = f"{pos}+{len(rep)}c"                # 바꾼 글자 뒤부터 계속 (무한반복 방지)
        count += 1

    messagebox.showinfo("모두 바꾸기", f"{count}개를 바꿨어요.", parent=dialog_parent())

BG_COLORS = {
    "white":  "#ffffff",
    "pink":   "#ffd6e7",
    "yellow": "#fff9c4",
}

def apply_bg():
    text.config(bg=BG_COLORS[bg_var.get()])

def update_status(event=None):
    line, col = text.index(tk.INSERT).split(".")
    status_var.set(f"{int(line)}줄, {int(col) + 1}열")


def close_find_dialog(event=None):
    global find_win
    text.tag_remove("found", "1.0", tk.END)
    if find_win is not None:
        find_win.destroy()
        find_win = None

def open_find_dialog(event=None):
    global find_win, find_entry

    # 이미 열려 있으면 새로 만들지 않고 앞으로 가져오기
    if find_win is not None and find_win.winfo_exists():
        find_win.lift()
        find_entry.focus_set()
        return "break"

    # 본문에서 드래그해 둔 글자가 있으면 자동으로 채워주기
    if text.tag_ranges("sel"):
        find_var.set(text.get("sel.first", "sel.last"))

    find_win = tk.Toplevel(root)
    find_win.title("찾기 및 바꾸기")
    find_win.transient(root)                      # 메모장 위에 항상 떠 있게
    find_win.resizable(False, False)
    find_win.protocol("WM_DELETE_WINDOW", close_find_dialog)

    tk.Label(find_win, text="찾을 내용:").grid(row=0, column=0, padx=8, pady=(10, 4), sticky="e")
    find_entry = tk.Entry(find_win, textvariable=find_var, width=28)
    find_entry.grid(row=0, column=1, padx=4, pady=(10, 4))

    tk.Label(find_win, text="바꿀 내용:").grid(row=1, column=0, padx=8, pady=4, sticky="e")
    tk.Entry(find_win, textvariable=replace_var, width=28).grid(row=1, column=1, padx=4, pady=4)

    tk.Checkbutton(find_win, text="대/소문자 구분", variable=case_var).grid(
        row=2, column=1, sticky="w", padx=4)

    tk.Button(find_win, text="다음 찾기", width=10, command=find_next).grid(row=0, column=2, padx=8, pady=(10, 4))
    tk.Button(find_win, text="바꾸기", width=10, command=replace_one).grid(row=1, column=2, padx=8, pady=4)
    tk.Button(find_win, text="모두 바꾸기", width=10, command=replace_all).grid(row=2, column=2, padx=8, pady=4)
    tk.Button(find_win, text="닫기", width=10, command=close_find_dialog).grid(row=3, column=2, padx=8, pady=(4, 10))

    find_entry.bind("<Return>", find_next)        # 입력칸에서 Enter = 다음 찾기
    find_win.bind("<Escape>", close_find_dialog)  # Esc = 닫기

    find_entry.focus_set()
    find_entry.select_range(0, tk.END)
    return "break"

# ---------- 메인 창 ----------
root = tk.Tk()
root.title("첫 메모장")
root.geometry("800x500")

# 찾기/바꾸기에서 쓰는 변수 (root 생성 후에 만들어야 해요)
find_var = tk.StringVar()
replace_var = tk.StringVar()
case_var = tk.BooleanVar(value=False)
bg_var = tk.StringVar(value="white") 
status_var = tk.StringVar(value="1줄, 1열")
status_bar = tk.Label(root, textvariable=status_var, anchor="e", relief="sunken", padx=8)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

text = tk.Text(root, wrap="word", undo=True)      # undo=True: Ctrl+Z로 되돌리기 가능
text.pack(fill=tk.BOTH, expand=True)
text.focus_set()
text.tag_config("found", background="yellow", foreground="black")   # 형광펜 스타일

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="파일(F)", underline=3, menu=file_menu)
file_menu.add_command(label="새파일", accelerator="Ctrl+N", command=new_file)
file_menu.add_command(label="열기", accelerator="Ctrl+O", command=open_file)
file_menu.add_command(label="저장", accelerator="Ctrl+S", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="종료", accelerator="Ctrl+Q", command=exit_app)

edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="편집(E)", underline=3, menu=edit_menu)
edit_menu.add_command(label="잘라내기", accelerator="Ctrl+X", command=cut_file)
edit_menu.add_command(label="복사하기", accelerator="Ctrl+C", command=copy_file)
edit_menu.add_command(label="붙여넣기", accelerator="Ctrl+V", command=paste_file)
edit_menu.add_separator()
edit_menu.add_command(label="찾기", accelerator="Ctrl+F", command=open_find_dialog)
edit_menu.add_command(label="다음 찾기", accelerator="F3", command=find_next)
edit_menu.add_command(label="바꾸기", accelerator="Ctrl+H", command=open_find_dialog)

view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="보기(V)", underline=3, menu=view_menu)
bg_menu = tk.Menu(view_menu, tearoff=0)
view_menu.add_cascade(label="배경색", menu=bg_menu)
bg_menu.add_radiobutton(label="하얀색", variable=bg_var, value="white",  command=apply_bg)
bg_menu.add_radiobutton(label="핑크색", variable=bg_var, value="pink",   command=apply_bg)
bg_menu.add_radiobutton(label="노란색", variable=bg_var, value="yellow", command=apply_bg)

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="도움말(H)", underline=4, menu=help_menu)
help_menu.add_command(label="프로그램 정보", command=about_file)

# ---------- 단축키 ----------
shortcuts = {
    "n": new_file,
    "o": open_file,
    "s": save_file,
    "q": exit_app,
    "f": open_find_dialog,
    "h": open_find_dialog,
}
for key, func in shortcuts.items():
    text.bind(f"<Control-{key}>", func)
    text.bind(f"<Control-{key.upper()}>", func)
text.bind("<F3>", find_next)

text.bind("<KeyRelease>", update_status)       # 키보드로 이동/입력할 때
text.bind("<ButtonRelease-1>", update_status)  # 마우스로 클릭할 때
update_status()                                # 시작할 때 한 번 표시

root.mainloop()