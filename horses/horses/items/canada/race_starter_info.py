import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_finish, handle_person_name, handle_starter_purse


class CanadianRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(output_processor=TakeFirst())
    driver = scrapy.Field(
        input_processor=MapCompose(handle_person_name), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(handle_finish), output_processor=TakeFirst()
    )
    finished = scrapy.Field(output_processor=TakeFirst())
    gallop = scrapy.Field(output_processor=TakeFirst())
    order = scrapy.Field(output_processor=TakeFirst())
    purse = scrapy.Field(
        input_processor=MapCompose(handle_starter_purse), output_processor=TakeFirst()
    )
    started = scrapy.Field(
        # input_processor = MapCompose(remove_tags, did_start),
        output_processor=TakeFirst()
    )
    trainer = scrapy.Field(
        input_processor=MapCompose(handle_person_name), output_processor=TakeFirst()
    )
