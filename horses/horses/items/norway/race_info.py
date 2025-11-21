import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RaceInfo
from .processor_functions import shorten_conditions, get_distance, get_race_purse, get_racenumber, get_startmethod, get_racetype, is_monte


class NorwegianRaceInfo(RaceInfo):
    conditions = scrapy.Field(
        input_processor=MapCompose(shorten_conditions),
        output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(get_distance),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(get_race_purse),
        output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(get_racenumber),
        output_processor=TakeFirst()
    )
    monte = scrapy.Field(
        input_processor=MapCompose(is_monte),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(get_startmethod),
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(get_racetype),
        output_processor=TakeFirst()
    )
