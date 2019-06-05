# -*- coding: utf-8 -*-
import scrapy
import re
import json
import os
from urllib.parse import urlparse, urlencode, parse_qs
from scrapy import Request
from case1.db import CommentsDb

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = [
        'https://item.jd.com/1384071.html'
    ]
    # Stores downloaded files
    html_dir = 'DownloadedSources'
    # Prefix of comment request
    comment_prefix = 'https://sclub.jd.com/comment/productPageComments.action?'
    # Prefix of comment version indicator
    comment_ver_prefix = 'fetchJSON_comment98vv'
    # Database manager
    comments_db = CommentsDb()

    def __init__(self):
        super(JdSpider, self).__init__()

        if not os.path.exists(self.html_dir):
            os.mkdir(self.html_dir)

        self.comments_db.connect()

    def parse(self, response):
        filename = os.path.join(self.html_dir, os.path.basename(response.url))

        with open(filename, 'wb') as f:
            f.write(response.text.encode('utf-8'))

        # Search for comment version in the pageConfig variable under script tags
        comment_ver = ''

        for scr in response.xpath('//script'):
            match = re.search(r"commentVersion\:\'(\d+)\'", scr.extract())

            if match is not None:
                comment_ver = match.group(1)
                break
        
        params = self.default_params()
        params['callback'] = '{}{}'.format(self.comment_ver_prefix, comment_ver)
        params['productId'] = os.path.basename(filename).split('.')[-2]
        params['page'] = 0

        url_comments = self.comment_prefix + urlencode(params)
        
        request = Request(url_comments, callback=self.parse_comments)

        return [request]

    def parse_comments(self, response):
        url = urlparse(response.url)
        query_params = parse_qs(url.query)

        filename = os.path.join(self.html_dir, 'comments_page_{}.html'.format(query_params['page'][0]))

        with open(filename, 'wb') as f:
            f.write(response.text.encode('utf-8'))

        match = re.search('^{}'.format(self.comment_ver_prefix) + r'\d+\((.+)\)\;$', response.text)
        
        requests = []
        if match is not None:
            j_obj = json.loads(match.group(1))
            max_page = j_obj['maxPage']

            # If there are still comments to be fetched increment page number
            if int(query_params['page'][0]) < max_page - 1:
                params = self.default_params()
                params['callback'] = query_params['callback'][0]
                params['productId'] = query_params['productId'][0]
                params['page'] = int(query_params['page'][0]) + 1

                url_comments = self.comment_prefix + urlencode(params)

                requests.append(Request(url_comments, callback=self.parse_comments))

                self.comments_db.insert(j_obj['comments'])
        elif response.body is None:
            # Comment version has expired, increment version
            match = re.match(self.comment_ver_prefix + r'(\d+)', query_params['callback'][0])

            if match is not None:
                params = self.default_params()
                params['callback'] = '{}{}'.format(self.comment_ver_prefix, match.group(1))
                params['productId'] = query_params['productId'][0]
                params['page'] = query_params['page'][0]

                url_comments = self.comment_prefix + urlencode(params)

                requests.append(Request(url_comments, callback=self.parse_comments))

        return requests

    # Constant query params
    def default_params(self):
        params = {
            'score': 0,
            'sortType': 5,
            'pageSize': 10,
            'isShadowSku': 0,
            'fold': 1
        }

        return params
        