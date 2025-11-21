import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayInfo
from .processor_functions import extract_racetrack_name, handle_raceday_date


class NorwegianRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_raceday_date),
        output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(extract_racetrack_name),
        output_processor=TakeFirst()
    )
