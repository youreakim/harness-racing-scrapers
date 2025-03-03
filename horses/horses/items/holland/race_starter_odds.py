import scrapy
from horses.items.base import RaceStarterOdds
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_odds


class DutchRaceStarterOdds(RaceStarterOdds):
    odds = scrapy.Field(
        input_processor=MapCompose(handle_odds), output_processor=TakeFirst()
    )
