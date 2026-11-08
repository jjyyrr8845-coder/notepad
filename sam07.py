import tkinter as tk
from tkinter import messagebox, simpledialog

# ---------- 열 너비 조절이 되는 표 ----------
GRID_COLOR = "#888888"     # 표 테두리 색

class ResizableTable(tk.Frame):
    def __init__(self, master, rows, cols, font=None, col_width=90):
        # 배경을 회색으로 두고 칸 사이에 1px 틈을 주면 테두리 선처럼 보여요
        super().__init__(master, bg=GRID_COLOR, padx=1, pady=1)
        self.font = font
        self.rows = 0
        self.cols = 0
        self.widths = []
        self.cells = []        # cells[행][열] = Entry
        self._parts = []       # 다시 그릴 때 지울 부품들 (칸 + 손잡이)
        self._pos = (0, 0)     # 우클릭한 칸의 위치
        self._drag = (0, 0)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="아래에 행 추가", command=self.add_row)
        self.menu.add_command(label="오른쪽에 열 추가", command=self.add_col)
        self.menu.add_separator()
        self.menu.add_command(label="이 행 삭제", command=self.del_row)
        self.menu.add_command(label="이 열 삭제", command=self.del_col)

        data = [[""] * cols for _ in range(rows)]
        self.rebuild(data, [col_width] * cols)

    # --- 표 그리기 ---
    def rebuild(self, data, widths):
        for w in self._parts:
            w.destroy()
        for i in range(2 * max(self.cols, len(widths)) + 2):   # 예전 열 설정 초기화
            self.grid_columnconfigure(i, minsize=0)

        self._parts = []
        self.cells = []
        self.rows, self.cols = len(data), len(widths)
        self.widths = list(widths)

        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                opts = {"width": 1, "relief": "flat", "bd": 0,
                        "highlightthickness": 0, "bg": "white"}
                if self.font:
                    opts["font"] = self.font
                e = tk.Entry(self, **opts)
                e.insert(0, data[r][c])
                e.grid(row=r, column=2 * c, sticky="nsew", pady=(0, 1))
                e.bind("<Button-3>", lambda ev, r=r, c=c: self._popup(ev, r, c))
                e.bind("<Return>", lambda ev, r=r, c=c: self._enter(r, c))
                row_cells.append(e)
                self._parts.append(e)
            self.cells.append(row_cells)

        for c in range(self.cols):
            self.grid_columnconfigure(2 * c, minsize=self.widths[c])
            grip = tk.Frame(self, width=4, bg=GRID_COLOR, cursor="sb_h_double_arrow")
            grip.grid(row=0, column=2 * c + 1, rowspan=self.rows, sticky="ns")
            grip.bind("<ButtonPress-1>", lambda ev, c=c: self._grip_start(ev, c))
            grip.bind("<B1-Motion>", lambda ev, c=c: self._grip_drag(ev, c))
            self._parts.append(grip)

    # --- 열 너비 조절 ---
    def _grip_start(self, event, c):
        self._drag = (event.x_root, self.widths[c])

    def _grip_drag(self, event, c):
        x0, w0 = self._drag
        self.widths[c] = max(30, w0 + event.x_root - x0)       # 최소 30px
        self.grid_columnconfigure(2 * c, minsize=self.widths[c])

    # --- 키보드 / 우클릭 ---
    def _enter(self, r, c):
        if r + 1 < self.rows:
            self.cells[r + 1][c].focus_set()                   # Enter = 아래 칸으로
        return "break"

    def _popup(self, event, r, c):
        self._pos = (r, c)
        self.menu.tk_popup(event.x_root, event.y_root)

    # --- 행/열 편집 ---
    def get_data(self):
        return [[e.get() for e in row] for row in self.cells]

    def add_row(self):
        r, _ = self._pos
        data = self.get_data()
        data.insert(r + 1, [""] * self.cols)
        self.rebuild(data, self.widths)

    def add_col(self):
        _, c = self._pos
        data = self.get_data()
        for row in data:
            row.insert(c + 1, "")
        widths = self.widths[:]
        widths.insert(c + 1, 90)
        self.rebuild(data, widths)

    def del_row(self):
        if self.rows <= 1:
            return
        r, _ = self._pos
        data = self.get_data()
        del data[r]
        self.rebuild(data, self.widths)

    def del_col(self):
        if self.cols <= 1:
            return
        _, c = self._pos
        data = self.get_data()
        for row in data:
            del row[c]
        widths = self.widths[:]
        del widths[c]
        self.rebuild(data, widths)

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

