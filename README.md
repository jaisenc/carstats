# carstats
Statistic analysis on used car prices in Canada. The package predicts a car's market value, and determines if a particular posting is undervalue or overvalue.

The package pulls live data from [AutoTrader](http://www.autotrader.ca/) and provides analysis on a search on the AutoTrader website.  

## Example

Run analysis on all postings of Mercedes E-Class near downtown Toronto

```bash
 python carstats
```

![regression](https://github.com/jaisenc/carstats/blob/master/docs/regression.png)
![scatter_age](https://github.com/jaisenc/carstats/blob/master/docs/cars_mercedes-benz_e-class_age_vs_km.png)
![scatter_km](https://github.com/jaisenc/carstats/blob/master/docs/cars_mercedes-benz_e-class_age_vs_price.png)
![boxplot_age](https://github.com/jaisenc/carstats/blob/master/docs/cars_mercedes-benz_e-class_boxplot_age.png)

## Quick Start

First get the url for your search on [AutoTrader](http://www.autotrader.ca/). For example, the following search is for all Audi A4 postings around Toronto.

http://www.autotrader.ca/cars/audi/a4/on/toronto/?prx=100&prv=Ontario&loc=m5j2j2&sts=New-Used&hprc=True&wcp=True&inMarket=basicSearch

![url](https://github.com/jaisenc/carstats/blob/master/docs/autotrader_link.png)

```python
from carstats import CarStats
audi_a4 = CarStats(
    'http://www.autotrader.ca/cars/audi/a4/on/toronto/?prx=100&prv=Ontario&loc=m5j2j2&sts=New-Used&hprc=True&wcp=True&inMarket=basicSearch')
audi_a4.html_report(show=True)
```

To predict a 4 year old, 60,0000km Audi A4's value
```python
audi_a4.predict(4,60000)
```


## Dependencies
-   pandas
-   statsmodel
-   matplotlib
-   titlecase



