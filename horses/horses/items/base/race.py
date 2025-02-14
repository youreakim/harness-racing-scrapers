import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class Race(scrapy.Item):
    links = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    race_info = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor=TakeFirst()
    )
    race_starters = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    race_times = scrapy.Field(
        input_processor=MapCompose(dict)
    )
