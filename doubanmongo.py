import os
import pymongo
import requests
from pyquery import PyQuery as pq


class Movie(object):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def get(url, filename):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'douban'
    # 建立 cached 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = Movie()
    m.name = e('.title').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic em').text()
    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    # https://movie.douban.com/top250?start=100
    filename = '{}.html'.format(url.split('=', 1)[-1])
    page = get(url, filename)
    e = pq(page)
    items = e('.item')
    # 调用 movie_from_div
    movies = [movie_from_div(i) for i in items]
    save_cover(movies)
    return movies


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        get(m.cover_url, filename)


def configured_db():
    # 连接 mongo 数据库, 主机是本机, 端口是默认的端口
    client = pymongo.MongoClient("mongodb://localhost:27017")

    # 设置要使用的数据库
    mongodb_name = 'doubanmongo'
    # 直接这样就使用数据库了，相当于一个字典
    db = client[mongodb_name]
    return db


def insert(db):
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        for m in movies:
            form = dict(
                name=m.__dict__['name'],
                score=m.__dict__['score'],
                quote=m.__dict__['quote'],
                cover_url=m.__dict__['cover_url'],
                ranking=m.__dict__['ranking'],
            )

            db.top250.insert(form)
            # 相当于 db['top250'].insert


def main():
    db = configured_db()
    insert(db)


if __name__ == '__main__':
    main()
