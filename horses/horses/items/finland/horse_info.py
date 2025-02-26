import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import HorseInfo
from .processor_functions import handle_name, handle_breed, handle_gender, handle_birthdate, check_ueln, is_empty


class FinnishHorseInfo(HorseInfo):
    birthdate = scrapy.Field(
        input_processor=MapCompose(handle_birthdate),
        output_processor=TakeFirst()
    )
    breed = scrapy.Field(
        input_processor=MapCompose(handle_breed),
        output_processor=TakeFirst()
    )
    breeder = scrapy.Field(
        input_processor=MapCompose(is_empty),
        output_processor=TakeFirst()
    )
    chip = scrapy.Field(
        input_processor=MapCompose(is_empty),
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
        input_processor=MapCompose(check_ueln),
        output_processor=TakeFirst()
    )
