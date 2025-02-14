import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class Horse(scrapy.Item):
    dam = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor=TakeFirst()
    )
    horse_info = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor=TakeFirst()
    )
    offspring = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    starts = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    registrations = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    result_summaries = scrapy.Field(
        input_processor=MapCompose(dict)
    )
    sire = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor = TakeFirst()
    )
