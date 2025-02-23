import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_basic, handle_horse_country, handle_horse_birthdate, handle_gender,\
    handle_breed, handle_chip


class CanadianHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_horse_birthdate),
        output_processor=TakeFirst()
    )
    breed = scrapy.Field(
        input_processor=MapCompose(handle_breed),
        output_processor=TakeFirst()
    )
    chip = scrapy.Field(
        input_processor=MapCompose(handle_chip),
        output_processor=TakeFirst()
    )
    country = scrapy.Field(
        input_processor=MapCompose(handle_horse_country),
        output_processor=TakeFirst()
    )
    gender = scrapy.Field(
        input_processor=MapCompose(handle_gender),
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        input_processor=MapCompose(handle_basic, str.upper),
        output_processor=TakeFirst()
    )
