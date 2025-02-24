import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    did_finish,
    handle_distance,
    handle_finish,
    handle_purse,
    is_approved,
    is_disqualified,
    made_a_break,
)


class DanishRaceStarterInfo(RaceStarterInfo):
    approved = scrapy.Field(
        input_processor=MapCompose(is_approved), output_processor=TakeFirst()
    )
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_disqualified), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_distance, int), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        input_processor=MapCompose(did_finish), output_processor=TakeFirst()
    )
    gallop = scrapy.Field(
        input_processor=MapCompose(made_a_break), output_processor=TakeFirst()
    )
    postposition = scrapy.Field(
        input_processor=MapCompose(str), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_purse, int), output_processor=TakeFirst()
    )
    started = scrapy.Field(output_processor=TakeFirst())
