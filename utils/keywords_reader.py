# --*-- coding: utf-8 --*--
"""
将keywords_list.py中的关键词导入数据库
"""
import sys
import os

from docs.keyword_list import DISTRICT_LIST  # 关键字列表之区域列表
from db_access import create_keyword  # 数据库创建关键字

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

for k in DISTRICT_LIST:
    for i in [k["中文名称"], k["英文名称"]]:
        res = create_keyword(i)
        if res["success"]:
            print("[导入] {}".format(i))
        else:
            if res["msg"] == "已存在":
                print("[存在] {}".format(i))
            else:
                print("[出错] {}".format(i))
