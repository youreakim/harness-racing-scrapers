import scrapy
from horses.items.base import RacedayInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    find_racetrack_code,
    handle_racedate,
    handle_raceday_country,
    handle_racetrack,
)


class GermanRacedayInfo(RacedayInfo):
    country = scrapy.Field(
        input_processor=MapCompose(handle_raceday_country), output_processor=TakeFirst()
    )
    date = scrapy.Field(
        input_processor=MapCompose(handle_racedate), output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(handle_racetrack), output_processor=TakeFirst()
    )
    racetrack_code = scrapy.Field(
        input_processor=MapCompose(find_racetrack_code), output_processor=TakeFirst()
    )
