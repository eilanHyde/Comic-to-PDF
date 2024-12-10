import os
import threading
from zipfile import ZipFile, ZIP_STORED
from PIL import Image
from natsort import natsorted
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# 获取当前主程序的根目录
def get_root_directory():
    return os.getcwd()

# 创建默认文件夹（输入和输出）
def create_default_folders():
    root_dir = get_root_directory()
    base_folder = os.path.join(root_dir, "comics")
    output_folder = os.path.join(root_dir, "output")

    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        print(f"默认输入文件夹已创建：{base_folder}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"默认输出文件夹已创建：{output_folder}")

    return base_folder, output_folder

# 获取所有子文件夹路径
def get_subfolders(base_folder):
    subfolders = []
    for root, dirs, _ in os.walk(base_folder):
        for dir_name in dirs:
            subfolders.append(os.path.join(root, dir_name))
    return subfolders

# 获取指定文件夹中的所有图片，并按自然顺序排序
def get_images_in_folder(folder_path):
    image_files = [
        os.path.join(folder_path, file_name)
        for file_name in os.listdir(folder_path)
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))
    ]
    return natsorted(image_files)

# 将图片合并为 PDF 文件
def create_pdf_from_images(image_files, output_pdf):
    images = []
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        except Exception as e:
            insert_log(f"错误：无法处理图片 {img_path}，原因：{e}\n")

    if images:
        try:
            images[0].save(output_pdf, save_all=True, append_images=images[1:], quality=100, optimize=False)
            insert_log(f"✅ PDF 已保存：{output_pdf}\n")
        except Exception as e:
            insert_log(f"❌ PDF 生成失败：{output_pdf}，原因：{e}\n")
    else:
        insert_log(f"⚠️ 未找到图片，跳过生成：{output_pdf}\n")

# 压缩文件夹为 ZIP
def zip_folder(folder_path, zip_name):
    zip_path = os.path.join(os.path.dirname(folder_path), f"{zip_name}.zip")
    with ZipFile(zip_path, 'w', compression=ZIP_STORED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    insert_log(f"📦 文件夹已打包为 ZIP：{zip_path}\n")

# 主函数：为每个漫画名称创建单独的 PDF 输出和 ZIP
def process_folders(base_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        insert_log(f"输出文件夹不存在，已创建：{output_folder}\n")

    insert_log(f"开始处理根目录：{base_folder}\n")
    comic_folders = [
        os.path.join(base_folder, folder)
        for folder in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, folder))
    ]
    insert_log(f"发现漫画数量：{len(comic_folders)}，漫画列表：{comic_folders}\n")

    for comic_folder in comic_folders:
        comic_name = os.path.basename(comic_folder)
        comic_output_folder = os.path.join(output_folder, comic_name)

        if not os.path.exists(comic_output_folder):
            os.makedirs(comic_output_folder)
            insert_log(f"创建漫画输出文件夹：{comic_output_folder}\n")

        insert_log(f"\n📚 正在处理漫画：{comic_name}\n")
        chapter_folders = get_subfolders(comic_folder)
        chapter_folders.insert(0, comic_folder)

        for chapter_folder in chapter_folders:
            chapter_name = os.path.basename(chapter_folder)
            insert_log(f"  📂 正在处理章节：{chapter_name}\n")

            image_files = get_images_in_folder(chapter_folder)
            if image_files:
                insert_log(f"  找到图片数量：{len(image_files)}，图片列表：{image_files}\n")
                output_pdf = os.path.join(comic_output_folder, f"{chapter_name}.pdf")
                create_pdf_from_images(image_files, output_pdf)
            else:
                insert_log(f"  ⚠️ 文件夹 {chapter_folder} 中未找到图片，跳过处理。\n")

        insert_log(f"🔄 开始压缩漫画目录：{comic_name}\n")
        zip_folder(comic_output_folder, comic_name)

# 插入日志并根据自动滚动设置进行滚动
def insert_log(message):
    log_text.insert(tk.END, message)
    if auto_scroll:
        log_text.see(tk.END)

# 创建GUI窗口
def create_gui():
    def browse_folder(entry_widget):
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_path)

    def open_folder(path):
        if path and os.path.exists(path):
            os.startfile(path)

    def start_processing():
        base_folder = base_folder_entry.get()
        output_folder = output_folder_entry.get()

        if not base_folder or not output_folder:
            messagebox.showwarning("警告", "请选择输入和输出文件夹路径")
            return

        start_button.config(state=tk.DISABLED)
        process_thread = threading.Thread(target=process_folders, args=(base_folder, output_folder))
        process_thread.start()

    def toggle_auto_scroll():
        global auto_scroll
        auto_scroll = auto_scroll_var.get()

    root = tk.Tk()
    root.title("comic-to-pdf")
    root.geometry('600x450')
    root.resizable(True, True)

    default_base_folder, default_output_folder = create_default_folders()

    tk.Label(root, text="输入文件夹：").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    base_folder_entry = tk.Entry(root, width=40)
    base_folder_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
    base_folder_entry.insert(0, default_base_folder)

    browse_base_folder_btn = tk.Button(root, text="浏览", command=lambda: browse_folder(base_folder_entry))
    browse_base_folder_btn.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    open_base_folder_btn = tk.Button(root, text="打开", command=lambda: open_folder(default_base_folder))
    open_base_folder_btn.grid(row=0, column=3, padx=5, pady=5, sticky="e")

    tk.Label(root, text="输出文件夹：").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    output_folder_entry = tk.Entry(root, width=40)
    output_folder_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
    output_folder_entry.insert(0, default_output_folder)

    browse_output_folder_btn = tk.Button(root, text="浏览", command=lambda: browse_folder(output_folder_entry))
    browse_output_folder_btn.grid(row=1, column=2, padx=5, pady=5, sticky="e")

    open_output_folder_btn = tk.Button(root, text="打开", command=lambda: open_folder(default_output_folder))
    open_output_folder_btn.grid(row=1, column=3, padx=5, pady=5, sticky="e")

    global start_button
    start_button = tk.Button(root, text="开始处理", command=start_processing)
    start_button.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

    global log_text
    log_text = tk.Text(root, width=70, height=15, wrap=tk.WORD)
    log_text.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

    log_scrollbar = tk.Scrollbar(root, command=log_text.yview)
    log_scrollbar.grid(row=3, column=4, sticky="ns")
    log_text.config(yscrollcommand=log_scrollbar.set)

    global auto_scroll
    auto_scroll = True
    auto_scroll_var = tk.BooleanVar(value=auto_scroll)
    auto_scroll_checkbox = tk.Checkbutton(root, text="自动滚动", variable=auto_scroll_var, command=toggle_auto_scroll)
    auto_scroll_checkbox.grid(row=4, column=0, columnspan=4, pady=5, sticky="w")

    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(1, weight=1)

    root.mainloop()

# 启动GUI
create_gui()
# BY:Eilan