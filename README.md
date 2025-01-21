# 漫画转换器 (Comic Converter)

[English Version](#comic-converter) | [日本語バージョン](#漫画コンバーター-comic-converter)

一个简单但实用的漫画转换工具，支持将漫画图片批量转换为 PDF 或长图格式。

## 功能特点

- 支持将漫画章节转换为 PDF 文件
- 支持生成长图格式（将多张图片垂直拼接）
- 自动压缩处理后的文件为 ZIP 格式
- 多语言支持 (简体中文、繁体中文、英语、日语等)
- 深色/浅色主题切换
- 友好的图形界面
- 自动保存配置

## 系统要求

- Python 3.x
- 依赖库：
  - `customtkinter`
  - `Pillow`
  - `img2pdf`
  - `rich`

## 安装

```bash
pip install customtkinter Pillow img2pdf rich
```

## 使用说明

1. 选择包含漫画章节的输入目录
2. 选择输出目录
3. 选择生成格式（PDF或长图）
4. 点击"开始处理"按钮

### 目录结构要求

```
输入目录/
  └── 漫画名称/
      └── 章节目录/
          └── 图片文件
```

## 配置说明

- 程序会自动记住上次使用的输入输出路径
- 可以通过设置菜单切换界面语言
- 支持深色/浅色主题切换
- 所有设置会自动保存到 config.json

## 支持的图片格式

- JPG/JPEG
- PNG
- WebP

## 作者

作者：eilanHyde
创建协助：GitHub Copilot

## 许可

请遵守相关版权法律法规，仅用于个人合法用途。

## 注意事项

- 处理大量图片时可能需要较长时间
- 建议定期备份重要文件
- 程序会自动处理子文件夹中的所有图片文件

---

# Comic Converter

[中文版本](#漫画转换器-comic-converter) | [日本語バージョン](#漫画コンバーター-comic-converter)

A simple yet practical tool for converting manga images into PDF or vertical-scroll images.

## Features

- Convert manga chapters into PDF files
- Generate vertical-scroll images (stitch multiple images vertically)
- Automatically compress processed files into ZIP format
- Multi-language support (Simplified Chinese, Traditional Chinese, English, Japanese, etc.)
- Light/Dark theme toggle
- User-friendly GUI
- Auto-save configurations

## System Requirements

- Python 3.x
- Dependencies:
  - `customtkinter`
  - `Pillow`
  - `img2pdf`
  - `rich`

## Installation

```bash
pip install customtkinter Pillow img2pdf rich
```

## Usage Instructions

1. Select the input directory containing manga chapters
2. Select the output directory
3. Choose the output format (PDF or vertical-scroll image)
4. Click the "Start Processing" button

### Directory Structure

```
Input Directory/
  └── Manga Title/
      └── Chapter Directory/
          └── Image Files
```

## Configuration

- The program remembers the last used input and output paths
- You can switch interface language via the settings menu
- Supports light and dark theme toggling
- All settings are saved automatically to `config.json`

## Supported Image Formats

- JPG/JPEG
- PNG
- WebP

## Author

Author: eilanHyde
Assisted by: GitHub Copilot

## License

Please comply with relevant copyright laws and use only for personal and lawful purposes.

## Notes

- Processing large numbers of images may take a long time
- Regularly back up important files
- The program automatically processes all image files in subfolders

---

# 漫画コンバーター (Comic Converter)

[中文版本](#漫画转换器-comic-converter) | [English Version](#comic-converter)

簡単で実用的な漫画変換ツールで、漫画画像を一括でPDFや縦長画像形式に変換できます。

## 機能

- 漫画の章をPDFファイルに変換
- 縦長画像形式を生成（複数の画像を縦に結合）
- 処理後のファイルを自動的にZIP形式で圧縮
- 多言語対応（簡体字中国語、繁体字中国語、英語、日本語など）
- ダーク/ライトテーマの切り替え
- ユーザーフレンドリーなGUI
- 設定の自動保存

## システム要件

- Python 3.x
- 必要なライブラリ：
  - `customtkinter`
  - `Pillow`
  - `img2pdf`
  - `rich`

## インストール

```bash
pip install customtkinter Pillow img2pdf rich
```

## 使用方法

1. 漫画の章が含まれる入力ディレクトリを選択
2. 出力ディレクトリを選択
3. 生成フォーマットを選択（PDFまたは縦長画像）
4. 「処理開始」ボタンをクリック

### ディレクトリ構成

```
入力ディレクトリ/
  └── 漫画タイトル/
      └── 章ディレクトリ/
          └── 画像ファイル
```

## 設定について

- プログラムは前回使用した入力パスと出力パスを記憶します
- 設定メニューからインターフェース言語を切り替えることができます
- ライト/ダークテーマの切り替えに対応
- すべての設定は自動的に`config.json`に保存されます

## サポートされている画像形式

- JPG/JPEG
- PNG
- WebP

## 作者

作者：eilanHyde
作成補助：GitHub Copilot

## ライセンス

関連する著作権法を遵守し、個人の合法的な目的でのみ使用してください。

## 注意事項

- 大量の画像を処理する場合、時間がかかることがあります
- 定期的に重要なファイルをバックアップしてください
- プログラムはサブフォルダ内のすべての画像ファイルを自動的に処理します
