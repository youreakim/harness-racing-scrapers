import scrapy
from horses.items.base import Registration
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_horse_link, handle_name


class SpanishRegistration(Registration):
    link = scrapy.Field(
        input_processor=MapCompose(str, handle_horse_link), output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_name), output_processor=TakeFirst()
    )
