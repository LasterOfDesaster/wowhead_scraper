import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from ids import GEM_IDS
from utils import Merger
from utils.formatter import Formatter

import json


class GemSpider(scrapy.Spider):
    name = "gem_scraper"
    start_urls = []
    gem_data = []
    lang = ""
    base_url = "https://www.wowhead.com/wotlk/{}/item={}/"
    item_quality = {
        "0" : "poor",
        "1" : "common",
        "2" : "uncommon",
        "3" : "rare",
        "4" : "epic",
        "5" : "legendary",
        "6" : "artifact",
        "7" : "heirloom",
    }
    gem_color = {
		# perfect cut
		"inv_jewelcrafting_gem_13" : "green",
		"inv_jewelcrafting_gem_14" : "orange",
		"inv_jewelcrafting_gem_15" : "yellow",
		"inv_jewelcrafting_gem_16" : "red",
		"inv_jewelcrafting_gem_17" : "blue",
		"inv_jewelcrafting_gem_18" : "purple",
		
		#green
		"inv_jewelcrafting_gem_19" : "green",
		"inv_jewelcrafting_gem_20" : "orange",
		"inv_jewelcrafting_gem_21" : "yellow",
		"inv_jewelcrafting_gem_22" : "red",
		"inv_jewelcrafting_gem_23" : "purple",
		"inv_jewelcrafting_gem_24" : "blue",
		
		#blue
        "inv_jewelcrafting_gem_25" : "green",
        "inv_jewelcrafting_gem_26" : "yellow",
        "inv_jewelcrafting_gem_27" : "blue",
        "inv_jewelcrafting_gem_28" : "red",
        "inv_jewelcrafting_gem_29" : "purple",
        "inv_jewelcrafting_gem_30" : "orange",
		
		#epic
        "inv_jewelcrafting_gem_37" : "red",
        "inv_jewelcrafting_gem_38" : "yellow",
        "inv_jewelcrafting_gem_39" : "orange",
        "inv_jewelcrafting_gem_40" : "purple",
        "inv_jewelcrafting_gem_41" : "green",
        "inv_jewelcrafting_gem_42" : "blue",

        #dragons eye
        "inv_jewelcrafting_dragonseye03" : "yellow",
        "inv_jewelcrafting_dragonseye04" : "blue",
        "inv_jewelcrafting_dragonseye05" : "red",
    }

    

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(lang, gemid) for gemid in GEM_IDS]
        #self.start_urls = [self.base_url.format(lang, gemid) for gemid in [40111, 36919, 36934, 36925 ]]        

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GemSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        gemid = response.url.split("/")[-2][5:]
        title = self.__parse_title(response)
        color, quality = self.__parse_symbol(response)

        result = {
            "id": int(gemid),
            "title": title,
            "color" : color,
            "quality": quality
        }
        self.logger.info(result)

        yield result

    def __parse_title(self, response) -> str:
        title: str = response.xpath("//div[@class='text']/h1[@class='heading-size-1']/text()").get()

        title = self.__filter_title(title)
        return title

    @staticmethod
    def __filter_title(title: str) -> str:
        if title.startswith("[DEPRECATED]"):
            title = title[13:]
        elif title.startswith("["):
            return ""
        return title.strip()

    def __parse_symbol(self, response) -> str:

        gemid:str = response.url.split("/")[-2][5:]
        xpath: str = '//body/div[3]/div[1]/div[1]/div[2]/div[3]/script[contains(text(),\'WH.Gatherer.addData(3, 8, {auf}\"{gem_id}\":\')]/text()'.format(gem_id=gemid, auf="{")

	# extract <script> tag from the raw HTML
        js: str = response.xpath(xpath).get()
	# replace \n with empty-string
        js = js.replace("\n", "")
	# replace junk with empty-string
        js = js.replace("//<![CDATA[", "")
        js = js.replace("var lv_comments3 = [];", "")
	# since <script> tag can contain multiple occurences of valid js split them by the delimiter ';'
        js = js[:js.find(";")]
	# line: WH.Gatherer.addData(X, Y, {});
	# since the line starts with a function call the  line also ends with a closing bracket + a semicolon
        json_text = js[26:len(js)-1]

	# try converting the parameter 3 from string to json
	# in case anything fails return "fail values" but don't brick the programm
        try:
            json_object = json.loads(json_text)

            gem_icon = json_object[gemid]['icon']
            gem_quality = json_object[gemid]['quality']

	    # check if gem_icon is in list of valid icons. so if the current icon is a uncut gem then use the original icon
	    # this way the raw gems can be filterd out later
            if gem_icon in self.gem_color:
                color = self.gem_color[gem_icon][:1]
            else:
                color = gem_icon

            # check if quality is present, if not return original value and not he numeric representation of quality
            if str(gem_quality) in self.item_quality:
                quality = self.item_quality[str(gem_quality)]
            else:
                quality = str(gem_quality)
        except:
            color = "fail"
            quality = "-1"

        return color, quality


    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter...")

        f = Formatter()
        f(self.lang, "gem")

        #self.logger.info("Formatting done!")
        #m = Merger(self.lang)
        #m()
        #self.logger.info("Merging done. New lookup file at '{}'".format(m.lang_dir))

        return
