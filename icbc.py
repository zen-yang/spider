import csv
import requests
from pyquery import PyQuery as pq
import time
import sched


class Rate(object):
    def __init__(self):
        self.currency = ''
        self.current_purchase_price = ''
        self.cash_purchase_price = ''
        self.current_offer = ''
        self.cash_sale_price = ''
        self.release_time = ''


def exchange_rate_from_div(td):
    e = pq(td)
    d = e('.tdCommonTableData').text()
    price = d[d.find('(') + 6: d.find('2018å') - 1].split()
    day1 = d[d.find('å¹') - 4: d.find('å¹')]
    day2 = d[d.find('å¹´') + 3: d.find('å¹´') + 5]
    day3 = d[d.find('æ¥ ') - 2: d.find('æ¥ ')]
    day4 = d[d.find('æ¥ ') + 4:]

    r = Rate()
    r.currency = d[d.find('(') + 1: d.find('(') + 4]
    r.current_purchase_price = str(price[0:1])[2:-2]
    r.cash_purchase_price = str(price[1:2])[2:-2]
    r.current_offer = str(price[2:3])[2:-2]
    r.cash_sale_price = str(price[3:4])[2:-2]
    r.release_time = '{}/{}/{} {}'.format(day1, day2, day3, day4)

    return r


def exchange_rates_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的汇率数据
    """
    r = requests.get(url)
    page = r.content
    e = pq(page)
    items = e('.tableDataTable tr')
    rates = [exchange_rate_from_div(i) for i in items][1:]

    return rates


def main():
    with open('icbc.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['currency', 'current_purchase_price', 'cash_purchase_price',
                      'current_offer', 'cash_sale_price', 'release_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, 250, 25):
            url = 'http://www.icbc.com.cn/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx'
            exchange_rates = exchange_rates_from_url(url)
            for e in exchange_rates:
                print('icbc exchange rates', e.__dict__)
                writer.writerow(e.__dict__)


def timer():
    time_format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, value)
    print('第1次爬取', formatted)
    main()
    count = 1
    while count <= 3:
        s = sched.scheduler(time.time, time.sleep)
        s.enter(60, 1, main, ())
        # 这里的60是60秒的意思,若想定时获取，改变数字即可60*60
        s.run()
        count += 1
        value = time.localtime(int(time.time()))
        dt = time.strftime(format, value)
        print('第{}次爬取'.format(count), dt)


if __name__ == '__main__':
    timer()
