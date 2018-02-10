# --*-- coding: utf-8 --*--
"""
自动发送邮件机器人文件
"""
import os
import sys

import time
from utils.send_email import send_mail
from config import SEND_MAIL_INTERVAL  # 导入发邮件频率0.5小时
from db_access import get_users  # 导入数据库操作的获取用户方法
from utils.blacklist import blacklist_email  # 黑名单列表_邮件

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)


def mail_bot():
    """
    邮件机器人
    """
    while True:
        user_list = get_users()  # 获取用户列表，数据库User表
        addr_list = []  # 初始化邮箱地址列表
        # 逐个添加邮箱
        for u in user_list:
            if u.email not in blacklist_email:
                addr_list.append(u.email)
        # 逐个发送邮件
        for to in addr_list:
            try:
                send_mail(to)
            except Exception as e:
                print(str(e))

        # 机器人休眠时间：集中发送邮件间隔时间（小时*参数）
        time.sleep(60 * 60 * SEND_MAIL_INTERVAL)


if __name__ == '__main__':
    mail_bot()
