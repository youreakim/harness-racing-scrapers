import scrapy
from w3lib.html import remove_tags
from horses.items.base import HorseInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    handle_birthdate,
    handle_country,
    handle_gender,
    handle_name,
)


class SpanishHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_birthdate), output_processor=TakeFirst()
    )
    country = scrapy.Field(
        input_processor=MapCompose(handle_country), output_processor=TakeFirst()
    )
    gender = scrapy.Field(
        input_processor=MapCompose(handle_gender), output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_name), output_processor=TakeFirst()
    )
    ueln = scrapy.Field(input_processor=MapCompose(remove_tags, str.strip), output_processor=TakeFirst())
