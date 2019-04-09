import scrapy
import json
import sqlite3
from datetime import date
from scrapy.exceptions import CloseSpider


class LoginSpider(scrapy.Spider):
    name = 'login_spider'
    start_urls = ['http://quotes.toscrape.com/login']

    def parse(self, response):
        self.log('visitei a página de login: {}'.format(response.url))
        token = response.css('input[name="csrf_token"]::attr(value)').extract_first()
        yield scrapy.FormRequest(
            url = 'http://quotes.toscrape.com/login',
            formdata = {
                'username': 'john.doe',
                'password': 'anything',
                'csrf_token': token,
            },
            callback = self.parse_author_links
        )

    def parse_author_links(self, response):
        has_logout_link = response.css('a[href="/logout"]').extract_first()
        if not has_logout_link:
            raise CloseSpider('falha na autenticação')
        self.log('Acabei de fazer login')

        links = response.css('.quote a[href*="goodreads.com"]::attr(href)').extract()
        for link in links:
            yield {'link': link}
 
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse_author_links,
            )