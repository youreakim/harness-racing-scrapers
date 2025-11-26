import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    did_finish,
    did_gallop,
    get_distance,
    handle_finish,
    handle_postposition,
    is_approved,
    is_disqualified,
    remove_licence,
)


class SwedishRaceStarterInfo(RaceStarterInfo):
    approved = scrapy.Field(
        input_processor=MapCompose(is_approved), output_processor=TakeFirst()
    )
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_disqualified), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(get_distance), output_processor=TakeFirst()
    )
    driver = scrapy.Field(
        input_processor=MapCompose(remove_licence), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        input_processor=MapCompose(did_finish), output_processor=TakeFirst()
    )
    gallop = scrapy.Field(
        input_processor=MapCompose(did_gallop), output_processor=TakeFirst()
    )
    postposition = scrapy.Field(
        input_processor=MapCompose(handle_postposition), output_processor=TakeFirst()
    )
    started = scrapy.Field(output_processor=TakeFirst())
    trainer = scrapy.Field(
        input_processor=MapCompose(remove_licence), output_processor=TakeFirst()
    )
