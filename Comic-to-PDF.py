import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from zipfile import ZipFile, ZIP_STORED
from PIL import Image
from natsort import natsorted
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json

class Config:
    """配置管理类"""
    DEFAULT_CONFIG = {
        'max_workers': min(os.cpu_count() or 4, 8),
        'optimize_pdf': False,
        'image_quality': 100,
        'generate_pdf': True,
        'merge_to_long_image': False,
        'auto_scroll': True,
        'last_input_folder': '',
        'last_output_folder': ''
    }
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败：{e}")
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败：{e}")
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class Logger:
    """日志管理类"""
    def __init__(self, text_widget, auto_scroll_var):
        self.text_widget = text_widget
        self.auto_scroll_var = auto_scroll_var
    
    def log(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.update_idletasks()
        self.text_widget.tag_configure("emoji", font=("Segoe UI Emoji", 10))
        self.text_widget.tag_add("emoji", "1.0", tk.END)
        if self.auto_scroll_var.get():
            self.text_widget.yview_moveto(1.0)
    
    def clear(self):
        self.text_widget.delete(1.0, tk.END)
    
    def export(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_widget.get(1.0, tk.END))
                messagebox.showinfo("成功", "日志导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出日志失败：{str(e)}")

class FileProcessor:
    """文件处理类"""
    def __init__(self, config, logger, progress_bar=None, progress_label=None, gui_root=None, start_button=None, stop_button=None):
        self.config = config
        self.logger = logger
        self.stop_flag = False
        self.progress_bar = progress_bar
        self.progress_label = progress_label
        self.gui_root = gui_root
        self.start_button = start_button
        self.stop_button = stop_button
        self.executor = None  # 添加线程池引用
        
    # 获取当前主程序的根目录
    def get_root_directory(self):
        return os.getcwd()

    # 创建默认文件夹（输入和输出）
    def create_default_folders(self):
        root_dir = self.get_root_directory()
        base_folder = os.path.join(root_dir, "input")  # 修改为 "input"
        output_folder = os.path.join(root_dir, "output")

        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
            self.logger.log(f"默认输入文件夹已创建：{base_folder}\n")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            self.logger.log(f"默认输出文件夹已创建：{output_folder}\n")

        return base_folder, output_folder

    # 获取所有子文件夹路径
    def get_subfolders(self, base_folder):
        subfolders = []
        for root, dirs, _ in os.walk(base_folder):
            for dir_name in dirs:
                subfolders.append(os.path.join(root, dir_name))
        return subfolders

    # 获取指定文件夹中的所有图片，并按自然顺序排序
    def get_images_in_folder(self, folder_path):
        image_files = [
            os.path.join(folder_path, file_name)
            for file_name in os.listdir(folder_path)
            if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))
        ]
        return natsorted(image_files)

    # 将图片合并为 PDF 文件
    def create_pdf_from_images(self, image_files, output_pdf):
        images = []
        for img_path in image_files:
            try:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                self.logger.log(f"错误：无法处理图片 {img_path}，原因：{e}\n")

        if images:
            try:
                images[0].save(
                    output_pdf, 
                    save_all=True, 
                    append_images=images[1:], 
                    quality=self.config.get('image_quality'),
                    optimize=self.config.get('optimize_pdf')
                )
                self.logger.log(f"✅ PDF 已保存：{output_pdf}\n")
            except Exception as e:
                self.logger.log(f"❌ PDF 生成失败：{output_pdf}，原因：{e}\n")
        else:
            self.logger.log(f"⚠️ 未找到图片，跳过生成：{output_pdf}\n")

    # 压缩文件夹为 ZIP
    def zip_folder(self, folder_path, zip_name):
        zip_path = os.path.join(os.path.dirname(folder_path), f"{zip_name}.zip")
        with ZipFile(zip_path, 'w', compression=ZIP_STORED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        self.logger.log(f"📦 文件夹已打包为 ZIP：{zip_path}\n")

    # 将图片纵向合并为一张长图
    def create_long_image_from_images(self, image_files, output_long_image):
        if not image_files:
            self.logger.log(f"⚠️ 未找到图片，跳过生成：{output_long_image}\n")
            return

        try:
            # 计算尺寸时复用已打开的图片对象
            images_info = []
            max_width = 0
            total_height = 0
            
            # 批量处理图片信息
            for img_path in image_files:
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                        max_width = max(max_width, width)
                        total_height += height
                        images_info.append((img_path, width, height))
                except Exception as e:
                    self.logger.log(f"错误：无法读取图片 {img_path}，原因：{e}\n")
                    continue

            if not images_info:
                self.logger.log(f"⚠️ 没有可用的图片，跳过生成：{output_long_image}\n")
                return

            # 创建目标长图
            long_image = Image.new('RGB', (max_width, total_height))
            y_offset = 0

            # 分批处理图片以优化内存使用
            BATCH_SIZE = 5
            for i in range(0, len(images_info), BATCH_SIZE):
                batch = images_info[i:i + BATCH_SIZE]
                
                for img_path, width, height in batch:
                    try:
                        with Image.open(img_path) as img:
                            # 如果图片模式不是RGB，进行转换
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # 调整图片大小
                            if width != max_width:
                                ratio = max_width / width
                                new_height = int(height * ratio)
                                img = img.resize((max_width, new_height), Image.LANCZOS)
                                height = new_height
                            
                            # 粘贴到长图上
                            long_image.paste(img, (0, y_offset))
                            y_offset += height
                            
                            # 主动释放内存
                            img = None
                    except Exception as e:
                        self.logger.log(f"错误：处理图片失败 {img_path}，原因：{e}\n")
                        continue

            # 保存结果
            long_image.save(output_long_image, format='PNG', optimize=True)
            self.logger.log(f"✅ 长图已保存：{output_long_image}\n")
            
            # 清理内存
            long_image = None

        except Exception as e:
            self.logger.log(f"❌ 长图生成失败：{output_long_image}，原因：{e}\n")
        finally:
            # 确保清理所有可能的引用
            import gc
            gc.collect()

    # 在文件开头添加全局变量
    stop_processing_flag = False
    processing_thread = None

    # 添加新的处理函数用于并行处理单个章节
    def process_single_chapter(self, chapter_info):
        try:
            chapter_folder, pdf_output_folder, long_output_folder, generate_pdf, merge_to_long_image = chapter_info
            chapter_name = os.path.basename(chapter_folder)
            result_message = f"  📂 处理章节：{chapter_name}\n"
            
            image_files = self.get_images_in_folder(chapter_folder)
            if not image_files:
                return result_message + f"  ⚠️ 文件夹 {chapter_folder} 中未找到图片，跳过处理。\n"
                
            result_message += f"  找到图片数量：{len(image_files)}\n"

            # 处理 PDF
            if generate_pdf and pdf_output_folder:
                output_pdf = os.path.join(pdf_output_folder, f"{chapter_name}.pdf")
                if not os.path.exists(output_pdf):
                    self.create_pdf_from_images(image_files, output_pdf)

            # 处理长图
            if merge_to_long_image and long_output_folder:
                output_long_image = os.path.join(long_output_folder, f"{chapter_name}_long.png")
                if not os.path.exists(output_long_image):
                    self.create_long_image_from_images(image_files, output_long_image)

            return result_message
        except Exception as e:
            return f"  ❌ 处理章节 {os.path.basename(chapter_folder)} 时出错：{str(e)}\n"

    def process_folders(self, base_folder, output_folder, generate_pdf, merge_to_long_image):
        global stop_processing_flag
        stop_processing_flag = False
        
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.logger.log(f"输出文件夹不存在，已创建：{output_folder}\n")

            self.logger.log(f"开始处理根目录：{base_folder}\n")
            comic_folders = [
                os.path.join(base_folder, folder)
                for folder in os.listdir(base_folder)
                if os.path.isdir(os.path.join(base_folder, folder))
            ]
            self.logger.log(f"发现漫画数量：{len(comic_folders)}\n")

            # 创建线程池，根据CPU核心数设置线程数
            max_workers = self.config.get('max_workers')
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            
            total_tasks = sum(len(self.get_subfolders(comic_folder)) + 1 for comic_folder in comic_folders)
            if self.progress_bar:
                self.progress_bar['maximum'] = total_tasks
                self.progress_bar['value'] = 0
            completed_tasks = 0

            for comic_folder in comic_folders:
                if stop_processing_flag:
                    self.logger.log("⚠️ 用户取消处理\n")
                    if self.executor:
                        self.executor.shutdown(wait=False)
                    break

                comic_name = os.path.basename(comic_folder)
                # 为PDF和长图分别创建输出文件夹
                comic_output_folder_pdf = os.path.join(output_folder, f"{comic_name}_pdf") if generate_pdf else None
                comic_output_folder_long = os.path.join(output_folder, f"{comic_name}_long") if merge_to_long_image else None

                # 检查是否需要处理
                need_process_pdf = False
                need_process_long = False
                if generate_pdf or merge_to_long_image:
                    for chapter_folder in self.get_subfolders(comic_folder) + [comic_folder]:
                        chapter_name = os.path.basename(chapter_folder)
                        if generate_pdf and (not comic_output_folder_pdf or 
                            not os.path.exists(os.path.join(comic_output_folder_pdf, f"{chapter_name}.pdf"))):
                            need_process_pdf = True
                        if merge_to_long_image and (not comic_output_folder_long or 
                            not os.path.exists(os.path.join(comic_output_folder_long, f"{chapter_name}_long.png"))):
                            need_process_long = True
                        if need_process_pdf and need_process_long:
                            break

                if not need_process_pdf and not need_process_long:
                    self.logger.log(f"📂 漫画 {comic_name} 已完全处理，跳过。\n")
                    if self.progress_bar and self.progress_label and self.gui_root:
                        self.progress_bar['value'] += len(self.get_subfolders(comic_folder)) + 1
                        self.gui_root.update_idletasks()
                    continue

                # 创建所需的输出文件夹
                if generate_pdf and need_process_pdf:
                    os.makedirs(comic_output_folder_pdf, exist_ok=True)
                if merge_to_long_image and need_process_long:
                    os.makedirs(comic_output_folder_long, exist_ok=True)

                self.logger.log(f"\n📚 正在处理漫画：{comic_name}\n")
                chapter_folders = self.get_subfolders(comic_folder)
                chapter_folders.insert(0, comic_folder)

                # 并行处理章节
                try:
                    # 创建任务列表和跟踪字典
                    futures = []
                    future_to_chapter = {}
                    for chapter_folder in chapter_folders:
                        if self.stop_flag:
                            break
                        future = self.executor.submit(
                            self.process_single_chapter,
                            (chapter_folder, 
                             comic_output_folder_pdf if generate_pdf else None,
                             comic_output_folder_long if merge_to_long_image else None,
                             generate_pdf, 
                             merge_to_long_image)
                        )
                        futures.append(future)
                        future_to_chapter[future] = chapter_folder

                    # 处理完成的任务结果
                    for future in as_completed(futures):
                        if self.stop_flag:
                            for f in futures:
                                f.cancel()
                            break
                        chapter_folder = future_to_chapter[future]
                        try:
                            result = future.result()
                            self.logger.log(result)
                        except Exception as e:
                            self.logger.log(f"  ❌ 处理失败 {os.path.basename(chapter_folder)}：{str(e)}\n")
                        
                        completed_tasks += 1
                        if self.progress_bar and self.progress_label and self.gui_root:
                            self.progress_bar['value'] = completed_tasks
                            self.progress_label.config(text=f"{int((completed_tasks / total_tasks) * 100)}%")
                            self.gui_root.update_idletasks()

                except Exception as e:
                    self.logger.log(f"处理失败：{str(e)}\n")
                    if self.stop_flag:
                        break

                if not stop_processing_flag:
                    # 分别为PDF和长图版本创建ZIP
                    if generate_pdf and need_process_pdf:
                        self.logger.log(f"🔄 开始压缩PDF目录：{comic_name}\n")
                        self.zip_folder(comic_output_folder_pdf, f"{comic_name}_pdf")
                    if merge_to_long_image and need_process_long:
                        self.logger.log(f"🔄 开始压缩长图目录：{comic_name}\n")
                        self.zip_folder(comic_output_folder_long, f"{comic_name}_long")

                completed_tasks += 1
                if self.progress_bar and self.progress_label and self.gui_root:
                    self.progress_bar['value'] = completed_tasks
                    self.progress_label.config(text=f"{int((completed_tasks / total_tasks) * 100)}%")
                    self.gui_root.update_idletasks()

            if not stop_processing_flag:
                self.logger.log("🎉 所有漫画处理完成！\n")
                if self.progress_bar and self.progress_label:
                    self.progress_bar['value'] = self.progress_bar['maximum']
                    self.progress_label.config(text="100%")
                messagebox.showinfo("完成", "所有漫画已处理完成！")

        except Exception as e:
            self.logger.log(f"❌ 处理过程出现错误：{str(e)}\n")
        finally:
            # 确保线程池被正确关闭
            if self.executor:
                self.executor.shutdown(wait=False)
            self.executor = None
            if self.gui_root and self.start_button and self.stop_button:
                self.gui_root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                self.gui_root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

    def stop_processing(self):
        """改进的停止处理方法"""
        self.stop_flag = True
        if self.executor:
            self.executor.shutdown(wait=False)
        self.executor = None

class GUI:
    """GUI管理类"""
    def __init__(self):
        self.root = tk.Tk()
        self.config = Config()
        
        # 初始化所有界面组件
        self.init_gui()
        
        # 创建日志实例
        self.logger = Logger(self.log_text, self.auto_scroll_var)
        
        # 创建文件处理器实例
        self.file_processor = FileProcessor(
            self.config,
            self.logger,
            progress_bar=self.progress_bar,
            progress_label=self.progress_label,
            gui_root=self.root,
            start_button=self.start_button,
            stop_button=self.stop_button
        )
        
        # 创建默认文件夹并更新输入输出路径
        default_input, default_output = self.file_processor.create_default_folders()
        
        # 如果配置中没有保存过路径，则使用默认路径
        if not self.config.get('last_input_folder'):
            self.config.set('last_input_folder', default_input)
            self.base_folder_entry.delete(0, tk.END)
            self.base_folder_entry.insert(0, default_input)
            
        if not self.config.get('last_output_folder'):
            self.config.set('last_output_folder', default_output)
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, default_output)
        
    def init_gui(self):
        self.root.title("comic-to-pdf")
        self.root.geometry('700x600')
        self.root.resizable(True, True)
        
        # 配置根窗口的grid权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 初始化所有界面组件
        self.init_variables()
        self.create_main_interface()
        self.bind_events()
        
    def init_variables(self):
        # 从配置中初始化所有变量
        self.max_workers_var = tk.IntVar(value=self.config.get('max_workers'))
        self.optimize_pdf_var = tk.BooleanVar(value=self.config.get('optimize_pdf'))
        self.image_quality_var = tk.IntVar(value=self.config.get('image_quality'))
        self.generate_pdf_var = tk.BooleanVar(value=self.config.get('generate_pdf'))
        self.merge_to_long_image_var = tk.BooleanVar(value=self.config.get('merge_to_long_image'))
        self.auto_scroll_var = tk.BooleanVar(value=self.config.get('auto_scroll'))
        
    def create_main_interface(self):
        # 创建notebook并配置权重
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 创建主框架并设置其grid权重
        main_frame = ttk.Frame(self.notebook)
        main_frame.grid_rowconfigure(3, weight=1)  # 日志区域可扩展
        main_frame.grid_columnconfigure(1, weight=1)  # 输入输出框可扩展
        
        self.notebook.add(main_frame, text="主界面")
        
        # 创建各个部分
        self.create_folder_controls(main_frame)
        self.create_action_buttons(main_frame)
        self.create_log_area(main_frame)
        self.create_progress_controls(main_frame)
        self.create_conversion_options(main_frame)
        
        # 创建设置和关于标签页
        self.create_settings_tab(self.notebook)  
        self.create_about_tab(self.notebook)     
        
    def create_folder_controls(self, main_frame):
        """创建文件夹选择控件"""
        # 输入文件夹控件
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        folder_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(folder_frame, text="输入文件夹：").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.base_folder_entry = tk.Entry(folder_frame, width=50)
        self.base_folder_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.base_folder_entry.insert(0, self.config.get('last_input_folder'))

        browse_base_folder_btn = tk.Button(folder_frame, text="浏览", command=lambda: self.browse_folder(self.base_folder_entry))
        browse_base_folder_btn.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        open_base_folder_btn = tk.Button(folder_frame, text="打开", command=lambda: self.open_folder(self.config.get('last_input_folder')))
        open_base_folder_btn.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        tk.Label(folder_frame, text="输出文件夹：").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_folder_entry = tk.Entry(folder_frame, width=50)
        self.output_folder_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.output_folder_entry.insert(0, self.config.get('last_output_folder'))

        browse_output_folder_btn = tk.Button(folder_frame, text="浏览", command=lambda: self.browse_folder(self.output_folder_entry))
        browse_output_folder_btn.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        open_output_folder_btn = tk.Button(folder_frame, text="打开", command=lambda: self.open_folder(self.config.get('last_output_folder')))
        open_output_folder_btn.grid(row=1, column=3, padx=5, pady=5, sticky="e")
        
    def create_action_buttons(self, main_frame):
        """创建操作按钮"""
        self.start_button = tk.Button(main_frame, text="开始处理", command=self.start_processing)
        self.start_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.stop_button = tk.Button(main_frame, text="停止处理", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

        clear_log_button = tk.Button(main_frame, text="清除日志", command=self.clear_log)
        clear_log_button.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        export_log_button = tk.Button(main_frame, text="导出日志", command=self.export_log)
        export_log_button.grid(row=2, column=4, padx=10, pady=5, sticky="ew")
        
    def create_log_area(self, main_frame):
        """创建日志显示区域"""
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=3, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
    def create_progress_controls(self, main_frame):
        """创建进度条和进度标签"""
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=600, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

        self.progress_label = tk.Label(main_frame, text="0%")
        self.progress_label.grid(row=5, column=4, padx=10, pady=5, sticky="e")
        
    def create_conversion_options(self, main_frame):
        """创建转换选项复选框"""
        self.generate_pdf_var = tk.BooleanVar(value=True)
        generate_pdf_checkbox = tk.Checkbutton(main_frame, text="合并为PDF", variable=self.generate_pdf_var)
        generate_pdf_checkbox.grid(row=6, column=0, columnspan=5, pady=5, sticky="w")

        self.merge_to_long_image_var = tk.BooleanVar(value=False)  # 修复：将 value() 改为 value=
        merge_to_long_image_checkbox = tk.Checkbutton(main_frame, text="合并为长图", variable=self.merge_to_long_image_var)
        merge_to_long_image_checkbox.grid(row=7, column=0, columnspan=5, pady=5, sticky="w")
        
    def create_settings_tab(self, notebook):
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="设置")
        
        # 并行处理设置
        parallel_frame = ttk.LabelFrame(settings_frame, text="并行处理设置")
        parallel_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(parallel_frame, text="最大并行处理数:").pack(side="left", padx=5)
        max_workers_spin = ttk.Spinbox(
            parallel_frame, 
            from_=1, 
            to=16, 
            width=5, 
            textvariable=self.max_workers_var
        )
        max_workers_spin.pack(side="left", padx=5)
        
        # PDF设置
        pdf_frame = ttk.LabelFrame(settings_frame, text="PDF设置")
        pdf_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Checkbutton(
            pdf_frame, 
            text="优化PDF大小（可能降低质量）", 
            variable=self.optimize_pdf_var
        ).pack(padx=5, pady=2)
        
        # 图像设置
        image_frame = ttk.LabelFrame(settings_frame, text="图像设置")
        image_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(image_frame, text="图像质量(1-100):").pack(side="left", padx=5)
        quality_spin = ttk.Spinbox(
            image_frame,
            from_=1,
            to=100,
            width=5,
            textvariable=self.image_quality_var
        )
        quality_spin.pack(side="left", padx=5)
        
    def create_about_tab(self, notebook):
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="关于")
        
        # 添加关于信息
        about_text = """
    Comic-to-PDF 转换工具

    版本: 1.2.0
    作者: Eilan Hyde
    GitHub: https://github.com/eilanHyde/Comic-to-PDF

    功能特点:
    - 支持批量转换漫画为PDF
    - 支持合并为长图
    - 多线程并行处理

    使用说明:
    1. 选择输入文件夹（包含漫画章节）
    2. 选择输出文件夹
    3. 选择处理方式（PDF/长图）
    4. 点击开始处理

    如有问题或建议，欢迎在GitHub提出Issue。
        """
        
        text_widget = tk.Text(about_frame, wrap=tk.WORD, width=50, height=20)
        text_widget.pack(padx=10, pady=10, expand=True, fill="both")
        text_widget.insert("1.0", about_text)
        text_widget.config(state="disabled")
        
    def bind_events(self):
        """绑定所有事件处理函数"""
        def on_setting_changed(*args):
            self.config.set('max_workers', self.max_workers_var.get())
            self.config.set('optimize_pdf', self.optimize_pdf_var.get())
            self.config.set('image_quality', self.image_quality_var.get())
            self.config.set('generate_pdf', self.generate_pdf_var.get())
            self.config.set('merge_to_long_image', self.merge_to_long_image_var.get())
            self.config.set('auto_scroll', self.auto_scroll_var.get())

        self.max_workers_var.trace_add('write', on_setting_changed)
        self.optimize_pdf_var.trace_add('write', on_setting_changed)
        self.image_quality_var.trace_add('write', on_setting_changed)
        self.generate_pdf_var.trace_add('write', on_setting_changed)
        self.merge_to_long_image_var.trace_add('write', on_setting_changed)
        self.auto_scroll_var.trace_add('write', on_setting_changed)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def browse_folder(self, entry):
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry.delete(0, tk.END)
            entry.insert(0, folder_path)
            
    def open_folder(self, folder_path):
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showwarning("警告", f"文件夹不存在：{folder_path}")
            
    def toggle_auto_scroll(self):
        self.config.set('auto_scroll', self.auto_scroll_var.get())
        
    def clear_log(self):
        self.logger.clear()
        
    def export_log(self):
        self.logger.export()
        
    def start_processing(self):
        base_folder = self.base_folder_entry.get()
        output_folder = self.output_folder_entry.get()
        generate_pdf = self.generate_pdf_var.get()
        merge_to_long_image = self.merge_to_long_image_var.get()

        if not base_folder or not output_folder:
            messagebox.showwarning("警告", "请选择输入和输出文件夹路径")
            return

        if not generate_pdf and not merge_to_long_image:
            messagebox.showwarning("警告", "请至少选择一种处理方式")
            return

        self.file_processor = FileProcessor(
            self.config,
            self.logger,
            progress_bar=self.progress_bar,
            progress_label=self.progress_label,
            gui_root=self.root,
            start_button=self.start_button,
            stop_button=self.stop_button
        )
        self.file_processor.stop_flag = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 如果存在旧的处理线程，等待其完成
        if self.file_processor.processing_thread and self.file_processor.processing_thread.is_alive():
            self.file_processor.processing_thread.join(timeout=0.1)
        
        self.file_processor.processing_thread = threading.Thread(
            target=self.file_processor.process_folders,
            args=(base_folder, output_folder, generate_pdf, merge_to_long_image)
        )
        self.file_processor.processing_thread.daemon = True  # 设置为守护线程
        self.file_processor.processing_thread.start()
        
    def stop_processing(self):
        """改进的停止处理方法"""
        if self.file_processor:
            self.file_processor.stop_processing()  # 使用新的停止方法
            self.logger.log("⚠️ 正在停止处理...\n")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        
    def on_closing(self):
        if self.file_processor and self.file_processor.processing_thread and self.file_processor.processing_thread.is_alive():
            self.file_processor.stop_flag = True
            self.file_processor.processing_thread.join(timeout=1.0)
        self.config.save_config()  # 退出前保存配置
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

def main():
    # 创建并运行GUI
    app = GUI()
    app.run()

if __name__ == "__main__":
    main()


