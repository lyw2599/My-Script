

```javascript
javascript:(function(){'use strict';function checkAndClick(){var continueButton=document.querySelector('.yx--alarm-clock');if(continueButton){continueButton.click();console.log('已自动点击继续计时按钮');}}setInterval(checkAndClick,60000);})();
```

# 2.0
```Python
import os
import pandas as pd
import re
from typing import Union, List

def parse_flex_range(range_str: str, max_val: int, is_col: bool = False) -> slice:

    if not range_str or range_str == ":":
        return slice(None)
    
    parts = range_str.split(':')
    if len(parts) != 2:
        return slice(None)
    
    start, end = parts
    
    # 列范围解析
    if is_col:
        start_idx = ord(start.upper()) - ord('A') if start else 0
        end_idx = (ord(end.upper()) - ord('A') + 1) if end else max_val
        return slice(start_idx, end_idx)
    
    # 行范围解析
    start_idx = int(start) - 1 if start else 0
    end_idx = int(end) if end else max_val
    return slice(start_idx, end_idx)

def read_file(file_path, file_type, sheet_name=None):

    if file_type == 'csv':
        # 自动检测编码
        encodings = ['utf-8', 'gbk', 'latin1', 'utf-16']
        for enc in encodings:
            try:
                return pd.read_csv(file_path, header=None, encoding=enc)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return pd.read_csv(file_path, header=None, errors='replace')
    
    elif file_type in ('xlsx', 'xls'):
        if sheet_name:
            return pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        else:
            with pd.ExcelFile(file_path) as xls:
                return pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
    return None

def merge_files(
    source_folder: str,
    output_file: str,
    merge_mode: str = 'row',
    sheet_name: Union[str, None] = None,
    cols: str = None,
    rows: str = None,
    output_format: str = 'excel',
    position: str = 'end'  # 'front'或'end'
):
    """
    
    参数:
        position: 来源信息位置 ('front'第一列, 'end'最后一列)
    """
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"文件夹不存在: {source_folder}")

    all_data = []
    max_cols = 0  # 记录最大列数
    
    for file in os.listdir(source_folder):
        try:
            file_path = os.path.join(source_folder, file)
            _, ext = os.path.splitext(file)
            file_type = ext[1:].lower() if ext else ''
            
            if file_type not in ('csv', 'xlsx', 'xls'):
                continue
                
            # 处理Excel多sheet
            if file_type in ('xlsx', 'xls') and not sheet_name:
                with pd.ExcelFile(file_path) as xls:
                    sheets = xls.sheet_names
            else:
                sheets = [sheet_name]
                
            for sheet in sheets:
                df = read_file(file_path, file_type, sheet)
                if df is None or df.empty:
                    continue
                
                # 应用行列范围筛选
                if rows:
                    row_slice = parse_flex_range(rows, len(df))
                    df = df.iloc[row_slice, :]
                
                if cols:
                    col_slice = parse_flex_range(cols, len(df.columns), is_col=True)
                    df = df.iloc[:, col_slice]
                
                # 记录最大列数
                current_cols = len(df.columns)
                if current_cols > max_cols:
                    max_cols = current_cols
                
                # 添加来源信息（位置可选）
                if position == 'front':
                    df.insert(0, 'source_file', file)
                    df.insert(1, 'sheet_name', sheet)
                else:  # 默认添加到末尾
                    df['source_file'] = file
                    df['sheet_name'] = sheet
                
                all_data.append(df)
                
        except Exception as e:
            print(f"处理文件 {file} 时出错: {str(e)}")

    if not all_data:
        print("未找到有效数据")
        return

    # 统一列数防止错位
    for df in all_data:
        if len(df.columns) < max_cols:
            padding_cols = max_cols - len(df.columns)
            padding_df = pd.DataFrame(
                [[None]*padding_cols for _ in range(len(df))],
                columns=[f'col_{i}' for i in range(len(df.columns), len(df.columns)+padding_cols)]
            )
            df = pd.concat([df, padding_df], axis=1)

    # 合并数据
    if merge_mode == 'column':
        max_rows = max(len(df) for df in all_data)
        for df in all_data:
            if len(df) < max_rows:
                padding = pd.DataFrame(
                    [[None]*len(df.columns)]*(max_rows - len(df)),
                    columns=df.columns
                )
                df = pd.concat([df, padding], axis=0)
        merged_df = pd.concat(all_data, axis=1)
    else:
        merged_df = pd.concat(all_data, axis=0, ignore_index=True)

    # 保存结果
    if output_file.lower().endswith('.csv'):
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    else:
        merged_df.to_excel(output_file, index=False)
    print(f"合并完成 → {output_file}")

# 使用示例
if __name__ == "__main__":
    merge_files(
        source_folder="C:/Users/12/Desktop/tetst/",
        output_file="merged_data.xlsx",
        merge_mode="column",
        sheet_name=None,  # 合并所有sheet
        cols="C:E",       # C列到最后一列
        rows="3:6",       # 第3行到最后一行
        position='front' # 来源信息放第一列
    )


    """
    支持行列范围选择的Excel合并函数
    
    参数:
        source_folder: 源文件夹路径
        output_file: 输出文件路径
        merge_mode: 合并模式('row'按行/'column'按列)
        sheet_name: None时合并所有sheet, 字符串时指定sheet
        cols: 列范围(如"A:", ":D", "B:D")
        rows: 行范围(如"5:", ":10", "5:10")
    """
```




