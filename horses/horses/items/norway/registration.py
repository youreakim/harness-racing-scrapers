import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import Registration
from .processor_functions import handle_horse_name, shorten_horse_link


class NorwegianRegistration(Registration):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_horse_link),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_horse_name),
        output_processor=TakeFirst()
    )
