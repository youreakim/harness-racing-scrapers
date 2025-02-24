import scrapy
from horses.items.base import Registration
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_name


class DanishRegistration(Registration):
    link = scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    name = scrapy.Field(
        input_processor=MapCompose(handle_name, str.strip, str.upper),
        output_processor=TakeFirst(),
    )
