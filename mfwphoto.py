import os
import requests
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


class Photopk(Model):
    """
    存储照片PK往期回顾信息
    """

    def __init__(self):
        self.theme_num = ''
        self.theme = ''
        self.date = ''
        self.ranking1 = ''
        self.photo_name1 = ''
        self.photo_link1 = ''
        self.author1 = ''
        self.author_link1 = ''
        self.votes1 = ''
        self.award1 = ''
        self.ranking2 = ''
        self.photo_name2 = ''
        self.photo_link2 = ''
        self.author2 = ''
        self.author_link2 = ''
        self.votes2 = ''
        self.award2 = ''
        self.ranking3 = ''
        self.photo_name3 = ''
        self.photo_link3 = ''
        self.author3 = ''
        self.author_link3 = ''
        self.votes3 = ''
        self.award3 = ''


def get(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3202.94 Safari/537.36',

    }
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'mfwphotopk'
    # 建立 mfwphotopk 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers=headers)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def photopk_from_div(div):
    """
    从一个 div 里面获取到一个照片PK往期回顾信息
    """
    e = pq(div)

    p = Photopk()
    theme_str = e('.th').text()
    theme_num_end = theme_str.find('期')
    p.theme_num = theme_str[1:theme_num_end]
    p.theme = e('.th span:first-child').text()
    p.date = e('.th span:last-child').text().strip('(').strip(')')
    p.ranking1 = e('li:first-child b').text()[3:]
    p.photo_name1 = e('li:first-child p').text()[5:]
    p.photo_link1 = e('li:first-child .pic img').attr('src')
    p.author1 = e('li:first-child dl dd a').text()
    p.author_link1 = 'http://www.mafengwo.cn{}'.format(e('li:first-child dl dd a').attr('href'))
    p.votes1 = e('li:first-child dl .vote span').text()
    p.award1 = e('li:first-child dl dd').eq(1).text()[3:]
    p.ranking2 = e('li:nth-child(2) b').text()[3:]
    p.photo_name2 = e('li:nth-child(2) p').text()[5:]
    p.photo_link2 = e('li:nth-child(2) .pic img').attr('src')
    p.author2 = e('li:nth-child(2) dl dd a').text()
    p.author_link2 = 'http://www.mafengwo.cn{}'.format(e('li:nth-child(2) dl dd a').attr('href'))
    p.votes2 = e('li:nth-child(2) dl .vote span').text()
    p.award2 = e('li:nth-child(2) dl dd').eq(1).text()[3:]
    p.ranking3 = e('li:last-child b').text()[3:]
    p.photo_name3 = e('li:last-child p').text()[5:]
    p.photo_link3 = e('li:last-child .pic img').attr('src')
    p.author3 = e('li:last-child dl dd a').text()
    p.author_link3 = 'http://www.mafengwo.cn{}'.format(e('li:last-child dl dd a').attr('href'))
    p.votes3 = e('li:last-child dl .vote span').text()
    p.award3 = e('li:last-child dl dd').eq(1).text()[3:]

    return p


def save_cover(photos):
    for p in photos:
        photo_link1 = p.photo_link1
        if photo_link1 != None:
            filename1 = '{}-{}.jpg'.format(p.theme, p.ranking1)
            photo_link2 = p.photo_link2
            filename2 = '{}-{}.jpg'.format(p.theme, p.ranking2)
            photo_link3 = p.photo_link3
            filename3 = '{}-{}.jpg'.format(p.theme, p.ranking3)

            form = {
                filename1: photo_link1,
                filename2: photo_link2,
                filename3: photo_link3,
            }

            for i in form:
                filename = i
                link = form[filename]
                get(link, filename)


def photos_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的照片信息
    """
    filename = '{}.html'.format(url.split('=', 1)[-1])
    page = get(url, filename)
    e = pq(page)

    items = e('.before_c').children()[0:-1]
    # 调用 photopk_from_div
    photos = [photopk_from_div(i) for i in items]
    save_cover(photos)
    return photos


def main():
    for i in range(0, 75, 5):
        url = 'http://www.mafengwo.cn/photo_pk/prev.php?offset={}'.format(i)
        photos = photos_from_url(url)
        print('mfw photos', photos)


if __name__ == '__main__':
    main()
