import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

from horses.items.base import RaceInfo
from .processor_functions import get_distance, handle_racetype, handle_startmethod, is_monte, handle_race_purse


class SwedishRaceInfo(RaceInfo):
    conditions = scrapy.Field(
        output_processor=Join(separator='\n')
    )
    distance = scrapy.Field(
        input_processor=MapCompose(get_distance),
        output_processor=TakeFirst()
    )
    monte = scrapy.Field(
        input_processor=MapCompose(is_monte),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_race_purse),
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(handle_racetype),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(handle_startmethod),
        output_processor=TakeFirst()
    )
