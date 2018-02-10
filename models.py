"""
用于初始化数据库表，需提前在config.py中配置数据库
"""
import os
import sys

from sqlalchemy import ForeignKey  # 外键类
from sqlalchemy import create_engine  # 创建数据库表引擎方法
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Sequence  # 表项的类型
from sqlalchemy import func  # 函数
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from config import DB  # 导入数据库配置

# 绝对路径（路径添加（文件路径 /or\, ..）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 添加系统的环境变量
sys.path.append(BASE_DIR)
# 创建数据库引擎实例
engine = create_engine('mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8'.format(
    USERNAME=DB['USER'],
    PASSWORD=DB['PASSWORD'],
    HOST=DB['HOST'],
    PORT=DB['PORT'],
    DB_NAME=DB['DB_NAME'],
), convert_unicode=True, echo=False)  # 不返回SQL语句,调试用
# 创建数据库会话（数据库工厂（自动提交，自动设置，引擎实例））
DBSession = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))

Base = declarative_base()  # 数据库模型基类
Base.query = DBSession.query_property()
Base = declarative_base()


def init_db(db_engine):
    """
    数据库初始化函数
    """
    Base.metadata.create_all(bind=db_engine)  # 创建所有继承于Base的数据表
    # Base.metadata.tables["log"].create(bind=db_engine)


class User(Base):  # 继承于Base
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(128))
    email = Column(String(128))
    password = Column(String(128))
    is_admin = Column(Boolean(), default=False)
    last_login = Column(DateTime(timezone=True), default=func.now())
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return "<User(username='%s', email='%s')>" % (self.username, self.email)


class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, Sequence('company_id_seq'), primary_key=True)
    name_cn = Column(String(128))
    name_en = Column(String(128))
    industry = Column(String(256))
    website = relationship("Website", uselist=False, back_populates="company")
    info_feed = relationship("InfoFeed", back_populates="company")
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return "<Company(name='%s')>" % self.name_en


class CompanyProfle(Base):
    # 企业、网址、公关联系人、股市代码
    __tablename__ = 'company_profile'
    id = Column(Integer, Sequence('company_profile_id_seq'), primary_key=True)
    company_id = Column(Integer)
    portal = Column(String(1024))
    contact = Column(String(128))
    stock_code = Column(String(128))


class Website(Base):
    __tablename__ = 'website'
    id = Column(Integer, Sequence('website_id_seq'), primary_key=True)
    url = Column(String(1024))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship("Company", back_populates="website")
    info_feed = relationship("InfoFeed", back_populates="website")
    html_content = relationship("HtmlContent", uselist=False, back_populates="website")
    create_at = Column(DateTime(timezone=True), default=func.now())
    update_at = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return "<Website(id='%s')>" % self.id


class HtmlContent(Base):
    """
    注意：!!! content字段需要手动改Mysql Column类型为LONGTEXT
    """
    __tablename__ = 'html_content'
    id = Column(Integer, Sequence('html_id_seq'), primary_key=True)
    content = Column(Text)
    website_id = Column(Integer, ForeignKey('website.id'))
    website = relationship("Website", uselist=False, back_populates="html_content")
    update_at = Column(DateTime(timezone=True), default=func.now())


class InfoFeed(Base):
    __tablename__ = 'info_feed'
    id = Column(Integer, Sequence('info_id_seq'), primary_key=True)
    url = Column(String(1024))
    text = Column(String(1024))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship("Company", back_populates="info_feed")
    website_id = Column(Integer, ForeignKey('website.id'))
    website = relationship("Website", back_populates="info_feed")
    create_at = Column(DateTime(timezone=True), default=func.now())


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, Sequence('keyword_id_seq'), primary_key=True)
    text = Column(String(256))
    create_at = Column(DateTime(timezone=True), default=func.now())


class ContactPerson(Base):
    __tablename__ = 'contact_person'
    id = Column(Integer, Sequence('contact_id_seq'), primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'))
    name = Column(String(1024))  # 姓名
    gender = Column(String(1024))  # 性别
    age = Column(Integer)
    position = Column(String(1024))  # 职位
    phone_number = Column(String(1024))  # 电话
    wechat = Column(String(1024))  # 微信
    email = Column(String(1024))  # 邮箱
    comment = Column(String(1024))  # 备注
    create_at = Column(DateTime(timezone=True), default=func.now())


class Report(Base):
    """
    标题 导语 作者 责任编辑 关键字 正文
    """
    __tablename__ = 'report'  # 表名
    id = Column(Integer, Sequence('report_id_seq'), primary_key=True)
    title = Column(String(1024))
    lead = Column(Text)
    author = Column(String(256))
    editor = Column(String(256))
    tags = Column(String(1024))
    content = Column(Text)
    update_at = Column(DateTime(timezone=True), default=func.now())
    create_at = Column(DateTime(timezone=True), default=func.now())


class CrawlerLOG(Base):
    __tablename__ = 'log'
    id = Column(Integer, Sequence('log_id_seq'), primary_key=True)
    level = Column(Integer)
    text = Column(Text)
    create_at = Column(DateTime(timezone=True), default=func.now())


if __name__ == '__main__':
    init_db(engine)  # 初始化数据库
    # pass
