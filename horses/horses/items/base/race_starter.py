import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class RaceStarter(scrapy.Item):
    horse = scrapy.Field(input_processor=MapCompose(dict), output_processor=TakeFirst())
    starter_info = scrapy.Field(
        input_processor=MapCompose(dict), output_processor=TakeFirst()
    )
    odds = scrapy.Field(input_processor=MapCompose(dict))
    positions = scrapy.Field(input_processor=MapCompose(dict))
    times = scrapy.Field(input_processor=MapCompose(dict))
