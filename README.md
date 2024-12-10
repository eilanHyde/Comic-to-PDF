
---

# Comic-to-PDF 
`Comic-to-PDF` 是一个将漫画图片批量转换为 PDF 文件并打包为 ZIP 文件的工具。该工具通过图形用户界面（GUI）简化了漫画图片的转换和压缩过程，支持从指定文件夹中读取漫画图像，生成单独的 PDF 文件，并将每个漫画文件夹压缩成 ZIP 文件。

## 目录
- [简介](#简介)
- [功能](#功能)
- [安装](#安装)
- [运行](#运行)
- [使用方法](#使用方法)
- [常见问题](#常见问题)

## 简介

`Comic-to-PDF` 程序支持将漫画图片（PNG、JPG、JPEG、WEBP 格式）按自然顺序合并为 PDF 文件，并将整个漫画文件夹打包成 ZIP 文件，方便存档或分享。程序使用 Python 编写，界面友好，适合不熟悉命令行操作的用户。

## 功能

- **选择输入文件夹**：从指定的文件夹中读取漫画文件。
- **生成 PDF 文件**：将每个漫画章节的图片按顺序合并为 PDF 文件。
- **生成 ZIP 文件**：将每个漫画文件夹打包成一个 ZIP 文件。
- **实时日志输出**：显示处理进度、成功/失败信息和错误提示。
- **自动滚动日志**：可以选择启用自动滚动日志，方便查看实时信息。

## 安装

1. **安装依赖**：

   请确保安装了以下 Python 库：

   ```bash
   pip install pillow natsort
   ```

   - `Pillow`：用于图像处理，支持打开、转换、保存图片。
   - `natsort`：用于对文件名按自然顺序进行排序。

2. **获取程序文件**：
   - 下载或克隆程序代码。
   - 运行 `comic-to-pdf.py` 文件即可启动 GUI。

## 运行

1. 克隆或下载项目代码到本地。
2. 运行 `comic-to-pdf.py` 文件：
   - 在命令行中输入：
     ```bash
     python comic-to-pdf.py
     ```
   - 启动后会打开一个图形用户界面窗口。

## 使用方法

1. **启动程序**：运行 `comic-to-pdf.py` 后，程序会打开一个窗口。

2. **选择输入文件夹**：
   - 点击输入框旁边的 **“浏览”** 按钮，选择包含漫画图片的文件夹。
   - 默认情况下，程序会在当前目录下创建一个 `comics` 文件夹作为默认输入文件夹。

3. **选择输出文件夹**：
   - 点击输出框旁边的 **“浏览”** 按钮，选择一个存储生成的 PDF 和 ZIP 文件的文件夹。
   - 默认情况下，程序会在当前目录下创建一个 `output` 文件夹作为默认输出文件夹。

4. **启动处理**：
   - 点击 **“开始处理”** 按钮，程序将开始处理输入文件夹中的漫画文件夹。
   - 处理过程中，程序会显示实时日志，记录每个漫画文件夹的处理进度。

5. **查看结果**：
   - 处理完成后，程序将在输出文件夹中创建每个漫画文件夹的子文件夹，并将 PDF 文件和 ZIP 文件保存在其中。
   - PDF 文件会按章节生成，每个章节一个 PDF。
   - ZIP 文件会将整个漫画文件夹压缩成一个 ZIP 文件。

6. **日志设置**：
   - 您可以通过勾选 **“自动滚动”** 选项来启用自动滚动日志窗口，确保实时查看日志信息。

## 常见问题

1. **Q: 程序没有生成 PDF 或 ZIP 文件。**
   - A: 请检查输入文件夹是否包含有效的图片文件。如果文件夹中没有图片，程序将跳过该文件夹。确保输出文件夹路径有效。

2. **Q: 日志中显示错误信息，如何解决？**
   - A: 查看日志中的详细错误信息。常见的错误可能是图片格式不支持或文件损坏。确保所有图片文件是有效的图像格式（PNG、JPG、JPEG、WEBP）。

3. **Q: 如何确保程序能够处理所有图片？**
   - A: 确保输入文件夹中的每个章节文件夹内包含有效且支持的图片格式（PNG、JPG、JPEG、WEBP）。程序会自动跳过不支持的文件类型。

4. **Q: 可以处理非漫画文件夹吗？**
   - A: 该程序设计用于处理包含漫画图像文件的文件夹。如果文件夹结构符合漫画的规范（每个漫画是一个子文件夹，每个章节是一个子子文件夹），程序会自动识别并处理。

## 许可证

该程序是一个开源项目，您可以自由使用、修改和分发。在使用过程中，请遵循相关的开源协议。

---

通过该指南，用户可以快速理解并使用 `Comic-to-PDF` 工具，轻松将漫画图片批量转换为 PDF 和压缩文件。
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
## 更新
v2024.12.10 18:56 更新记录：打包了一个exe即点即用程序
v2024.12.10 22:02 更新记录：更新了gui跟随窗口大小调整，Android实机测试比例正常不会像上个版本一样显示不全。现在转换pdf时不会压缩图片
