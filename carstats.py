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
from titlecase import titlecase
from urllib2 import build_opener, HTTPCookieProcessor
from matplotlib.ticker import FuncFormatter
from statsmodels.api import OLS, add_constant

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
# url = 'http://www.autotrader.ca/cars/mercedes-benz/e-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000'


def num_comma(x, pos):
    return '{0:,.0f}'.format(x)

FORMATTER_COMMA = FuncFormatter(num_comma)


class CarStats(object):
    def __init__(self, url, max_km=200000, max_age=15):
        # Prase html
        if 'rcp=' not in url:
            url += 'rcp=1000'
        url_split = url.split('/')
        opener = build_opener(HTTPCookieProcessor())
        opener.addheaders = [('User-Agent', 'Mozilla/5.0'),
                             ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        response = opener.open(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")
        df = self._parse_html(soup)
        self.df = df.query('km <= @max_km and age <= @max_age')

        self.car_model = '{}_{}_{}'.format(url_split[3], url_split[4], url_split[5])
        self.name = titlecase('{} {}'.format(url_split[4], url_split[5]))
        self.report_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reports')
        self.model = None

        if not (os.path.isdir(self.report_path)):
            os.mkdir(self.report_path)

    def get_df(self):
        return self.df

    def gen_ols(self):
        df_raw = self.df.copy()
        df_scaled = self._normalize(df_raw)
        self.model = OLS(df_scaled.price, add_constant(df_scaled[['km', 'age']]))
        print self.model.fit().summary()
        return self.model

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
        <img src="{img_3}" alt="Opps...can't display image">

        """.format(report_name=self.name,
                   ols=self.gen_ols().fit().summary().as_html(),
                   img_1=os.path.basename(self.gen_graph_age_vs_price(show=False)),
                   img_2=os.path.basename(self.gen_graph_km_vs_price(show=False)),
                   img_3=os.path.basename(self.gen_boxplot_by_age(show=False)))
        f.write(html)
        f.close()
        if show:
            webbrowser.open('file://' + html_file_path)

    def predict(self, age, km, html=True, show=True):
        if self.model == None:
            self.gen_ols()
        fitted_model = self.model.fit()
        km_scaled = self._scaler(km, 'km')
        age_scaled = self._scaler(age, 'age')
        pred_scaled = fitted_model.predict([1, km_scaled, age_scaled])
        pred = self._scaler(pred_scaled, 'price', inverse=True)
        return pred[0]

    def gen_boxplot_by_age(self, show=False, fig_size=(6, 4)):
        fig_name = self.car_model + "_boxplot_age.png"
        plot_path = os.path.join(self.report_path, fig_name)
        ax = self.df[['age', 'price']].boxplot(by='age',figsize=fig_size)
        ax.yaxis.set_major_formatter(FORMATTER_COMMA)
        plt.savefig(plot_path,transparent=True,bbox_inches='tight')
        if show:
            plt.show()
        return plot_path

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
        ax = self.df.plot(x=x, y=y, kind='scatter', figsize=figsize, title='{} vs {}'.format(x, y))
        ax.yaxis.set_major_formatter(FORMATTER_COMMA)
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.savefig(plot_path,transparent=True,bbox_inches='tight')
        if show:
            plt.show()
        return plot_path

    @staticmethod
    def _parse_html(soup):
        """
        parse the beautiful soup object into a pandas DataFrame
        :param soup:
        :return: df
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

    def _scaler(self, value, column, inverse=False):
        means = self.df.mean()
        stds = self.df.std()

        if inverse:
            out = (value * stds[column]) + means[column]
        else:
            out = (value - means[column]) / stds[column]
        return out

    @staticmethod
    def _normalize(df):
        """
        Z-score normalization
        :param df: DataFrame
        :return: DataFrame
        """
        return (df - df.mean()) / df.std()


if __name__ == '__main__':
    mercedes_e = CarStats(
        'http://www.autotrader.ca/cars/mercedes-benz/e-class/on/toronto/?prx=100&prv=Ontario&loc=m5p3h6&sts=New-Used&hprc=True&wcp=True&rcs=0&rcp=1000')
    mercedes_e.html_report(show=True)
