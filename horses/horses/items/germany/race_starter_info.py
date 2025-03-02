import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    convert_to_int,
    handle_distance,
    handle_finish,
    handle_purse,
    handle_startnumber,
    is_disqualified,
)


class GermanRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_disqualified), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        # input_processor=MapCompose(did_finish),
        output_processor=TakeFirst()
    )
    postposition = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_purse), output_processor=TakeFirst()
    )
    started = scrapy.Field(output_processor=TakeFirst())
    startnumber = scrapy.Field(
        input_processor=MapCompose(handle_startnumber), output_processor=TakeFirst()
    )
