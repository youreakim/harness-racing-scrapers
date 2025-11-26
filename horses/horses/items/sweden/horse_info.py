import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_name, handle_gender, handle_country, handle_birthdate, handle_breed, filter_breeder


class SwedishHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_birthdate),
        output_processor=TakeFirst()
    )
    breed = scrapy.Field(
        input_processor=MapCompose(handle_breed),
        output_processor=TakeFirst()
    )
    breeder = scrapy.Field(
        input_processor=MapCompose(filter_breeder),
        output_processor=TakeFirst()
    )
    country = scrapy.Field(
        input_processor=MapCompose(handle_country),
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
