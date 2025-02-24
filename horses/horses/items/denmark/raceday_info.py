import scrapy
from itemloaders.processors import TakeFirst

from horses.items.base import RacedayInfo


class DanishRacedayInfo(RacedayInfo):
    collection_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    country = scrapy.Field(
        output_processor=TakeFirst()
    )
    date = scrapy.Field(
        output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        output_processor=TakeFirst()
    )
    racetrack_code = scrapy.Field(
        output_processor=TakeFirst()
    )
    region = scrapy.Field(
        output_processor=TakeFirst()
    )
    status = scrapy.Field(
        output_processor=TakeFirst()
    )
    type = scrapy.Field(
        output_processor=TakeFirst()
    )
