# coding=utf-8
"""
返回两字段的区别
"""
import difflib  # 标准库：比较序列


def diff_file(lines1, lines2):
    if (not lines1) or (not lines2):
        return
    diff_text = ''
    diff = list(difflib.ndiff(lines1.splitlines(), lines2.splitlines()))
    for i in diff:
        if i.startswith('+'):
            diff_text += i[1:]
    return diff_text





