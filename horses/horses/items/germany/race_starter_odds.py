import scrapy
from horses.items.base import RaceStarterOdds
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_show_odds


class GermanRaceStarterOdds(RaceStarterOdds):
    odds = scrapy.Field(
        input_processor=MapCompose(handle_show_odds), output_processor=TakeFirst()
    )
