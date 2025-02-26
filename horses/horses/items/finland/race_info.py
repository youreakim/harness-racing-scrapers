import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceInfo
from .processor_functions import handle_startmethod, handle_racetype


class FinnishRaceInfo(RaceInfo):
    monte = scrapy.Field(
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(handle_racetype),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(handle_startmethod),
        output_processor=TakeFirst()
    )
