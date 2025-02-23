import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import Registration
from .processor_functions import handle_basic, shorten_horse_link


class CanadianRegistration(Registration):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_horse_link),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_basic, str.upper),
        output_processor=TakeFirst()
    )
