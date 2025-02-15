import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import Registration
from .processor_functions import handle_horselink, handle_registration, handle_name


class BelgianRegistration(Registration):
    link = scrapy.Field(
        input_processor=MapCompose(handle_horselink),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_name),
        output_processor=TakeFirst()
    )
    registration = scrapy.Field(
        input_processor=MapCompose(handle_registration),
        output_processor=TakeFirst()
    )
