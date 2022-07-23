from matplotlib import image
import scrapy
import json
from .. items import FoodyItem

# class FoodySpider(CrawlSpider):
#     name = "foody"
#     allowed_domains = ["foody.vn"]

#     start_urls = ["https://www.foody.vn/ho-chi-minh/2-beo-banh-sau-rieng-shop-online"]

#     def parse(self, response):
#         foody_item = FoodyItem()
#         data_resp = scrapy.Selector(response)

#         foody_item['name'] = data_resp.xpath("div[@class='main-info-title']").extract_first()
#         yield foody_item


class FoodySpider(scrapy.Spider):
    name = "foody"
    # allowed_domains = ["foody.vn", "gappapi.deliverynow.vn"]

    start_urls = ["https://www.foody.vn/ho-chi-minh/oc-co-lan","https://www.foody.vn/ho-chi-minh/nha-hang-viet-pho-le-quy-don","https://www.foody.vn/ho-chi-minh/sapinkie-an-vat-4-teen","https://www.foody.vn/ho-chi-minh/banh-canh-cua-nguyen-cong-tru"]

    headers = {"Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"}


    def parse(self, response):
        response_content = scrapy.Selector(response)

        item = FoodyItem()

        # General
        item['name'] = response_content.xpath("//div[@class='main-info-title']/h1/text()").extract_first()
        item['shop_type'] = response_content.xpath("//div[@class='category-items']/a/text()").extract_first()
        item['category'] = response_content.xpath("//div[@class='category-cuisines']/div[2]/a/text()").extract_first().strip()
        item['open_time'] = response_content.xpath("//div[@class='micro-timesopen']/span[3]/text()").extract_first().strip()
        temp = response_content.xpath("//span[@itemprop='priceRange']//span/text()").extract()

        price_range = ''
        item['price_range'] = price_range.join(temp)

        # # Crawl dynamic data
        # deliveryMenuUrl = "https://www.foody.vn/__get/Notification/GetSummaryNew"
        # url = "https://directory.ntschools.net/api/System/GetAllSchools"
        # yield scrapy.Request(url=url, callback=self.parse_api, headers=self.headers)
        # # item['menu'] = response_content.xpath("//a[@class='title-name-food']/div/text()").extract()
        # # item['comments'] = response_content.xpath("//div[@class='lists list-reviews']/div/ul").extract()

        # Gallery
        # galleryUrl = "%s/album-anh" % response.url

        # Reviews
        reviewUrl = "%s/binh-luan" % response.url
        yield scrapy.Request(url=reviewUrl, callback=self.parse_review, meta={'arg': item})
    

    def parse_gallery(self, response):
        response_content = scrapy.Selector(response)
        item = response.meta.get('arg')

        item['images'] = response_content.xpath("//div[@id='microGallery']//div/div//a/@href").extract()
        yield item
    

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
            item['reviews'].append({"user": userUrls[i], "createdAt": createdAts[i],"platform": platforms[i].strip(), "rating": ratings[i], "title": titles[i], "content": contents[i]})

        suffix = "/binh-luan"

        galleryUrl = response.url.removesuffix(suffix) + "/album-anh"
        
        yield scrapy.Request(url=galleryUrl, callback=self.parse_gallery, meta={'arg': item})
    

    def parse_gallery(self, response):
        response_content = scrapy.Selector(response)
        item = response.meta.get('arg')
        item['photos'] = response_content.xpath("//div[@class='micro-home-album-img']/div[1]/a/@href").extract()
        yield item

         
    
    # def parse_api(self, response):
    #     #item = FoodyItem()

    #     #data = json.loads(response.body)
    #     #print(data)
    #     # menu = []

    #     # for dish in dishes:
    #     #     temp ={}
    #     #     temp['name'] = dish['name']
    #     #     temp['price'] = dish['price']['value']
    #     #     temp['photos'] = []

    #     #     photos = dish['photos']
    #     #     for p in photos:
    #     #         temp.append(p['value'])

    #     #     menu.append(temp)

    #     # item['menu'] = dishes    

    #     data = json.loads(response.body)
    #     yield {
    #         'name': data[2]['schoolName']
    #     }
    
