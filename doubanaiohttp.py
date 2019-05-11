import os
import time
import asyncio
import itertools
from aiohttp import ClientSession
from pyquery import PyQuery as pq


class Model(object):
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.other = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


class Session(ClientSession):
    def __init__(self, cache_dir_path='douban', **kwargs):
        super().__init__(**kwargs)
        self.cache_dir_path = cache_dir_path

    async def get(self, url, filename, **kwargs):
        """
        缓存, 避免重复下载网页浪费时间
        """

        path = os.path.join(self.cache_dir_path, filename)

        # 从缓存获取
        if os.path.exists(path):
            with open(path, 'rb') as f:
                content = f.read()
                # 检验 cache 的完整性
                # 如不完整则需要重新通过网络 get
                if validate_content(content):
                    return content

        # 从网络获取
        async with super().get(url, **kwargs) as r:
            content = await r.content.read()

            # 写入文件前，确保目录存在
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as file:
                file.write(content)

            return content


def validate_content(content):
    """
    主要用于判断是否需要重新通过网络 get
    """
    # 暂且只做个简单的长度判断
    return len(content) > 1024


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = Movie()
    m.name = e('.title').text()
    m.other = e('.other').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic').find('em').text()
    return m


async def save_cover(movies, session):
    tasks = []
    for m in movies:
        url = m.cover_url
        filename = '{}.jpg'.format(m.ranking)
        t = session.get(url, filename)
        tasks.append(t)

    await asyncio.wait(tasks)


async def movies_from_url(url, session):
    """
    从 url 中下载网页并解析出页面内所有的电影
    """
    # https://movie.douban.com/top250?start=100
    filename = '{}.html'.format(url.split('=', 1)[-1])
    page = await session.get(url, filename)
    e = pq(page)
    items = e('.item')
    # 调用 movie_from_div
    movies = [movie_from_div(i) for i in items]
    return movies


async def run(**kwargs):
    """
    爬虫执行的入口，构造 url
    """
    async with Session(**kwargs) as session:
        url = 'https://movie.douban.com/top250?start={}'
        tasks = (movies_from_url(url.format(i), session) for i in range(0, 250, 25))

        rs = await asyncio.gather(*tasks)
        movies = itertools.chain(*rs)

        # 仅用于显示
        movies, movies_for_print = itertools.tee(movies)
        for a in movies_for_print:
            print(a)

        await save_cover(movies, session)


def main():
    start_time = time.time()
    config = dict(
        # 缓存目录路径
        cache_dir_path='douban',
        # 频繁请求会被服务器拒绝响应
        # 若不及时断开，则会长时间处于等待状态，浪费时间
        # 由于有做缓存，不用担心中断，多次执行程序直到抓取完即可
        read_timeout=5,
        # 如果需要模拟登陆状态，可以直接 copy 浏览器的 cookie
        # hedaers={
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        #                   'AppleWebKit/537.36 (KHTML, like Gecko) '
        #                   'Chrome/62.0.3202.94 Safari/537.36 ',
        #     'Cookie': secret.cookie,
        # },
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(**config))
    loop.close()

    print('\n耗时 {} second'.format(time.time() - start_time))
    # 耗时 2.7962474822998047 second
    # 用request库的爬虫耗时 33.42990970611572 second


if __name__ == '__main__':
    main()
