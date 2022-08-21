from time import sleep
import scrapy
import json
from .. items import FoodyItem

class FoodySpider(scrapy.Spider):
    name = "foody"
    suffix_url = "https://www.foody.vn"

    allowed_domains = ["foody.vn"]

    start_urls = ["https://www.foody.vn/ho-chi-minh/quan-an?CategoryGroup=food&c=quan-an"]

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.foody.vn/ho-chi-minh/quan-an?CategoryGroup=food&c=quan-an",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54",
        "X-Requested-With": "XMLHttpRequest"
    }

    def parse(self, response):
        response_content = scrapy.Selector(response)
        item = FoodyItem()

        base_url = 'https://www.foody.vn/ho-chi-minh/quan-an?ds=Restaurant&vt=row&st=1&c=3&page={0}&provinceId=217&categoryId=3&append=true'

        for i in range(1,5):
            request = scrapy.Request(base_url.format(str(i)), callback= self.parseShowMore, headers= self.headers)
            sleep(0.25)
            yield request

    def parseData1(self, data):
        item = FoodyItem()

        item['name'] = data['Name']

        # general
        item['avgRating'] = data['AvgRatingOriginal']
        item['hasBooking'] = data['HasBooking']
        item['hasDelivery'] = data['HasDelivery']

        # contact
        item['address'] = data['Address']
        item['district'] = data['District']
        item['city'] = data['City']
        item['phone'] = data['Phone']

        # metrics
        item['totalReview'] = data['TotalReview']
        item['totalView'] = data['TotalView']
        item['totalFavourite'] = data['TotalFavourite']
        item['totalCheckins'] = data['TotalCheckins']

        # for backend
        item['categories'] = data['Categories']
        item['reviewUrl'] = data['ReviewUrl']
        item['albumUrl'] = data['AlbumUrl']

        return item

    def parseShowMore(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        
        for d in data['searchItems']:
            # CRAWL
            scrapyItem = self.parseData1(d)
            request = scrapy.Request(url = self.suffix_url + d['DetailUrl'], callback= self.parseDetail, headers= self.headers, meta={'item': scrapyItem})
            yield request

            if d['SubItems']:
                for s in d['SubItems']:
                    # CRAWL
                    scrapyItem = self.parseData1(s)
                    request = scrapy.Request(url = self.suffix_url + s['DetailUrl'], callback= self.parseDetail, headers= self.headers, meta={'item': scrapyItem})
                    yield request

    def parseDetail(self, response):
        response_content = scrapy.Selector(response)
        item = item = response.meta.get('item')

        # Open time
        item['open_time'] = response_content.xpath("//div[@class='micro-timesopen']/span[3]/text()").extract_first().strip()

        # Price range
        temp = response_content.xpath("//span[@itemprop='priceRange']//span/text()").extract()
        price_range = ''
        item['price_range'] = price_range.join(temp)

        # ratings
        citerias = response_content.xpath("//div[@class='microsite-top-points']/div[@class='label']/text()").extract()
        points = response_content.xpath("//div[@class='microsite-top-points']/div[1]/span/text()").extract()

        ratings = {}
        for i in range(len(citerias)):
            ratings[citerias[i]] = float(points[i]) 
        item['detailRating'] = ratings

        yield scrapy.Request(url = self.suffix_url + item['reviewUrl'], callback=self.parse_review, meta={'arg': item})
    

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

        # Photos
        yield scrapy.Request(url = self.suffix_url + item['albumUrl'], callback=self.parse_photo, meta={'arg': item})
    

    def parse_photo(self, response):
        response_content = scrapy.Selector(response)
        item = response.meta.get('arg')
        item['photos'] = response_content.xpath("//div[@class='micro-home-album-img']/div[1]/a/@href").extract()
        yield item