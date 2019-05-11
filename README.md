# doubananiohttp.py
用 aiohttp 爬取豆瓣电影T250。

# 实现的主要功能

1. 获取电影的基本信息
2. 下载电影的图片
3. 使用了缓存功能

# doubancsv.py
用普通方法、线程池、新开线程、进程池、gevent 加猴子补丁等方法，测试爬取豆瓣电影T250，
在上面功能的基础上，把电影的基本信息存到 csv 文件中。

# doubanamango.py
将爬取豆瓣电影T250的信息存到 mangodb 数据库中。

# doubanamysql.py
将爬取豆瓣电影T250的信息存到 MySQL 数据库中。

# doubanasqlacl.py
用 sqlalchemy 将爬取豆瓣电影T250的信息存到 MySQL 数据库中。

# icbc.py
将爬取 icbc 汇率的信息存到 csv 文件中。

# mfwphotopk.py
爬取 马蜂窝照片PK往期回顾 中的照片信息、下载了图片、做了缓存功能。
