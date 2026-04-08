#!/usr/bin/env python3
"""
更新提示词仓库索引

功能：
1. 扫描所有分类目录下的.md文件
2. 提取元信息
3. 更新README.md中的索引表
"""

import os
import re
from datetime import datetime
from pathlib import Path

def extract_metadata(file_path):
    """从文件中提取元信息"""
    metadata = {
        'name': '',
        'source': '',
        'category': '',
        'rating': '',
        'score': '',
        'file': file_path.name
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 提取标题
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                metadata['name'] = title_match.group(1)
            
            # 提取表格中的元信息
            source_match = re.search(r'\|\s*来源\s*\|\s*([^|]+)\s*\|', content)
            if source_match:
                metadata['source'] = source_match.group(1).strip()
            
            category_match = re.search(r'\|\s*分类\s*\|\s*([^|]+)\s*\|', content)
            if category_match:
                metadata['category'] = category_match.group(1).strip()
            
            rating_match = re.search(r'\|\s*质量评级\s*\|\s*([^|]+)\s*\|', content)
            if rating_match:
                metadata['rating'] = rating_match.group(1).strip()
            
            score_match = re.search(r'\|\s*总分\s*\|\s*([\d.]+)', content)
            if score_match:
                metadata['score'] = score_match.group(1)
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return metadata

def scan_prompts(base_path):
    """扫描所有提示词文件"""
    prompts = []
    categories = ['coding', 'writing', 'agent', 'video', 'creative', 'workflow']
    
    for category in categories:
        category_path = base_path / category
        if category_path.exists():
            for file_path in category_path.glob('*.md'):
                if file_path.name != '.gitkeep':
                    metadata = extract_metadata(file_path)
                    metadata['category'] = category
                    prompts.append(metadata)
    
    return prompts

def generate_index_table(prompts):
    """生成索引表格"""
    lines = ["| 名称 | 分类 | 来源 | 评级 | 文件 |", "|------|------|------|------|------|"]
    
    for p in sorted(prompts, key=lambda x: x.get('rating', 'Z')):
        rating = p.get('rating', '-')
        name = p.get('name', p.get('file', 'Unknown'))
        category = p.get('category', '-')
        source = p.get('source', '-')
        file_link = f"[{p.get('file', '')}]({p.get('category', '')}/{p.get('file', '')})"
        
        lines.append(f"| {name} | {category} | {source} | {rating} | {file_link} |")
    
    return '\n'.join(lines)

def update_readme(base_path, index_table):
    """更新README.md"""
    readme_path = base_path / 'README.md'
    
    if not readme_path.exists():
        print("README.md not found")
        return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找索引部分
    index_pattern = r'## 索引\s*\n\n.*?(?=\n---|\n##|\Z)'
    
    new_index = f"## 索引\n\n{index_table}\n"
    
    if re.search(index_pattern, content, re.DOTALL):
        content = re.sub(index_pattern, new_index, content, flags=re.DOTALL)
    else:
        # 追加到文件末尾
        content = content.rstrip() + '\n\n' + new_index
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated README.md with {len(index_table.split(chr(10))) - 2} prompts")

def main():
    """主函数"""
    base_path = Path(__file__).parent.parent.parent / 'prompt-library'
    
    if not base_path.exists():
        print(f"Prompt library not found at {base_path}")
        return
    
    print(f"Scanning prompts in {base_path}...")
    prompts = scan_prompts(base_path)
    print(f"Found {len(prompts)} prompts")
    
    index_table = generate_index_table(prompts)
    update_readme(base_path, index_table)
    
    print("Done!")

if __name__ == '__main__':
    main()
