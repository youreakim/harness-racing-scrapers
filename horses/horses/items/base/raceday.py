import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class Raceday(scrapy.Item):
    links = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    raceday_info = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor=TakeFirst()
    )
    races = scrapy.Field(
        input_processor=MapCompose(dict)
    )
