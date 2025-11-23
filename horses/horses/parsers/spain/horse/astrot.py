import json

from scrapy.http.response import Response
from horses.items.spain import (
    SpanishHorse,
    SpanishHorseInfo,
    SpanishRegistration,
    SpanishResultSummary,
)
from itemloaders import ItemLoader


def parse_offspring(response: Response, horse: ItemLoader) -> None:
    offspring_json = json.loads(response.body)

    for horse_json in offspring_json:
        offspring = ItemLoader(item=SpanishHorse())

        offspring_info = ItemLoader(item=SpanishHorseInfo())

        offspring_info.add_value("name", horse_json["nombre"])
        offspring_info.add_value("birthdate", horse_json["fecha_nacimiento"])
        offspring_info.add_value("ueln", str(horse_json["ueln"]))
        offspring_info.add_value("gender", horse_json["nombre_sexo"])
        offspring_info.add_value("country", horse_json["pais"])

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=SpanishRegistration())

        offspring_registration.add_value("name", horse_json["nombre"])
        offspring_registration.add_value("link", horse_json["id_caballo"])

        offspring_registration.add_value("source", "fect")

        offspring.add_value("registrations", offspring_registration.load_item())

        parent_gender = "padre" if horse.get_output_value("horse_info")["gender"] == "mare" else "madre"

        parent = ItemLoader(item=SpanishHorse())

        parent_info = ItemLoader(item=SpanishHorseInfo())

        parent_info.add_value("name", horse_json[parent_gender])
        parent_info.add_value("country", horse_json[parent_gender])

        parent_info.add_value(
            "gender",
            "horse" if parent_gender == "padre" else "mare"
        )

        parent.add_value("horse_info", parent_info.load_item())

        parent_registration = ItemLoader(item=SpanishRegistration())

        parent_registration.add_value("name", horse_json[parent_gender])
        parent_registration.add_value("link", horse_json[f"id_{parent_gender}"])
        parent_registration.add_value("source", "fect")

        parent.add_value("registrations", parent_registration.load_item())

        offspring.add_value(
            "sire" if parent_info.get_output_value("gender") == "horse" else "dam",
            parent.load_item()
        )

        if horse_json["n_numCarreras"] > 0:
            result_summary = ItemLoader(item=SpanishResultSummary())

            result_summary.add_value("earnings", horse_json["importe_carreras"])
            result_summary.add_value("mark", horse_json["n_record"])
            result_summary.add_value("starts", horse_json["n_numCarreras"])
            result_summary.add_value("wins", horse_json["n_totalPrimeros"])

            result_summary.add_value("year", 0)

            offspring.add_value("result_summaries", result_summary.load_item())

        horse.add_value("offspring", offspring.load_item())
