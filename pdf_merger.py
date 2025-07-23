#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF智能合并脚本
支持多种合并模式和命名规则
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import argparse

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("请先安装PyPDF2库: pip install PyPDF2")
    sys.exit(1)


class PDFMerger:
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.pdf_files = self._get_pdf_files()
        
    def _get_pdf_files(self) -> List[Path]:
        """获取文件夹中所有PDF文件并按名称排序"""
        pdf_files = list(self.folder_path.glob("*.pdf"))
        # 按文件名中的数字排序
        pdf_files.sort(key=lambda x: self._extract_number(x.name))
        return pdf_files
    
    def _extract_number(self, filename: str) -> int:
        """从文件名中提取数字用于排序"""
        numbers = re.findall(r'\d+', filename)
        return int(numbers[0]) if numbers else 0
    
    def show_files(self):
        """显示所有PDF文件"""
        print(f"\n在文件夹 '{self.folder_path}' 中找到 {len(self.pdf_files)} 个PDF文件:")
        for i, file in enumerate(self.pdf_files, 1):
            print(f"{i:3d}. {file.name}")
    
    def merge_pdfs(self, start_index: int, count: int, output_name: str) -> bool:
        """合并指定范围的PDF文件"""
        try:
            if start_index < 0 or start_index >= len(self.pdf_files):
                print(f"错误: 起始索引 {start_index + 1} 超出范围")
                return False
            
            end_index = min(start_index + count, len(self.pdf_files))
            files_to_merge = self.pdf_files[start_index:end_index]
            
            if not files_to_merge:
                print("错误: 没有文件需要合并")
                return False
            
            print(f"\n正在合并以下文件:")
            for file in files_to_merge:
                print(f"  - {file.name}")
            
            writer = PdfWriter()
            
            for file_path in files_to_merge:
                try:
                    reader = PdfReader(str(file_path))
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    print(f"警告: 处理文件 {file_path.name} 时出错: {e}")
                    continue
            
            output_path = self.folder_path / output_name
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"✓ 成功合并为: {output_name}")
            print(f"  合并了 {len(files_to_merge)} 个文件")
            return True
            
        except Exception as e:
            print(f"合并过程中出错: {e}")
            return False
    
    def generate_filename(self, start_index: int, count: int, naming_mode: str, volume_number: int = None) -> str:
        """根据命名模式生成文件名"""
        end_index = min(start_index + count, len(self.pdf_files)) - 1
        
        if naming_mode == "range":
            # 模式1: 几-几 (如: 001-010.pdf)
            start_num = self._extract_number(self.pdf_files[start_index].name)
            end_num = self._extract_number(self.pdf_files[end_index].name)
            return f"{start_num:03d}-{end_num:03d}.pdf"
        
        elif naming_mode == "volume":
            # 模式2: 第x卷 (如: 第1卷.pdf)
            vol_num = volume_number if volume_number else 1
            return f"卷{vol_num}.pdf"
        
        elif naming_mode == "custom":
            # 模式3: 自定义前缀 + 范围
            start_num = self._extract_number(self.pdf_files[start_index].name)
            end_num = self._extract_number(self.pdf_files[end_index].name)
            return f"合并版_{start_num:03d}-{end_num:03d}.pdf"
        
        else:
            # 默认模式
            return f"merged_{start_index + 1}-{end_index + 1}.pdf"


def interactive_mode():
    """交互式模式"""
    print("=== PDF智能合并工具 ===")
    
    # 获取当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 初始化合并器
    merger = PDFMerger(current_dir)
    
    if not merger.pdf_files:
        print("当前目录中没有找到PDF文件!")
        return
    
    # 显示文件列表
    merger.show_files()
    
    while True:
        print("\n" + "="*50)
        print("请选择操作:")
        print("1. 批量合并 (按数量分组)")
        print("2. 指定范围合并")
        print("3. 全部合并")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            batch_merge_mode(merger)
        elif choice == "2":
            range_merge_mode(merger)
        elif choice == "3":
            merge_all_mode(merger)
        elif choice == "4":
            print("再见!")
            break
        else:
            print("无效选择，请重新输入")


