import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

from horses.items.base import RaceInfo
from .processor_functions import handle_distance, handle_racetype, handle_startmethod, calculate_purse, is_monte


class DanishRaceInfo(RaceInfo):
    conditions = scrapy.Field(
        output_processor=Join('\n')
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance),
        output_processor=TakeFirst()
    )
    monte = scrapy.Field(
        input_processor=MapCompose(is_monte),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(calculate_purse),
        output_processor=TakeFirst()
    )
    racename = scrapy.Field(
        output_processor=Join(' ')
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(handle_racetype),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(handle_startmethod),
        output_processor=TakeFirst()
    )
