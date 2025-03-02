import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

from horses.items.base import RaceInfo
from .processor_functions import handle_distance, get_racenumber, get_racetype, handle_racepurse, get_startmethod, remove_non_breaking_space


class GermanRaceInfo(RaceInfo):
    conditions = scrapy.Field(
        input_processor=MapCompose(remove_non_breaking_space),
        output_processor=Join('\n')
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_racepurse),
        output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(get_racenumber),
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(get_racetype),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(get_startmethod),
        output_processor=TakeFirst()
    )
