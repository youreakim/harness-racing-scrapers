import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    convert_to_int,
    did_finish,
    did_gallop,
    did_start,
    handle_starter_distance,
    handle_starter_finish,
    handle_starter_purse,
    is_starter_disqualified,
    remove_license,
)


class NorwegianRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_starter_disqualified),
        output_processor=TakeFirst(),
    )
    distance = scrapy.Field(
        input_processor=MapCompose(handle_starter_distance),
        output_processor=TakeFirst(),
    )
    driver = scrapy.Field(
        input_processor=MapCompose(remove_license), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_starter_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        input_processor=MapCompose(did_finish), output_processor=TakeFirst()
    )
    gallop = scrapy.Field(
        input_processor=MapCompose(did_gallop), output_processor=TakeFirst()
    )
    postposition = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(handle_starter_purse), output_processor=TakeFirst()
    )
    started = scrapy.Field(
        input_processor=MapCompose(did_start), output_processor=TakeFirst()
    )
    trainer = scrapy.Field(
        input_processor=MapCompose(remove_license), output_processor=TakeFirst()
    )
