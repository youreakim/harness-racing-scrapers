import scrapy
from horses.items.base import RaceStarterInfo
from itemloaders.processors import Compose, MapCompose, TakeFirst

from .processor_functions import (
    convert_to_int,
    did_finish,
    did_gallop,
    did_start,
    handle_person_name,
    handle_starter_finish,
    handle_starter_purse,
    handle_startnumber,
    is_starter_disqualified,
)


class ItalianRaceStarterInfo(RaceStarterInfo):
    # alla ska helst vara samma värde, men åtminstone en True
    disqualified = scrapy.Field(
        input_processor=MapCompose(is_starter_disqualified),
        # output_processor=TakeFirst()
        output_processor=Compose(lambda v: any(v)),
    )
    # alla ska vara samma
    # distance = scrapy.Field(
    #     input_processor=MapCompose(convert_to_int),
    #     output_processor=TakeFirst()
    # )
    driver = scrapy.Field(
        input_processor=MapCompose(handle_person_name), output_processor=TakeFirst()
    )
    # alla ska vara samma
    finish = scrapy.Field(
        input_processor=MapCompose(handle_starter_finish), output_processor=TakeFirst()
    )
    # alla ska vara samma, om en False => False
    finished = scrapy.Field(
        input_processor=MapCompose(did_finish),
        # output_processor=TakeFirst()
        output_processor=Compose(lambda v: all(v)),
    )
    # alla ska vara samma, om en True => True
    gallop = scrapy.Field(
        input_processor=MapCompose(did_gallop),
        # output_processor=TakeFirst()
        output_processor=Compose(lambda v: any(v)),
    )
    # alla ska vara samma
    # order = scrapy.Field(
    #     input_processor=MapCompose(convert_to_int),
    #     output_processor=TakeFirst()
    # )
    postposition = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    # alla ska vara samma
    purse = scrapy.Field(
        input_processor=MapCompose(handle_starter_purse), output_processor=TakeFirst()
    )
    # alla ska vara samma, en False => False
    started = scrapy.Field(
        input_processor=MapCompose(did_start),
        # output_processor=TakeFirst()
        output_processor=Compose(lambda v: all(v)),
    )
    startnumber = scrapy.Field(
        input_processor=MapCompose(handle_startnumber), output_processor=TakeFirst()
    )
    trainer = scrapy.Field(
        input_processor=MapCompose(handle_person_name), output_processor=TakeFirst()
    )
