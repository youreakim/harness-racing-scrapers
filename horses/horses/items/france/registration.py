import scrapy
from horses.items.base import Registration
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    handle_basic,
    handle_horse_name,
    handle_source,
    shorten_horse_link,
)


class FrenchRegistration(Registration):
    link = scrapy.Field(
        input_processor=MapCompose(handle_basic, shorten_horse_link),
        output_processor=TakeFirst(),
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_horse_name), output_processor=TakeFirst()
    )
    source = scrapy.Field(
        input_processor=MapCompose(handle_source), output_processor=TakeFirst()
    )
