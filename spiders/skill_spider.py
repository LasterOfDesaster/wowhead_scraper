import scrapy
from scrapy import signals
from scrapy.shell import inspect_response

from utils import Merger
from utils.formatter import Formatter

import json


class SkillSpider(scrapy.Spider):
    name = "skill_scraper"
    start_urls = []
    gem_data = []
    lang = ""
    base_url = "https://www.wowhead.com/wotlk/{}/spells/abilities/{}?filter=16;3;0"
    item_quality = {

    }   
    classes = [
        "rogue",
        "warrior",
        "mage",
        "druid",
        "warlock",
        "hunter",
        "shaman",
        "paladin",
        "priest",
        "death-knight"
    ]

    def __init__(self, lang="en", **kwargs):
        super().__init__(**kwargs)
        self.lang = lang
        self.start_urls = [self.base_url.format(lang, cid) for cid in self.classes]
        #self.start_urls = [self.base_url.format(lang, cid) for cid in ["rogue", "druid", ] ]      

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SkillSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        if "?notFound=" in response.url:
            qid = response.url[response.url.index("?notFound=") + 10:]
            self.logger.warning("Quest with ID '{}' could not be found.".format(qid))
            return
        className:str = response.url.split("/")[-1].split("?")[0]
        title = self.__parse_title(response)
        text = self.__parse_html(response)

        result = {
            "class": className,
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
        xpath: str = '//body/div[3]/div[1]/div[1]/div[2]/div[3]/script[contains(text(),\'WH.Gatherer.addData(6, 8, {auf}\')]/text()'.format(auf="{")

        js: str = response.xpath(xpath).get()
        js = js.replace("\n", "")
        js = js.replace("//<![CDATA[", "").replace("//]]", "")
        js = js.replace("var lv_comments3 = [];", "")
        js_lines = js.split(";")
        js = ""

        for js_line in js_lines:
            if "WH.Gatherer.addData(6, 8," in js_line:
                js = js_line
                break
        json_text = js[26:len(js)-1]

        result: str = ""
        try:
            json_object = json.loads(json_text)

            for spellID, data in json_object.items():
                result = result + spellID + ";"
        except:
            result = "fail"

        return result


    def spider_closed(self, spider):
        self.logger.info("Spider closed. Starting formatter...")

        f = Formatter()
        #f(self.lang, "cons")

        #self.logger.info("Formatting done!")
        #m = Merger(self.lang)
        #m()
        #self.logger.info("Merging done. New lookup file at '{}'".format(m.lang_dir))

        return
