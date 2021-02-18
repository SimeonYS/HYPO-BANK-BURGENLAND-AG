import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import BurgenItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.bank-bgld.at/de/bank-burgenland/presse/presseaussendungen']

    def parse(self, response):
        links = response.xpath('//p[@class="more"]/a[@class="nu"]/@href').getall()

        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="nächste Seite"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(BurgenItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="mt0"]//text()').get()
        content = response.xpath('//div[@class="notop"]//text()').getall()
        content = re.sub(pattern, "", ' '.join(content))


        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()