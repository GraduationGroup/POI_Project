import scrapy
import json
from .. items import FoodyItem

class FoodySpider(scrapy.Spider):
    name = "foody"
    # allowed_domains = ["foody.vn", "gappapi.deliverynow.vn"]

    start_urls = ["https://www.foody.vn/ho-chi-minh/com-tam-minh-long-nguyen-thi-thap","https://www.foody.vn/ho-chi-minh/oc-co-lan","https://www.foody.vn/ho-chi-minh/nha-hang-viet-pho-le-quy-don","https://www.foody.vn/ho-chi-minh/sapinkie-an-vat-4-teen","https://www.foody.vn/ho-chi-minh/banh-canh-cua-nguyen-cong-tru"]


    def parse(self, response):
        response_content = scrapy.Selector(response)

        item = FoodyItem()

        # Name
        item['name'] = response_content.xpath("//div[@class='main-info-title']/h1/text()").extract_first()

        # Shop type
        item['shop_type'] = response_content.xpath("//div[@class='category-items']/a/text()").extract_first()

        # Category
        item['category'] = response_content.xpath("//div[@class='category-cuisines']/div[2]/a/text()").extract_first().strip()

        # Rating
        citerias = response_content.xpath("//div[@class='microsite-top-points']/div[@class='label']/text()").extract()
        points = response_content.xpath("//div[@class='microsite-top-points']/div[1]/span/text()").extract()
        ratings = {}
        for i in range(len(citerias)):
            ratings[citerias[i]] = float(points[i]) 
        item['ratings'] = ratings
        ratings['Avg'] = float(response_content.xpath("//div[@class='microsite-point-avg ']/text()").extract_first().strip())

        # Open time
        item['open_time'] = response_content.xpath("//div[@class='micro-timesopen']/span[3]/text()").extract_first().strip()

        # Price range
        temp = response_content.xpath("//span[@itemprop='priceRange']//span/text()").extract()
        price_range = ''
        item['price_range'] = price_range.join(temp)

        # Reviews
        reviewUrl = "%s/binh-luan" % response.url
        yield scrapy.Request(url=reviewUrl, callback=self.parse_review, meta={'arg': item})


    def parse_review(self, response):
        response_content = scrapy.Selector(response)
        item = response.meta.get('arg')

        item['reviews'] = []
        
        userUrls = response_content.xpath("//div[@class='list-reviews']/div[1]/ul[1]//a[@class='ru-username']/@href").extract()
        createdAts = response_content.xpath("//div[@class='list-reviews']/div[1]/ul[1]//span[@class='ru-time']/text()").extract()
        platforms = response_content.xpath("//div[@class='list-reviews']/div[1]/ul[1]//a[@class='ru-device']/text()").extract() #strip
        titles = response_content.xpath("//div[@class='list-reviews']/div[1]/ul[1]//a[@class='rd-title']//span/text()").extract()
        contents = response_content.xpath("//div[@class='rd-des toggle-height']/span/text()").extract()
        ratings = response_content.xpath("//div[@class='list-reviews']//li/div[2]/div[1]/span/text()").extract()

        temp = response_content.xpath("//div[@class='list-reviews']/div[1]/ul[1]//ul")
        photos = []

        for t in temp:
            photos.append(t.xpath(".//img/@src").extract())

        for i in range(len(userUrls)):
            item['reviews'].append({"user": userUrls[i], "createdAt": createdAts[i],"platform": platforms[i].strip(), "rating": float(ratings[i]), "title": titles[i], "content": contents[i]})

        suffix = "/binh-luan"

        galleryUrl = response.url.removesuffix(suffix) + "/album-anh"
        
        yield scrapy.Request(url=galleryUrl, callback=self.parse_photo, meta={'arg': item})
    

    def parse_photo(self, response):
        response_content = scrapy.Selector(response)
        item = response.meta.get('arg')
        item['photos'] = response_content.xpath("//div[@class='micro-home-album-img']/div[1]/a/@href").extract()
        yield item


