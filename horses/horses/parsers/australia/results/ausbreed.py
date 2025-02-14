from horses.items.australia import AustralianRegistration
from itemloaders import ItemLoader


def parse_ausbreed_race_result(response, starters):
    for current_starter in starters[
        response.url[response.url.rfind("=") + 1 :]
    ].values():
        horse = current_starter["horse"]

        name = horse.get_output_value("horse_info")["name"]

        if (
            response.xpath(f'//a[text()="{name}"]')
            and current_starter["starter"].get_output_value("starter_info")["started"]
        ):
            registration = ItemLoader(
                item=AustralianRegistration(),
                selector=response.xpath(f'//a[text()="{name}"]'),
            )

            registration.add_value("name", name)
            registration.add_value("source", "ab")

            registration.add_xpath("link", "./@href")

            horse.add_value("registrations", registration.load_item())
