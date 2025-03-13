import re
import sys
from io import StringIO

def extract_after_integrality(text):
    """提取'integrality :'行之后的所有内容"""
    lines = text.split('\n')
    # 匹配以任意空格开头，后接integrality和冒号的行
    pattern = re.compile(r'^\s*integrality\s*:')
    
    # 遍历所有行查找匹配项
    for idx, line in enumerate(lines):
        if pattern.search(line):
            # 返回从匹配行开始到结尾的所有行
            return '\n'.join(lines[idx+1:])
    
    # 如果未找到则返回空字符串
    return ''


def extract_and_execute_code(filename):
    # 读取文件内容
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式提取Python代码块
    code_block = re.search(r'```python(.*?)```', content, re.DOTALL)
    if not code_block:
        raise ValueError("文件中未找到Python代码块")
    
    python_code = code_block.group(1).strip()

    # 准备捕获标准输出
    original_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # 在隔离的命名空间中执行代码
        exec(python_code, {})
    except Exception as e:
        # 恢复标准输出后抛出异常
        sys.stdout = original_stdout
        raise RuntimeError(f"代码执行出错: {str(e)}")
    finally:
        # 始终恢复标准输出
        sys.stdout = original_stdout

    # 获取捕获的输出内容
    exe_result = captured_output.getvalue()
    exe_result = extract_after_integrality(exe_result)

    return exe_result


# 使用示例
# if __name__ == "__main__":
#     try:
#         # output_str = extract_and_execute_code('2025-03-12_00-17-41.txt')
#         output_str = extract_and_execute_code('2025-03-12_13-14-10.txt')
#         print("捕获的输出内容：")
#         print(output_str)
#     except Exception as e:
#         print(str(e))
