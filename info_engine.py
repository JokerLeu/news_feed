# --*-- coding: utf-8 --*--
"""
信息获取引擎
"""
import os
import sys

from utils.log import NOTICE, log, ERROR, RECORD  # 引入日志

import time
import random
from config import CELERY_BROKER, CELERY_BACKEND, CRAWL_INTERVAL # 导入配置
from db_access import *  # 导入所有数据库操作方法
from utils.blacklist import blacklist_site, blacklist_company  # 网址名单，公司名单
from utils.content_process import complement_url, check_content   # 内容处理：完成usl，检测内容
from utils.diff import diff_file  # 文件的区别
from utils.html_downloader import crawl  # 下载网页
from bs4 import BeautifulSoup
from celery import Celery

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

celery_app = Celery('info_engine', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)

websites = get_websites()  # 网址列表=数据库的获取网站方法
# websites = get_websites_desc()


@celery_app.task
def extract(w_id):
    """
    语法糖方法：ccelery应用.任务，提取
    """
    try:
        # 从数据库获取网址
        w = get_website(w_id)
        # log(NOTICE, "开始 #{id} {name} {site} ".format(id=w.id, name=w.company.name_cn, site=w.url))

        # 爬取网页
        new_html_content = crawl(w.url)
        # 如果没有内容，返回
        if not new_html_content:
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        # 如果数据库中已经保存了该网页内容
        if w.html_content:
            # 提取内容，待比较
            old_html_content = w.html_content.content
        # 如果数据库原来没有的该网页内容
        else:
            # 保存
            save_html_content(w.id, new_html_content)
            # 生成日志，返回
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        # 比较新旧两网页内容
        diff_text = diff_file(old_html_content, new_html_content)
        # 如果一样，就生成日志，返回
        if not diff_text:
            log(NOTICE, "#{id} {name} {site} 抓到更新 0 条".format(id=w.company.id, name=w.company.name_cn, site=w.url))
            return

        # 保存新内容
        save_html_content(w.id, new_html_content)

        # 更新的内容，使用lxml HTML解析
        soup = BeautifulSoup(diff_text, 'lxml')
        # 所有<a>标签
        items = soup.find_all('a')
        # 计数
        COUNT = 0
        # 有<a>标签
        if items:
            # 分别处理
            for a in items:
                # 字符串
                if a.string:
                    # href网址，描述
                    url, text = a.get('href'), a.string
                    # 检查url和标题
                    check_pass = check_content(url, text)
                    # 通过
                    if check_pass:
                        # 补全url
                        url = complement_url(url, w.url)
                        # 补全后url还在
                        if url:
                            # 保存
                            result = save_info_feed(url, text, w.id, w.company.id)
                            # 保存成功则计数+1
                            if result:
                                COUNT += 1
                            # log(RECORD, "[name] [+] [{url}  {text}]".format(name=w.company.name_cn, url=url, text=text.strip()))
        # 完成后计数还为0
        if COUNT == 0:
            # 日志提示
            log(NOTICE, "#{id} {name} {site} 抓到更新 {count} 条".format(id=w.company.id, name=w.company.name_cn, site=w.url, count=COUNT))
        else:
            # 日志记录
            log(RECORD, "#{id} {name} {site} 抓到更新 {count} 条".format(id=w.company.id, name=w.company.name_cn, site=w.url, count=COUNT))

    except Exception as e:
        try:
            w = get_website(w_id)
            log(ERROR, "#{id} {name} {site} {err}".format(id=w.id, name=w.company.name_cn, site=w.url, err=str(e)))
        except Exception as e:
            log(ERROR, str(e))


def gen_info():
    # random.shuffle(websites)
    for w in websites[:]:
        if (w.url not in blacklist_site) and (w.company.name_cn not in blacklist_company):
            extract.delay(w.id)


if __name__ == '__main__':
    while True:
        gen_info()
        time.sleep(60 * CRAWL_INTERVAL)
