import os
import re

# 获取工作目录
work_dir = os.path.dirname(os.path.abspath(__file__))

# 获取所有文件并按名称排序
files = sorted(os.listdir(work_dir), reverse=True)

# 定义匹配卷几的正则表达式
pattern = re.compile(r'卷(\d+)\.pdf')

for file in files:
    match = pattern.match(file)
    if match:
        num = int(match.group(1))
        new_num = num + 2
        new_file = f'卷{new_num}.pdf'
        old_path = os.path.join(work_dir, file)
        new_path = os.path.join(work_dir, new_file)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            print(f'重命名 {file} 到 {new_file} 时出错: {e}')