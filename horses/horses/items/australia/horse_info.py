import scrapy
from horses.items.base import HorseInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    handle_basic,
    handle_breed,
    handle_breeder,
    handle_gender,
    handle_horse_birthdate,
    handle_horse_country,
    handle_horse_name,
)


class AustralianHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_horse_birthdate), output_processor=TakeFirst()
    )
    breed = scrapy.Field(
        input_processor=MapCompose(handle_breed), output_processor=TakeFirst()
    )
    breeder = scrapy.Field(
        input_processor=MapCompose(handle_breeder), output_processor=TakeFirst()
    )
    country = scrapy.Field(
        input_processor=MapCompose(handle_horse_country), output_processor=TakeFirst()
    )
    gender = scrapy.Field(
        input_processor=MapCompose(handle_basic, handle_gender),
        output_processor=TakeFirst(),
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_horse_name), output_processor=TakeFirst()
    )
