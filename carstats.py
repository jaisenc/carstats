"""
Created on 1/24/2017, 4:32 PM

@author: jason.chen
"""
import datetime
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from bs4 import BeautifulSoup
from urllib2 import build_opener, HTTPCookieProcessor
from pandas.stats.api import ols
import webbrowser

matplotlib.style.use('ggplot')

# mercedes c300
# url = 'http://www.autotrader.ca/cars/mercedes-benz/c-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'
# mercedes glk
# url = 'http://www.autotrader.ca/cars/mercedes-benz/glk-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'
# lexus rx (RX 350)
# url = 'http://www.autotrader.ca/cars/lexus/rx/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'
# toyota camry
# url = 'http://www.autotrader.ca/cars/toyota/camry/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'
# mercedes e class
url = 'http://www.autotrader.ca/cars/mercedes-benz/e-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'


class CarStats(object):
    def __init__(self, url):
        url_split = url.split('/')
        opener = build_opener(HTTPCookieProcessor())
        opener.addheaders = [('User-Agent', 'Mozilla/5.0'),
                             ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        response = opener.open(url)
        html = response.read()

        soup = BeautifulSoup(html, "lxml")
        self.df = self._parse_html(soup)
        self.car_model = '{}_{}_{}'.format(url_split[3], url_split[4], url_split[5])
        self.name = '{} {}'.format(url_split[4], url_split[5])
        self.ols_summary = ''
        self.report_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reports')

        if not (os.path.isdir(self.report_path)):
            os.mkdir(self.report_path)

    def gen_ols(self, max_km=300000):
        df_raw = self.df.query("km <= @max_km")
        res = ols(y=df_raw.price, x=df_raw[['km', 'age']])
        print res.summary
        self.ols_summary = res.summary
        return res

    def gen_graph_km_vs_price(self, show=False):
        fig_name = '{}_age_vs_km.png'.format(self.car_model)
        return self.gen_scatter_plot(x='km', y='price', fig_name=fig_name)

    def gen_graph_age_vs_price(self, show=False):
        fig_name = '{}_age_vs_price.png'.format(self.car_model)
        return self.gen_scatter_plot(x='age', y='price', fig_name=fig_name)

    def html_report(self, show=True):
        html_file_path = os.path.join(self.report_path, self.car_model + '.html')
        f = open(html_file_path, 'wb')
        html = """
        <h1>{report_name} Statistics</h1>
        <h2>Linear Regression</h2>
        <p>{ols}</p>
        <img src="{img_1}" alt="Opps...can't display image">
        <img src="{img_2}" alt="Opps...can't display image">

        """.format(report_name=self.name,
                   ols=self.gen_ols(),
                   img_1=os.path.basename(self.gen_graph_age_vs_price(show=False)),
                   img_2=os.path.basename(self.gen_graph_km_vs_price(show=False)))
        f.write(html)
        f.close()
        if show:
            webbrowser.open('file://' + html_file_path)

    def predict(self, age, km, html=True, show=True):
        pass

    def gen_scatter_plot(self, x, y, fig_name, show=False, figsize=(6, 4)):
        """
        Generate a scatter plot and save the image in the report parth

        :param x:
        :param y:
        :param fig_name:
        :param show:
        :param figsize:
        :return:
        """
        plot_path = os.path.join(self.report_path, fig_name)
        self.df.plot(x=x, y=y, kind='scatter', figsize=figsize, title='{} vs {}'.format(x, y))
        plt.savefig(plot_path)
        if show:
            plt.show()
        return plot_path

    @staticmethod
    def _parse_html(soup):
        """
        parse the beautiful soup object into a pandas DataFrame
        :param soup:
        :return:
        """
        out = []
        num_skipped = 0
        for resultItem in soup.findAll('div', class_='resultItem'):
            if resultItem.getText().find(' ') <> -1:
                try:
                    year = int(resultItem.find('span', class_='resultTitle').getText().split()[0])
                    if resultItem.getText().find('NEW VEHICLE') <> -1:
                        km = 0
                    else:
                        km = int(resultItem.find("div", class_="at_km").string.split()[0].replace(',', ''))
                    price = int(resultItem.find("div", class_="at_price").text.split()[0][1:].replace(',', ''))
                    out.append([km, price, year])
                except:
                    num_skipped += 1
            else:
                num_skipped += 1
        print 'Total Skipped {}'.format(num_skipped)
        print 'Total length {}'.format(len(out))
        df = pd.DataFrame(out, columns=['km', 'price', 'year'])
        df['age'] = datetime.datetime.today().year - df.year
        return df


if __name__ == '__main__':
    mercedes_e = CarStats(
        'http://www.autotrader.ca/cars/mercedes-benz/e-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000')
    mercedes_e.html_report(show=True)
