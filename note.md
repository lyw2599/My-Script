

```javascript
javascript:(function(){'use strict';function checkAndClick(){var continueButton=document.querySelector('.yx--alarm-clock');if(continueButton){continueButton.click();console.log('已自动点击继续计时按钮');}}setInterval(checkAndClick,60000);})();
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
