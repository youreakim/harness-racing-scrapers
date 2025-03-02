import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_name, handle_country, handle_birthdate, handle_gender, remove_title


class GermanHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_birthdate),
        output_processor=TakeFirst()
    )
    chip = scrapy.Field(
        input_processor=MapCompose(remove_title),
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
    ueln = scrapy.Field(
        input_processor=MapCompose(remove_title),
        output_processor=TakeFirst()
    )
