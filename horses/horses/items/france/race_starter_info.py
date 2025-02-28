import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    did_start,
    handle_starter_distance,
    handle_starter_finish,
    handle_starter_purse,
    handle_startnumber,
    is_starter_disqualified,
)


class FrenchRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_starter_disqualified),
        output_processor=TakeFirst(),
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_starter_distance),
        output_processor=TakeFirst(),
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_starter_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        # input_processor=MapCompose(did_finish),
        output_processor=TakeFirst()
    )
    gallop = scrapy.Field(
        # input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_starter_purse), output_processor=TakeFirst()
    )
    started = scrapy.Field(
        input_processor=MapCompose(did_start), output_processor=TakeFirst()
    )
    startnumber = scrapy.Field(
        input_processor=MapCompose(handle_startnumber), output_processor=TakeFirst()
    )
