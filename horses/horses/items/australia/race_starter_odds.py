import scrapy
from horses.items.base import RaceStarterOdds
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_win_odds


class AustralianRaceStarterOdds(RaceStarterOdds):
    odds = scrapy.Field(
        input_processor=MapCompose(handle_win_odds), output_processor=TakeFirst()
    )
