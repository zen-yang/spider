import os
import requests
import config
from pyquery import PyQuery as pq

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Boolean,
    String,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)


def configured_engine():
    url = 'mysql+pymysql://root:{}@localhost:3306/{}?charset=utf8mb4'.format(
        config.mysql_password,
        config.mysql_db,
    )
    e = create_engine(url, echo=True)
    return e


SQLBase = declarative_base()


def reset_database():
    url = 'mysql+pymysql://root:{}@localhost:3306/?charset=utf8mb4'.format(
        config.mysql_password
    )
    print('sql url', url)
    e = create_engine(url, echo=True)

    with e.connect() as c:
        db = config.mysql_db

        c.execute('DROP DATABASE IF EXISTS {}'.format(db))
        c.execute('CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'.format(db))
        c.execute('USE {}'.format(db))

    SQLBase.metadata.create_all(bind=e)


class SQLMixin(object):
    session = scoped_session(sessionmaker(bind=configured_engine()))
    query = session.query_property()

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, nullable=False, default=False)

    # created_time = Column(Integer, nullable=False)
    # updated_time = Column(Integer, nullable=False)
    #
    # def add_default_value(self):
    #     timestamp = int(time.time())
    #     self.created_time = timestamp
    #     self.updated_time = timestamp

    @classmethod
    def new(cls, **kwargs):
        m = cls()
        for name, value in kwargs.items():
            setattr(m, name, value)
        # m.add_default_value()

        cls.session.add(m)
        cls.session.commit()

        return m

    def __repr__(self):
        s = ''
        for attr, column in self.__mapper__.c.items():
            if hasattr(self, attr):
                v = getattr(self, attr)
                s += '{}: ({})\n'.format(attr, v)
        return '< {}\n{} >\n'.format(self.__class__.__name__, s)


class Movie(SQLMixin, SQLBase):
    __tablename__ = 'Movie'
    name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False, default='0')
    quote = Column(String(100), nullable=False)
    cover_url = Column(String(100), nullable=False)
    ranking = Column(Integer, nullable=False, default='0')


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


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        get(m.cover_url, filename)


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


def get_movies():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)

        for m in movies:
            print('test', m.__dict__)
            Movie.new(**m.__dict__)


def main():
    reset_database()
    get_movies()


if __name__ == '__main__':
    main()
