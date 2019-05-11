import os
import requests
import config
import pymysql.cursors
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


def create_db_tb():
    db = pymysql.connect(config.host, config.user, config.password, port=3306)
    cursor = db.cursor()
    cursor.execute('SELECT VERSION()')
    data = cursor.fetchone()
    print('Database version:', data)
    cursor.execute("DROP DATABASE IF EXISTS doubanmysql")
    cursor.execute("CREATE DATABASE doubanmysql DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute("USE doubanmysql")
    sql = """
    CREATE TABLE top250(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    score FLOAT NOT NULL default '0',
    quote VARCHAR(255) NOT NULL,
    cover_url VARCHAR(255) NOT NULL,
    ranking INT NOT NULL default '0'
    )
    """

    cursor.execute(sql)
    db.close()


def insert():
    # Connect to the database
    connection = pymysql.connect(config.host,
                                 config.user,
                                 config.password,
                                 db='doubanmysql',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = """
            INSERT INTO top250(name, score, quote, cover_url, ranking)
            VALUES (%s, %s, %s, %s, %s)
            """
            for i in range(0, 250, 25):
                url = 'https://movie.douban.com/top250?start={}'.format(i)
                movies = movies_from_url(url)
                for m in movies:
                    name = m.__dict__['name']
                    score = m.__dict__['score']
                    quote = m.__dict__['quote']
                    cover_url = m.__dict__['cover_url']
                    ranking = m.__dict__['ranking']

                    cursor.execute(sql, (name, score, quote, cover_url, ranking))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM top250"
            cursor.execute(sql)
            result = cursor.fetchall()

            for row in result:
                properties = ('{}=({})'.format(k, v) for k, v in row.items())
                s = '\n<{} \n  {}>'.format('top250', '\n  '.join(properties))
                print(s)
    except:
        connection.rollback()
    finally:
        connection.close()


if __name__ == '__main__':
    create_db_tb()
    insert()
