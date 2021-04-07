import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import GrandsavingsbankItem
from itemloaders.processors import TakeFirst


class GrandsavingsbankSpider(scrapy.Spider):
	name = 'grandsavingsbank'
	start_urls = ['https://grandsavingsbank.com/wp-admin/admin-ajax.php?id=&post_id=0&slug=home&canonical_url=https%3A%2F%2Fgrandsavingsbank.com%2Fblog%2F&posts_per_page=999999&page=0&offset=0&post_type=post&repeater=default&seo_start_page=1&preloaded=false&preloaded_amount=0&order=DESC&orderby=date&action=alm_get_posts&query_type=standard']

	def parse(self, response):
		data = json.loads(response.text)
		raw_data = scrapy.Selector(text=data['html'])

		post_links = raw_data.xpath('//a[@class="permalink"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="post-content"]//text()[normalize-space() and not(ancestor::h1 | ancestor::div[@class="post-details"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//p[@class="post-date"]/text()').get()

		item = ItemLoader(item=GrandsavingsbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
