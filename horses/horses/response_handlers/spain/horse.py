import scrapy
from horses.parsers.spain.horse.astrot import (
    parse_offspring,
)
from horses.parsers.spain.horse.fect import (
    parse_horse,
    parse_search_result
)
from itemloaders import ItemLoader


SPANISH_DOMAINS = ["federaciobaleardetrot.com", "astrot.com"]


class SpainHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = SPANISH_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": "https://www.federaciobaleardetrot.com/buscarCaballosServidor.php",
                    "formdata": {
                        "draw": "1",
                        "columns[0][data]": "ueln",
                        "columns[0][name]": "",
                        "columns[0][searchable]": "true",
                        "columns[0][orderable]": "true",
                        "columns[0][search][value]": "",
                        "columns[0][search][regex]": "false",
                        "columns[1][data]": "nombre",
                        "columns[1][name]": "",
                        "columns[1][searchable]": "true",
                        "columns[1][orderable]": "true",
                        "columns[1][search][value]": "",
                        "columns[1][search][regex]": "false",
                        "columns[2][data]": "importe_total",
                        "columns[2][name]": "",
                        "columns[2][searchable]": "true",
                        "columns[2][orderable]": "true",
                        "columns[2][search][value]": "",
                        "columns[2][search][regex]": "false",
                        "columns[3][data]": "num_carreras",
                        "columns[3][name]": "",
                        "columns[3][searchable]": "true",
                        "columns[3][orderable]": "true",
                        "columns[3][search][value]": "",
                        "columns[3][search][regex]": "false",
                        "order[0][column]": "0",
                        "order[0][dir]": "asc",
                        "start": "0",
                        "length": "10",
                        "search[value]": "",
                        "search[regex]": "false",
                        "nombreCaballo": self.name.replace(" ", "+"),
                    },
                },
            )
        ]

    def handle_response(self, response):
        self.parse_search_result(response)

    def parse_search_result(self, response):
        horses = parse_search_result(response)

        for horse in horses:
            self.horses.append(SpainHorse(horse=horse["horse"], horse_id=horse["horse_id"]))

            break


class SpainHorse:
    def __init__(self, horse: ItemLoader, horse_id: str) -> None:
        self.horse = horse
        self.horse_id = horse_id

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://www.federaciobaleardetrot.com/datosCaballo.php?idCaballo={self.horse_id}",
                },
            ),
            (
                scrapy.Request,
                {
                    "url": f"https://www.astrot.com/ajax/getListaHijos.php?tipo=1&idCaballo={self.horse_id}",
                },
            ),
        ]

    def handle_response(self, response):
        if "/datosCaballo.php" in response.url:
            parse_horse(response, self.horse)
        elif "Hijos.php" in response.url:
            parse_offspring(response, self.horse)

    def return_horse(self):
        return self.horse.load_item()
