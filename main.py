import datetime
import csv
import argparse
import logging
logging.basicConfig(level=logging.INFO) #método INFO visual en terminal
import re # regular expressions
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

import new_page_objects as news
from common import config

logger = logging.getLogger(__name__) #nombre del módulo
is_well_formed_link = re.compile(r'^https?://.+/.+$') #https://exapmle.com/hello
is_root_path = re.compile(r'^/.+$') # /some-text

def _news_scrapper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    # En el retorno de la funcion config() se construye 'news_site_uid'

    logging.info('Beginning scrapper for {}'.format(host))
    
    #se crea la instancia
    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
       article = _fetch_article(news_site_uid, host, link)

       if article:
           logger.info('Article have been fetched')
           articles.append(article)
           
    
    _save_articles(news_site_uid, articles)

def _save_articles(news_site_uid, articles):
    now = datetime.datetime.now()
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(news_site_uid=news_site_uid, datetime=now.strftime('%Y_%m_%d'))

    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)

def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article ar {}'.format(link))

    article = None
    try:
        article = news.ArticlePage(news_site_uid,_build_link(host, link))
    except (HTTPError, MaxRetryError) as error:
        logging.warning('Error while fetching the article', exc_info=False)


    if article and not article.body:
        logger.warning('Invalid article, there is no body')
        return None

    return article

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)

if __name__ == '__main__':
    parser = argparse.ArgumentParser() # Crea un parser bash
    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site', help='The news site that you want to scrape', type = str, choices=news_site_choices)

    args = parser.parse_args()
    _news_scrapper(args.news_site)