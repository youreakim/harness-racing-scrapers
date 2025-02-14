import scrapy
from horses.items.base import RaceInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    get_distance,
    get_gait,
    get_race_purse,
    get_race_type,
    get_racenumber,
    get_startmethod,
)


class AustralianRaceInfo(RaceInfo):
    distance = scrapy.Field(
        input_processor=MapCompose(get_distance), output_processor=TakeFirst()
    )
    gait = scrapy.Field(
        input_processor=MapCompose(get_gait), output_processor=TakeFirst()
    )
    monte = scrapy.Field(output_processor=TakeFirst())
    purse = scrapy.Field(
        input_processor=MapCompose(get_race_purse), output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(get_racenumber), output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(get_race_type), output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(get_startmethod), output_processor=TakeFirst()
    )