# ---------- 표 삽입 ----------
def insert_table(event=None):
    rows = simpledialog.askinteger("표 삽입", "행 수:", parent=root,
                                   minvalue=1, maxvalue=30, initialvalue=3)
    if rows is None:
        return "break"
    cols = simpledialog.askinteger("표 삽입", "열 수:", parent=root,
                                   minvalue=1, maxvalue=10, initialvalue=3)
    if cols is None:
        return "break"

    table = ResizableTable(text, rows, cols, font=text.cget("font"))
    text.window_create(tk.INSERT, window=table)    # 커서 위치에 표 끼워 넣기
    text.insert(tk.INSERT, "\n")                   # 표 아래에 이어서 쓸 줄 만들기
    return "break"

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

# ---------- 유선노트 ----------
RULE_COLOR = "#a9c4e8"    # 연한 파란 선 (하양/핑크/노랑 배경 모두 잘 어울려요)
ruled_lines = []          # 선으로 쓰는 얇은 Frame들을 모아두는 리스트

def update_ruled(*args):
    if not ruled_var.get():
        return
    info = text.dlineinfo("@0,0")        # 화면 맨 위 줄의 (x, y, 너비, 높이, 기준선)
    if not info:
        return
    y0, h = info[1], info[3]             # 맨 위 줄의 y좌표, 한 줄의 높이
    if h <= 0:
        return

    count = text.winfo_height() // h + 2          # 화면을 채울 선 개수
    while len(ruled_lines) < count:               # 부족하면 선 추가
        ruled_lines.append(tk.Frame(text, height=1, bg=RULE_COLOR))

    for i, line in enumerate(ruled_lines):
        if i < count:
            line.place(x=0, y=y0 + (i + 1) * h - 1, relwidth=1, height=1)
        else:
            line.place_forget()                   # 남는 선은 숨기기

def toggle_ruled():
    if ruled_var.get():
        update_ruled()
    else:
        for line in ruled_lines:
            line.place_forget()               # 끄면 모든 선 숨기기

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
ruled_var = tk.BooleanVar(value=False)    # 유선노트 켜짐/꺼짐 (기본: 꺼짐)
status_var = tk.StringVar(value="1줄, 1열")
status_bar = tk.Label(root, textvariable=status_var, anchor="e", relief="sunken", padx=8)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

text = tk.Text(root, wrap="word", undo=True,
               font=("맑은 고딕",13),
               spacing1=8, spacing2=8, spacing3=0)      # undo=True: Ctrl+Z로 되돌리기 가능
text.config(yscrollcommand=lambda *args: update_ruled())   # 스크롤될 때마다 선 위치 갱신
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
edit_menu.add_separator()
edit_menu.add_command(label="표 삽입...", accelerator="Ctrl+T", command=insert_table)

view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="보기(V)", underline=3, menu=view_menu)
bg_menu = tk.Menu(view_menu, tearoff=0)
view_menu.add_cascade(label="배경색", menu=bg_menu)
bg_menu.add_radiobutton(label="하얀색", variable=bg_var, value="white",  command=apply_bg)
bg_menu.add_radiobutton(label="핑크색", variable=bg_var, value="pink",   command=apply_bg)
bg_menu.add_radiobutton(label="노란색", variable=bg_var, value="yellow", command=apply_bg)
view_menu.add_separator()
view_menu.add_checkbutton(label="유선노트", variable=ruled_var, command=toggle_ruled)

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
    "t": insert_table
}
for key, func in shortcuts.items():
    text.bind(f"<Control-{key}>", func)
    text.bind(f"<Control-{key.upper()}>", func)
text.bind("<F3>", find_next)
text.bind("<Configure>", lambda e: update_ruled())   # 창 크기가 바뀔 때 선 다시 배치

text.bind("<KeyRelease>", update_status)       # 키보드로 이동/입력할 때
text.bind("<ButtonRelease-1>", update_status)  # 마우스로 클릭할 때
update_status()                                # 시작할 때 한 번 표시

root.mainloop()