import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import Registration
from .processor_functions import handle_name


class FinnishRegistration(Registration):
    name = scrapy.Field(
        input_processor=MapCompose(handle_name),
        output_processor=TakeFirst()
    )
