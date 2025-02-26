import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_name, is_disqualified


class FinnishRaceStarterInfo(RaceStarterInfo):
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_disqualified), output_processor=TakeFirst()
    )
    driver = scrapy.Field(
        input_processor=MapCompose(handle_name), output_processor=TakeFirst()
    )
    gallop = scrapy.Field(output_processor=TakeFirst())
    trainer = scrapy.Field(
        input_processor=MapCompose(handle_name), output_processor=TakeFirst()
    )
    started = scrapy.Field(output_processor=TakeFirst())
