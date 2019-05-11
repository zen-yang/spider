import os
import csv
import time
import requests
import gevent

import threadpool
from threading import Thread
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor

from pyquery import PyQuery as pq
from gevent import monkey

monkey.patch_all()


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


# def movies_from_url(url):
#     """
#     从 url 中下载网页并解析出页面内所有的电影
#     """
#     # https://movie.douban.com/top250?start=100
#     filename = '{}.html'.format(url.split('=', 1)[-1])
#     page = get(url, filename)
#     e = pq(page)
#     items = e('.item')
#     # 调用 movie_from_div
#     movies = [movie_from_div(i) for i in items]
#     save_cover(movies)
#     return movies


# def main():
#     start_time = time.time()
#     with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for i in range(0, 250, 25):
#             url = 'https://movie.douban.com/top250?start={}'.format(i)
#             movies = movies_from_url(url)
#             for m in movies:
#                 print('top250 movies', m.__dict__)
#                 writer.writerow(m.__dict__)
#
#     print('%d second' % (time.time() - start_time))
#     # 普通爬虫下载网页+图片+数据存入data.csv，耗时 35 second


# def movies_from_url(url):
#     """
#     从 url 中下载网页并解析出页面内所有的电影
#     """
#     # https://movie.douban.com/top250?start=100
#     filename = '{}.html'.format(url.split('=', 1)[-1])
#     page = get(url, filename)
#     e = pq(page)
#     items = e('.item')
#     # 调用 movie_from_div
#     movies = [movie_from_div(i) for i in items]
#     save_cover(movies)
#     # 写进data.csv文件
#     with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         for m in movies:
#             print('top250 movies', m.__dict__)
#             writer.writerow([
#                 m.__dict__['name'],
#                 m.__dict__['score'],
#                 m.__dict__['quote'],
#                 m.__dict__['cover_url'],
#                 m.__dict__['ranking']
#             ])
#
#
# def table_head():
#     try:
#         file = open('data.csv', 'a', newline='', encoding='utf-8')
#         fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#     finally:
#         file.close()
#
#
# def main():
#     start_time = time.time()
#
#     table_head()
#
#     url = ['https://movie.douban.com/top250?start={}'.format(i) for i in range(0, 250, 25)]
#     pool = threadpool.ThreadPool(8)
#     requests = threadpool.makeRequests(movies_from_url, url)
#     [pool.putRequest(req) for req in requests]
#     pool.wait()
#
#     print('\n耗时 {} second'.format(time.time() - start_time))
#     # 用线程池爬虫下载网页+图片+数据存入data.csv
#     # 先创建data.csv和表头，然后再写入数据，耗时 7.36 second
#     # data.csv文件的输出顺序是乱的，猜测是线程池，程序执行顺序问题


# def movies_from_url(url):
#     """
#     从 url 中下载网页并解析出页面内所有的电影
#     """
#     # https://movie.douban.com/top250?start=100
#     filename = '{}.html'.format(url.split('=', 1)[-1])
#     page = get(url, filename)
#     e = pq(page)
#     items = e('.item')
#     # 调用 movie_from_div
#     movies = [movie_from_div(i) for i in items]
#     save_cover(movies)
#     # 写进data.csv文件
#     with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for m in movies:
#             print('top250 movies', m.__dict__)
#             writer.writerow(m.__dict__)
#
#
# def main():
#     start_time = time.time()
#
#     url = ['https://movie.douban.com/top250?start={}'.format(i) for i in range(0, 250, 25)]
#     pool = threadpool.ThreadPool(8)
#     requests = threadpool.makeRequests(movies_from_url, url)
#     [pool.putRequest(req) for req in requests]
#     pool.wait()
#
#     print('\n耗时 {} second'.format(time.time() - start_time))
#     # 用线程池爬虫下载网页+图片+数据存入data.csv
#     # 跟上一部分代码对比，每次以追加的形式写入表头和数据，耗时 7.20 second
#     # data.csv文件的输出顺序是乱的，猜测是线程池，程序执行顺序问题


# def movies_from_url(url):
#     """
#     从 url 中下载网页并解析出页面内所有的电影
#     """
#     # https://movie.douban.com/top250?start=100
#     filename = '{}.html'.format(url.split('=', 1)[-1])
#     page = get(url, filename)
#     e = pq(page)
#     items = e('.item')
#     # 调用 movie_from_div
#     movies = [movie_from_div(i) for i in items]
#     save_cover(movies)
#     # 写进data.csv文件
#     with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for m in movies:
#             print('top250 movies', m.__dict__)
#             writer.writerow(m.__dict__)
#
#
# def main():
#     start_time = time.time()
#
#     url = ['https://movie.douban.com/top250?start={}'.format(i) for i in range(0, 250, 25)]
#
#     threads = []
#     for u in url:
#         t = Thread(target=movies_from_url, args=[u])
#         t.start()
#         threads.append(t)
#
#     for t in threads:
#         t.join()
#
#     print('\n耗时 {} second'.format(time.time() - start_time))
#     # 用新开线程的方式，爬虫下载网页+图片+数据存入data.csv
#     # 每次以追加的形式写入表头和数据，耗时 5.05 second
#     # data.csv文件的输出顺序是乱的，猜测是开新线程执行顺序问题


# def movies_from_url(url):
#     """
#     从 url 中下载网页并解析出页面内所有的电影
#     """
#     # https://movie.douban.com/top250?start=100
#     filename = '{}.html'.format(url.split('=', 1)[-1])
#     page = get(url, filename)
#     e = pq(page)
#     items = e('.item')
#     # 调用 movie_from_div
#     movies = [movie_from_div(i) for i in items]
#     save_cover(movies)
#     # 写进data.csv文件
#     with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for m in movies:
#             print('top250 movies', m.__dict__)
#             writer.writerow(m.__dict__)
#
#
# def main():
#     start_time = time.time()
#
#     for i in range(0, 250, 25):
#         url = 'https://movie.douban.com/top250?start={}'.format(i)
#
#         p = Pool(8)
#         p.apply_async(movies_from_url, args=(url,))
#         p.close()
#         p.join()
#
#     print('\n耗时 {} second'.format(time.time() - start_time))
#     # 用进程池的方式，爬虫下载网页+图片+数据存入data.csv，耗时 38.11 second
#     # data.csv文件的输出顺序正确


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
    # 写进data.csv文件
    with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'score', 'quote', 'cover_url', 'ranking']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for m in movies:
            print('top250 movies', m.__dict__)
            writer.writerow(m.__dict__)


def main():
    start_time = time.time()

    url = ['https://movie.douban.com/top250?start={}'.format(i) for i in range(0, 250, 25)]

    jobs = [gevent.spawn(movies_from_url, u) for u in url]
    gevent.joinall(jobs)
    [job.value for job in jobs]

    print('\n耗时 {} second'.format(time.time() - start_time))
    # 用gevent加猴子补丁方法，耗时 26.9 second
    # data.csv文件的输出顺序乱的。
    # 如果先下载html和图片，用时3秒，再写进data.csv用时0.36秒左右，输出的数据是按顺序的


if __name__ == '__main__':
    main()
