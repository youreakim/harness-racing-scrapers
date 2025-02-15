import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_birthdate, handle_name, handle_gender


class BelgianHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_birthdate),
        output_processor=TakeFirst()
    )
    gender = scrapy.Field(
        input_processor=MapCompose(handle_gender),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_name),
        output_processor=TakeFirst()
    )
