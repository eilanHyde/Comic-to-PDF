#### **项目名称**: comic-to-pdf

**描述**:
comic-to-pdf是一个基于 Python 的图形界面工具，用于将漫画文件夹中的图片转换为 PDF 文件并打包为 ZIP 文件。该工具支持自动处理所有子文件夹中的图片，生成各章节的 PDF 文件，并将整个漫画目录压缩为一个 ZIP 文件。界面友好，适用于批量处理漫画图片，方便漫画作者和爱好者的管理和分享。

---

### **主要功能**:
1. **自动化处理**: 自动遍历漫画目录及其子目录，找到所有图片，并按章节生成 PDF 文件。
2. **PDF 文件生成**: 根据图片创建符合标准的 PDF 文件，每个章节一个 PDF。
3. **ZIP 文件打包**: 每个漫画目录压缩为一个 ZIP 文件，以便于分享和存储。
4. **界面与日志输出**: 图形界面简洁，提供操作反馈和日志记录功能，支持自动滚动日志显示。


### **使用说明**:
- **输入文件夹**: 选择包含漫画图片的文件夹。
- **输出文件夹**: 选择保存 PDF 和 ZIP 文件的文件夹。
- **日志输出**: 操作过程中的日志信息会在日志框中显示，支持自动滚动。

---

### **运行环境**

#### **1. 必需的运行环境**
- **操作系统**: Windows、macOS 或 Linux。
- **Python 版本**: Python 3.8 或更高版本。

#### **2. 所需的第三方库**
以下库需要通过 `pip` 安装：
- **Pillow**: 用于处理图像（支持 JPG、PNG 等格式）。
- **natsort**: 用于自然排序文件名。
- **tkinter**: 标准 Python GUI 库，通常随 Python 安装。

#### **3. 安装依赖**
运行以下命令以安装必要的库：
```bash
pip install pillow natsort
```

#### **4. 硬件需求**
- 推荐 4GB 内存及以上，特别是处理高分辨率图片时。
- 硬盘需要足够空间存储临时文件和生成的 PDF、ZIP 文件。

---

### **使用文档**

#### **功能概述**
该程序用于将漫画图片文件批量合并为 PDF 文件，并为每本漫画创建独立的压缩包（ZIP 文件）。通过简单的图形化界面（GUI），用户可以：
1. 设置输入文件夹和输出文件夹。
2. 查看操作日志。
3. 执行批量处理，并生成结果。

---

#### **文件夹结构要求**
- **输入文件夹（`comics`）**: 每本漫画作为一个独立文件夹，文件夹内可以包含多个子文件夹（每个子文件夹代表章节）。
  - 示例结构：
    ```
    comics/
    ├── 漫画A/
    │   ├── 第1章/
    │   │   ├── 01.jpg
    │   │   ├── 02.jpg
    │   ├── 第2章/
    │       ├── 01.jpg
    ├── 漫画B/
        ├── 01.png
        ├── 02.png
    ```
- **输出文件夹（`output`）**: 用于保存生成的 PDF 文件和 ZIP 压缩包。

---

#### **操作步骤**

1. **启动程序**
   双击运行 `comic-to-pdf.py` 文件，或者在终端输入：
   ```bash
   python comic-to-pdf.py
   ```

2. **选择输入和输出文件夹**
   - 默认输入文件夹为程序根目录下的 `comics`。
   - 默认输出文件夹为程序根目录下的 `output`。
   - 可通过点击 “浏览” 按钮更改文件夹路径。

3. **检查输入文件夹结构**
   确保输入文件夹符合上述文件夹结构要求，图片文件为常见格式（如 PNG、JPG 等）。

4. **点击 “开始处理”**
   - 程序会依次读取每本漫画文件夹，将其中的图片合并为 PDF 文件，并生成 ZIP 压缩包。
   - 处理进度和日志会实时显示在日志框中。

5. **日志窗口**
   - 查看操作日志（支持自动滚动）。
   - 可取消勾选 "自动滚动" 以固定日志查看位置。

6. **检查结果**
   - 输出文件夹中，每本漫画对应一个子文件夹，包含 PDF 文件和 ZIP 压缩包。

---

#### **示例**
假设输入文件夹结构如下：
```
comics/
├── 漫画A/
│   ├── 第1章/
│   │   ├── 01.jpg
│   │   ├── 02.jpg
│   ├── 第2章/
│       ├── 01.jpg
├── 漫画B/
    ├── 01.png
    ├── 02.png
```

执行后，输出文件夹 `output/` 将生成以下内容：
```
output/
├── 漫画A/
│   ├── 第1章.pdf
│   ├── 第2章.pdf
│   └── 漫画A.zip
├── 漫画B/
    ├── 漫画B.pdf
    └── 漫画B.zip
```

---

#### **注意事项**
1. **文件名排序问题**:
   - 图片文件按自然顺序排序。如果顺序不对，请检查文件名。
   - 推荐命名方式：`01.jpg`、`02.jpg`。

2. **文件格式支持**:
   - 图片格式支持：JPG、PNG、JPEG、WEBP。
   - 非支持文件会被跳过。

3. **可能的异常**:
   - **PDF 生成失败**: 检查图片文件是否损坏或不支持的格式。
   - **输出路径不可用**: 确保有写权限，路径有效。

4. **程序性能**:
   - 对于大量高分辨率图片，可能会消耗较多内存和时间。

---

### **贡献**:
欢迎任何形式的贡献，包括提交代码、报告问题或提出改进建议。请在 GitHub 上创建问题或拉取请求。

### **许可证**:
此项目使用 **MIT License**。具体详情见 `LICENSE` 文件。

---

PS:此工具为3A制作(AI生成代码、AI Debug、AI生成自述文档)，如有问题还请复制代码询问ChatGPT
本人一点代码都没看(不报错实现功能就是胜利)所以可能提供不了什么技术支持

特别感谢OpenAI的技术支持

---

v2024.12.10 18:56 更新记录：打包了一个exe即点即用程序(正在研究打包到安卓的可行性)
