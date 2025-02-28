import json

import arrow
import scrapy
from horses.items.france import FrenchHorse
from horses.parsers.france.horse.ifce import (
    get_number_offspring_pages,
    parse_horse_info_ifce,
    parse_offspring_ifce,
    parse_pedigree_ifce,
    parse_search_ifce,
)
from horses.parsers.france.horse.letrot import (
    get_number_offspring_pages_letrot,
    get_number_starts_pages_letrot,
    parse_horse_letrot,
    parse_offspring_letrot,
    parse_result_summaries_letrot,
    parse_search_letrot,
    parse_siblings_letrot,
    parse_starts_letrot,
)
from horses.parsers.france.horse.trotpedigree import (
    parse_horse_tp,
    parse_offspring_tp,
    parse_search_tp,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

FRENCH_DOMAINS = ["letrot.com", "trot-pedigree.net", "ifce.fr"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
TP_BASE_URL = "http://trot-pedigree.net/js/app"


class FranceHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = FRENCH_DOMAINS
        self.horses = []
        self.name = name

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": "https://infochevaux.ifce.fr/fr/info-chevaux",
                    "formdata": {
                        "recherche": json.dumps(
                            {
                                "recherche": f"{self.name}",
                                "page": 1,
                                "nbResultat": "10",
                                "facettes": {},
                                "filtres": {},
                            }
                        )
                    },
                },
            ),
            (
                scrapy.Request,
                {"url": f"https://www.letrot.com/v1/api/search/fuzzy/{self.name}"},
            ),
            (
                scrapy.Request,
                {
                    "url": f"{TP_BASE_URL}/combocnfromdb.php?mask={self.name}&pos=0&dhxr{int(arrow.utcnow().timestamp() * 1000)}=1"
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        horse_ids = []

        if "combocnfromdb" in response.url:
            horse_ids.extend(parse_search_tp(response, self.name))
        elif "letrot.com" in response.url:
            horse_ids.extend(parse_search_letrot(response, self.name))
        elif "ifce.fr" in response.url:
            horse_ids.extend(parse_search_ifce(response, self.name))

        self.horses.extend(FranceHorse(horse_id=horse_id) for horse_id in horse_ids)


class FranceHorse:
    def __init__(self, horse_id: str) -> None:
        self.horse = ItemLoader(item=FrenchHorse())
        self.horse_id = horse_id
        self.family_id = None
        self.siblings = []

        self.requests = []

        if len(self.horse_id) == 6:
            self.requests.extend(
                [
                    (
                        scrapy.Request,
                        {"url": f"{TP_BASE_URL}/comp_ped.php?lechev='{self.horse_id}'"},
                    ),
                    (
                        scrapy.Request,
                        {
                            "url": f"{TP_BASE_URL}/treefromdbp.php?idpere='{self.horse_id}'"
                        },
                    ),
                ]
            )
        elif len(self.horse_id) == 12:
            self.requests.extend(
                [
                    (
                        scrapy.Request,
                        {
                            "url": f"https://www.letrot.com/v1/api/horses/"
                            f"{self.horse_id}/siblings?limit=20&page=1"
                        },
                    ),
                    (
                        scrapy.Request,
                        {
                            "url": f"https://www.letrot.com/v1/api/horses/{self.horse_id}/pedigree"
                        },
                    ),
                    (
                        scrapy.Request,
                        {
                            "url": f"https://www.letrot.com/v1/api/horses/{self.horse_id}"
                            f"/production-stats?type=current_horse"
                        },
                    ),
                    (
                        scrapy.Request,
                        {
                            "url": f"https://www.letrot.com/v1/api/horses/{self.horse_id}"
                            f"/analyzes?type=years&limit=20&page=1&sort_by=id&order_by=desc"
                        },
                    ),
                ]
            )
        else:
            self.requests.extend(
                [
                    (
                        scrapy.Request,
                        {
                            "url": f"https://infochevaux.ifce.fr/fr/{self.horse_id}/infos-generales"
                        },
                    ),
                    (
                        scrapy.FormRequest,
                        {
                            "url": f"https://infochevaux.ifce.fr/fr/{self.horse_id}/pedigree-et-chevaux-associes/pedigree-5-generations",
                            "formdata": {
                                "recherche": json.dumps(
                                    {
                                        "id": f"{self.horse_id[self.horse_id.rfind('-') + 1:]}",
                                        "ancetresCommuns": True,
                                        "coefficientConsanguinite": False,
                                    }
                                )
                            },
                            "meta": {
                                **META_PLAYWRIGHT,
                                "playwright_page_methods": [
                                    PageMethod(
                                        "wait_for_selector", "div#pedigree5G div"
                                    )
                                ],
                            },
                        },
                    ),
                ]
            )

    def handle_response(self, response):
        if "/comp_ped" in response.url:
            parse_horse_tp(response, self.horse, self.horse_id)
        elif "/treefromdbp" in response.url:
            parse_offspring_tp(response, self.horse)
        elif response.url.endswith("/pedigree"):
            parse_horse_letrot(response, self.horse, self.siblings)
        elif "/production-stats" in response.url:
            pages = get_number_offspring_pages_letrot(response)

            self.requests.extend(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.letrot.com/v1/api/horses/{self.horse_id}/productions"
                        f"?generations=1990-2025&limit=20&page={page}&sort_by=horseName&order_by=asc"
                    },
                )
                for page in range(1, pages + 1)
            )
        elif "/productions?" in response.url:
            parse_offspring_letrot(response, self.horse)
        elif "/siblings" in response.url:
            parse_siblings_letrot(response, self.siblings)
        elif "/perfs?" in response.url:
            parse_starts_letrot(response, self.horse)
        elif "/analyzes" in response.url:
            parse_result_summaries_letrot(response, self.horse)

            pages = get_number_starts_pages_letrot(response)

            self.requests.extend(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.letrot.com/v1/api/horses/{self.horse_id}/perfs?limit=20&page={page}&excludeNP=false&sort_by=date_performance&order_by=desc"
                    },
                )
                for page in range(1, pages + 1)
            )
        elif response.url.endswith("/infos-generales"):
            parse_horse_info_ifce(response, self.horse, self.horse_id)

            pages = get_number_offspring_pages(response)

            for page in range(1, pages + 1):
                self.requests.append(
                    (
                        scrapy.FormRequest,
                        {
                            "url": f"https://infochevaux.ifce.fr/fr/{self.horse_id}/production/production-totale",
                            "formdata": {
                                "recherche": json.dumps(
                                    {
                                        "recherche": "",
                                        "page": page,
                                        "nbResultat": "100",
                                        "facettes": {},
                                        "filtres": {},
                                    }
                                )
                            },
                        },
                    ),
                )
        elif response.url.endswith("/pedigree-5-generations"):
            parse_pedigree_ifce(response, self.horse)
        elif response.url.endswith("/production-totale"):
            parse_offspring_ifce(response, self.horse, self.horse_id)

    def return_horse(self):
        return self.horse.load_item()
