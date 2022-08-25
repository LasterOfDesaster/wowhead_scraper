import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

# this list of consumes ids is exported from wow.tools -> view table -> items -> export csv -> filter for classID == 0 (consumes)
# classID 0 is for all consumes, subClassId differentiates between Pots, Flask, Food&Drink, Xplosives, ...
# List of all consumes is ~2k+ so I filtered for SubClassID 0-7 separatly and made an export for each and then running a Formatter
# + renaming output_consumes.csv to output_cons_X_DESC.csv (X = SubClassID, DESC = short description). 
#from ids import CONS_IDS
from utils import Merger
from utils.formatter import Formatter

import json


class ConsumesSpider(scrapy.Spider):
    name = "cons_scraper"
    start_urls = []
    gem_data = []
    lang = ""
    base_url = "https://www.wowhead.com/wotlk/item={}/"
    item_quality = {

    }  
    # CONS_IDS is normally from \ids\cons_ids.py but some consumes made problems when parsing HTML so the following list is just the 
    # previous not working subset of the consumes list
    CONS_IDS = [
        6657, 
        7676, 
        27657, 
        27658, 
        27659, 
        27660, 
        27662, 
        27663, 
        27664, 
        27665, 
        27666, 
        27667, 
        27854, 
        28501, 
        29292, 
        29293, 
        30357, 
        30358, 
        30359, 
        30361, 
        31672, 
        31673, 
        32721, 
        33052, 
        33825, 
        33866, 
        33867, 
        33872, 
        33874, 
        34411, 
        34748, 
        34749, 
        34750, 
        34751, 
        34752, 
        34754, 
        34755, 
        34756, 
        34757, 
        34758, 
        34762, 
        34763, 
        34764, 
        34765, 
        34766, 
        34767, 
        34768, 
        34769, 
        38466, 
        39691, 
        42779, 
        42942, 
        42993, 
        42994, 
        42995, 
        42996, 
        42998, 
        42999, 
        43000, 
        43001, 
        43015, 
        43268, 
        43478, 
        43480, 
        44791, 
        44953, 
        45279, 
        46691, 
        46887, 
    ] 

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(cid) for cid in self.CONS_IDS]
        #self.start_urls = [self.base_url.format(lang, cid) for cid in [4536, 12212, 13893, 27651, 29112, 32455,  ] ]      

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ConsumesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        gemid = response.url.split("/")[-2][5:]
        title = self.__parse_title(response)
        text = self.__parse_html(response)

        result = {
            "id": int(gemid),
            "title": title,
            "text" : text
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

    def __parse_html(self, response) -> str:

        itemid:str = response.url.split("/")[-2][5:]
        xpath: str = '//body/div[3]/div[1]/div[1]/div[2]/div[3]/script[contains(text(),\'WH.Gatherer.addData(3, 8, {auf}\"{item_id}\":\')]/text()'.format(item_id=itemid, auf="{")

        # extract <script> tag from raw HTML
        js: str = response.xpath(xpath).get()
        # replace junk with empty-string
        js = js.replace("\n", "")
        js = js.replace("//<![CDATA[", "")
        js = js.replace("var lv_comments3 = [];", "")
        # since <script> tag can contain multiple occurences of valid js split them by the delimiter ';'
        js_lines = js.split(";")

        # sometimes the <script> tag can contain multiple lines of JS, to find the line for further processing loop over the
        # each line and check if it contains 'WH.Gatherer.addData(3, 8,'        
        js = ""
        for js_line in js_lines:
            if "WH.Gatherer.addData(3, 8," in js_line:
                js = js_line
                break
        json_text = js[26:len(js)-1]

	    # try converting the parameter 3 from string to json
	    # in case anything fails return "fail values" but don't brick the programm
        try:
            json_object = json.loads(json_text)

            # check  if itemid is contained in json_object, if not then use fallback value
            if itemid not in json_object:
                result = "fail"
            else:
                result = json_object[itemid]
        except:
            result = "fail"

        return result


    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter...")

        # since webscraping hundreds of data each time the processes are mostly manually done
        # therefore the Formatter is called by hand and not executed in sequence after the Spider is done
        f = Formatter()
        #f(self.lang, "cons")

        #self.logger.info("Formatting done!")
        #m = Merger(self.lang)
        #m()
        #self.logger.info("Merging done. New lookup file at '{}'".format(m.lang_dir))

        return
