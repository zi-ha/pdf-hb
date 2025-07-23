#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF简易合并工具
简化版本，更容易使用
"""

import os
import re
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter


def get_pdf_files(folder_path):
    """获取并排序PDF文件"""
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    # 按文件名中的数字排序
    pdf_files.sort(key=lambda x: int(re.findall(r'\d+', x.name)[0]) if re.findall(r'\d+', x.name) else 0)
    return pdf_files


def merge_pdfs(files, output_name):
    """合并PDF文件"""
    writer = PdfWriter()
    
    print(f"正在合并 {len(files)} 个文件...")
    for file_path in files:
        print(f"  添加: {file_path.name}")
        reader = PdfReader(str(file_path))
        for page in reader.pages:
            writer.add_page(page)
    
    with open(output_name, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✓ 合并完成: {output_name}")


def main():
    print("=== PDF简易合并工具 ===\n")
    
    # 获取当前目录的PDF文件
    current_dir = os.getcwd()
    pdf_files = get_pdf_files(current_dir)
    
    if not pdf_files:
        print("当前目录中没有找到PDF文件!")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for i, file in enumerate(pdf_files, 1):
        print(f"{i:3d}. {file.name}")
    
    print("\n请选择合并模式:")
    print("1. 按数量分组合并")
    print("2. 全部合并为一个文件")
    print("3. 指定范围合并")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 按数量分组
        try:
            count = int(input("每组多少个文件? "))
            naming = input("命名方式 (1=数字范围 2=卷号): ").strip()
            
            total_groups = (len(pdf_files) + count - 1) // count
            
            for i in range(total_groups):
                start_idx = i * count
                end_idx = min(start_idx + count, len(pdf_files))
                group_files = pdf_files[start_idx:end_idx]
                
                if naming == "2":
                    output_name = f"第{i+1}卷.pdf"
                else:
                    start_num = int(re.findall(r'\d+', group_files[0].name)[0])
                    end_num = int(re.findall(r'\d+', group_files[-1].name)[0])
                    output_name = f"{start_num:03d}-{end_num:03d}.pdf"
                
                merge_pdfs(group_files, output_name)
                
        except ValueError:
            print("请输入有效数字")
    
    elif choice == "2":
        # 全部合并
        naming = input("文件名 (直接回车使用'全集.pdf'): ").strip()
        output_name = naming if naming else "全集.pdf"
        merge_pdfs(pdf_files, output_name)
    
    elif choice == "3":
        # 指定范围
        try:
            start = int(input(f"起始编号 (1-{len(pdf_files)}): ")) - 1
            count = int(input("合并数量: "))
            
            if start < 0 or start >= len(pdf_files):
                print("编号超出范围")
                return
            
            end_idx = min(start + count, len(pdf_files))
            selected_files = pdf_files[start:end_idx]
            
            naming = input("命名方式 (1=数字范围 2=自定义): ").strip()
            
            if naming == "2":
                output_name = input("文件名: ").strip()
                if not output_name.endswith('.pdf'):
                    output_name += '.pdf'
            else:
                start_num = int(re.findall(r'\d+', selected_files[0].name)[0])
                end_num = int(re.findall(r'\d+', selected_files[-1].name)[0])
                output_name = f"{start_num:03d}-{end_num:03d}.pdf"
            
            merge_pdfs(selected_files, output_name)
            
        except ValueError:
            print("请输入有效数字")
    
    else:
        print("无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")
    
    input("\n按回车键退出...")