def batch_merge_mode(merger: PDFMerger):
    """批量合并模式"""
    try:
        files_per_group = int(input("每组合并多少个文件? "))
        if files_per_group <= 0:
            print("文件数量必须大于0")
            return
        
        # 选择命名模式
        naming_mode = choose_naming_mode()
        
        total_files = len(merger.pdf_files)
        groups = (total_files + files_per_group - 1) // files_per_group
        
        print(f"\n将创建 {groups} 个合并文件:")
        
        for i in range(groups):
            start_idx = i * files_per_group
            actual_count = min(files_per_group, total_files - start_idx)
            
            if naming_mode == "volume":
                filename = merger.generate_filename(start_idx, actual_count, naming_mode, i + 1)
            else:
                filename = merger.generate_filename(start_idx, actual_count, naming_mode)
            
            print(f"  第{i+1}组: {filename} (包含 {actual_count} 个文件)")
        
        confirm = input("\n确认执行? (y/n): ").strip().lower()
        if confirm == 'y':
            success_count = 0
            for i in range(groups):
                start_idx = i * files_per_group
                actual_count = min(files_per_group, total_files - start_idx)
                
                if naming_mode == "volume":
                    filename = merger.generate_filename(start_idx, actual_count, naming_mode, i + 1)
                else:
                    filename = merger.generate_filename(start_idx, actual_count, naming_mode)
                
                if merger.merge_pdfs(start_idx, actual_count, filename):
                    success_count += 1
            
            print(f"\n批量合并完成! 成功创建 {success_count}/{groups} 个文件")
    
    except ValueError:
        print("请输入有效的数字")


def range_merge_mode(merger: PDFMerger):
    """指定范围合并模式"""
    try:
        start = int(input(f"起始文件编号 (1-{len(merger.pdf_files)}): ")) - 1
        count = int(input("要合并的文件数量: "))
        
        if start < 0 or start >= len(merger.pdf_files):
            print("起始编号超出范围")
            return
        
        if count <= 0:
            print("文件数量必须大于0")
            return
        
        # 选择命名模式
        naming_mode = choose_naming_mode()
        
        if naming_mode == "volume":
            vol_num = int(input("卷号: "))
            filename = merger.generate_filename(start, count, naming_mode, vol_num)
        else:
            filename = merger.generate_filename(start, count, naming_mode)
        
        print(f"\n将创建文件: {filename}")
        
        confirm = input("确认执行? (y/n): ").strip().lower()
        if confirm == 'y':
            merger.merge_pdfs(start, count, filename)
    
    except ValueError:
        print("请输入有效的数字")


def merge_all_mode(merger: PDFMerger):
    """全部合并模式"""
    naming_mode = choose_naming_mode()
    
    if naming_mode == "volume":
        vol_num = int(input("卷号: "))
        filename = merger.generate_filename(0, len(merger.pdf_files), naming_mode, vol_num)
    else:
        filename = merger.generate_filename(0, len(merger.pdf_files), naming_mode)
    
    print(f"\n将合并所有 {len(merger.pdf_files)} 个文件为: {filename}")
    
    confirm = input("确认执行? (y/n): ").strip().lower()
    if confirm == 'y':
        merger.merge_pdfs(0, len(merger.pdf_files), filename)


def choose_naming_mode() -> str:
    """选择命名模式"""
    print("\n选择文件命名模式:")
    print("1. 范围模式 (如: 001-010.pdf)")
    print("2. 卷号模式 (如: 第1卷.pdf)")
    print("3. 自定义模式 (如: 合并版_001-010.pdf)")
    
    while True:
        mode_choice = input("请选择命名模式 (1-3): ").strip()
        if mode_choice == "1":
            return "range"
        elif mode_choice == "2":
            return "volume"
        elif mode_choice == "3":
            return "custom"
        else:
            print("无效选择，请重新输入")


def command_line_mode():
    """命令行模式"""
    parser = argparse.ArgumentParser(description='PDF智能合并工具')
    parser.add_argument('--folder', '-f', default='.', help='PDF文件所在文件夹路径')
    parser.add_argument('--count', '-c', type=int, help='每组合并的文件数量')
    parser.add_argument('--start', '-s', type=int, default=1, help='起始文件编号')
    parser.add_argument('--naming', '-n', choices=['range', 'volume', 'custom'], 
                       default='range', help='命名模式')
    parser.add_argument('--volume', '-v', type=int, help='卷号 (仅在volume模式下使用)')
    parser.add_argument('--output', '-o', help='输出文件名')
    
    args = parser.parse_args()
    
    merger = PDFMerger(args.folder)
    
    if not merger.pdf_files:
        print(f"在文件夹 '{args.folder}' 中没有找到PDF文件!")
        return
    
    merger.show_files()
    
    if args.count:
        # 批量模式
        total_files = len(merger.pdf_files)
        groups = (total_files + args.count - 1) // args.count
        
        for i in range(groups):
            start_idx = i * args.count
            actual_count = min(args.count, total_files - start_idx)
            
            if args.naming == "volume":
                vol_num = (args.volume or 1) + i
                filename = merger.generate_filename(start_idx, actual_count, args.naming, vol_num)
            else:
                filename = merger.generate_filename(start_idx, actual_count, args.naming)
            
            merger.merge_pdfs(start_idx, actual_count, filename)
    
    elif args.output:
        # 单个文件模式
        start_idx = args.start - 1
        count = len(merger.pdf_files) - start_idx
        merger.merge_pdfs(start_idx, count, args.output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command_line_mode()
    else:
        interactive_mode()