from agent import get_famous_person_info
from ulice import get_street_info


def chatbot(street_name):
    street_info = get_street_info(street_name)
    if street_info:
        street_info_str = "\n".join(
            [f"{key}: {value}" for key, value in street_info[0].items()]
        )
        if (
            "Opis značenja imena ulice/trga" in street_info[0]
            and street_info[0]["Opis značenja imena ulice/trga"]
        ):
            famous_person_info = get_famous_person_info(
                street_info[0]["Opis značenja imena ulice/trga"]
            )
            return f"Street Info:\n{street_info_str}\n\nFamous Person Info:\n{famous_person_info}"
        else:
            return f"Street Info:\n{street_info_str}"
    else:
        return "Street not found."


# Example usage
street_name = "Trg bana Josipa Jelačića"
print(chatbot(street_name))
