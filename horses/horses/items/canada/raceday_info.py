import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayInfo
from .processor_functions import extract_racetrack_name, extract_raceday_date


class CanadianRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(extract_raceday_date),
        output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(extract_racetrack_name),
        output_processor=TakeFirst()
    )
