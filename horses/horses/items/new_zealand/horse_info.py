import scrapy
import html
from horses.items.base import HorseInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    handle_basic,
    handle_breed,
    handle_breeder,
    handle_chip,
    handle_country,
    handle_gender,
    handle_horse_birthdate,
    handle_horse_name,
)


class NZHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_horse_birthdate), output_processor=TakeFirst()
    )
    breed = scrapy.Field(
        input_processor=MapCompose(handle_breed), output_processor=TakeFirst()
    )
    breeder = scrapy.Field(
        input_processor=MapCompose(handle_breeder, html.unescape),
        output_processor=TakeFirst()
    )
    chip = scrapy.Field(
        input_processor=MapCompose(handle_chip), output_processor=TakeFirst()
    )
    country = scrapy.Field(
        input_processor=MapCompose(handle_basic, handle_country),
        output_processor=TakeFirst(),
    )
    gender = scrapy.Field(
        input_processor=MapCompose(handle_basic, handle_gender),
        output_processor=TakeFirst(),
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_horse_name), output_processor=TakeFirst()
    )
