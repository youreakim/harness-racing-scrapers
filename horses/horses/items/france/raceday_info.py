import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayInfo
from .processor_functions import raceday_date_from_link, racetrack_code_from_link


class FrenchRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(raceday_date_from_link),
        output_processor=TakeFirst()
    )
    racetrack_code = scrapy.Field(
        input_processor=MapCompose(racetrack_code_from_link),
        output_processor=TakeFirst()
    )
