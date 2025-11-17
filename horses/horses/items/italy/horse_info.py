import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_horse_name, handle_horse_country, handle_horse_birthdate, handle_gender


class ItalianHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_horse_birthdate),
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
        input_processor=MapCompose(handle_horse_name),
        output_processor=TakeFirst()
    )