```python

import os
import pandas as pd
import re

def parse_range(range_str, max_val):
    """解析范围字符串，如A:D或5:10"""
    if not range_str:
        return None
    
    # 处理列范围 (A:D格式)
    if re.match(r'^[A-Za-z]?:[A-Za-z]?$', range_str):
        start, end = range_str.split(':')
        start = ord(start.upper()) - ord('A') if start else 0
        end = ord(end.upper()) - ord('A') if end else max_val
        return slice(start, end + 1)
    
    # 处理行范围 (5:10格式)
    elif re.match(r'^\d*:\d*$', range_str):
        start, end = range_str.split(':')
        start = int(start) - 1 if start else 0
        end = int(end) if end else max_val
        return slice(start, end)
    
    return None

def merge_excel_files(source_folder, output_file, 
                     merge_mode='row', sheet_name=None,
                     cols=None, rows=None):
    """
    支持行列范围选择的Excel合并函数
    
    参数:
        source_folder: 源文件夹路径
        output_file: 输出文件路径
        merge_mode: 合并模式('row'/'column')
        sheet_name: 指定sheet名称
        cols: 列范围(如"A:D")
        rows: 行范围(如"5:10")
    """
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"源文件夹不存在: {source_folder}")

    all_data = []
    
    for file in os.listdir(source_folder):
        if file.endswith(('.xlsx', '.xls')):
            try:
                file_path = os.path.join(source_folder, file)
                
                # 读取整个文件
                if sheet_name:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                else:
                    with pd.ExcelFile(file_path) as xls:
                        df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
                
                # 应用行列范围筛选
                if rows:
                    row_slice = parse_range(rows, len(df))
                    df = df.iloc[row_slice, :]
                
                if cols:
                    col_slice = parse_range(cols, len(df.columns))
                    df = df.iloc[:, col_slice]
                
                df['source_file'] = file
                df['sheet_name'] = sheet_name or xls.sheet_names[0]
                all_data.append(df)
                
            except Exception as e:
                print(f"处理文件 {file} 时出错: {str(e)}")

    if not all_data:
        print("未找到任何有效数据")
        return

    if merge_mode == 'column':
        # 按列合并
        max_rows = max(len(df) for df in all_data)
        for df in all_data:
            if len(df) < max_rows:
                df = pd.concat([df, pd.DataFrame(index=range(max_rows - len(df)))], axis=0)
        merged_df = pd.concat(all_data, axis=1)
    else:
        # 按行合并
        merged_df = pd.concat(all_data, axis=0, ignore_index=True)

    merged_df.to_excel(output_file, index=False)
    print(f"合并完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    merge_excel_files(
        source_folder="C:/Users/12/Desktop/tetst/",
        output_file="merged.xlsx",
        merge_mode='column', #column
        sheet_name="Sheet2",
        cols="D:H",
        rows="5:20"
    )

```
