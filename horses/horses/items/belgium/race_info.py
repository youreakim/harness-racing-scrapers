import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

from horses.items.base import RaceInfo
from .processor_functions import handle_basic, handle_distance, handle_racetype, handle_racepurse, handle_startmethod,\
    is_monte, remove_time, handle_racenumber


class BelgianRaceInfo(RaceInfo):
    conditions = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=Join('\n')
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance),
        output_processor=TakeFirst()
    )
    gait = scrapy.Field(
        output_processor=TakeFirst()
    )
    monte = scrapy.Field(
        input_processor=MapCompose(is_monte),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_racepurse),
        output_processor=TakeFirst()
    )
    race_class = scrapy.Field(
        output_processor=TakeFirst()
    )
    racename = scrapy.Field(
        input_processor=MapCompose(remove_time),
        output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(handle_racenumber),
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
    status = scrapy.Field(
        output_processor=TakeFirst()
    )
    track_condition = scrapy.Field(
        output_processor=TakeFirst()
    )
