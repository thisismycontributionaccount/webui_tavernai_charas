import json
import requests
import os
import shutil
import urllib.parse
from glob import glob
from pathlib import Path
from random import randint
from PIL import Image, ExifTags
from typing import Callable
from TavernAICategory import TavernAICategory
from TavernAICard import TavernAICard
#from TavernAIService import TavernAIService

TAGS = ["chara", "UserComment", "Chara"]
IFD_CODE_LOOKUP = {i.value: i.name for i in ExifTags.IFD}
API_URL = "https://tavernai.net"
CATEGORIES = f"{API_URL}/api/categories"
CHARACTERS = f"{API_URL}/api/characters"
USERS = f"{API_URL}/api/users"
RECENT_CHARAS = f"{CHARACTERS}/board"


TAGS = ["chara", "UserComment", "Chara"]
IFD_CODE_LOOKUP = {i.value: i.name for i in ExifTags.IFD}
API_URL = "https://tavernai.net"
CATEGORIES = f"{API_URL}/api/categories"
CHARACTERS = f"{API_URL}/api/characters"
USERS = f"{API_URL}/api/users"
RECENT_CHARAS = f"{CHARACTERS}/board"



class TavernAIService:
    """
    Service regarding all available functions related to the TavernAI API.
    """

    @staticmethod
    def fetch_recent_cards(amount=30, nsfw=True):
        """
        Requests the most recent cards.

        Default:
        - amount = 30
        - nsfw = `True`
        """

        params = TavernAIService.__encode_params(nsfw=nsfw)
        response = requests.get(
            f"{CATEGORIES}/{TavernAIService.__category(recent=True)}{params}"
        ).json()

        return TavernAIService.__parseAmount(amount=amount, decoded=response)

    @staticmethod
    def fetch_random_cards(amount=30, nsfw=True):
        """
        Requests random cards.

        Default:
        - amount = 30
        - nsfw = `True`
        """

        params = TavernAIService.__encode_params(nsfw=nsfw)
        response = requests.get(
            f"{CATEGORIES}/{TavernAIService.__category(random=True)}{params}"
        ).json()

        return TavernAIService.__parseAmount(amount=amount, decoded=response)

    @staticmethod
    def fetch_category_cards(category: str | None = None, amount=30, nsfw=True, page=1):
        """
        Requests cards from a designated category.

        Default:
        - category = None (will throw error)
        - amount = 30
        - nsfw = `True`
        - page = 1
        """

        params = TavernAIService.__encode_params(nsfw=nsfw, page=page)
        response = requests.get(
            f"{CATEGORIES}/{TavernAIService.__category(category=category)}{params}"
        ).json()["results"]

        return TavernAIService.__parseAmount(amount=amount, decoded=response)

    @staticmethod
    def fetch_catergories():
        """
        Requests all available categories
        """

        response = requests.get(CATEGORIES).json()
        categories = [TavernAICategory.from_dict(entry) for entry in response]
        return sorted(categories, key=lambda cat: cat.name)

    @staticmethod
    def fetch_category(name: str):
        """
        Requests a category.
        """

        params = TavernAIService.__encode_params(q=name)
        response = requests.get(CHARACTERS + params).json().get("categories")
        fetched_categories = [TavernAICategory.from_dict(c) for c in response]

        # sourcery skip: use-next
        for cat in fetched_categories:
            if name == cat.name:
                return cat

        return None

    @staticmethod
    def fetch_query(query: str, nsfw=True):
        """
        Requests a search query.

        Default:
        - nsfw = `True`
        """

        params = TavernAIService.__encode_params(nsfw=nsfw, q=query)
        response = requests.get(CHARACTERS + params).json().get("characters")

        return TavernAIService.__parseAmount(response, -1)

    @staticmethod
    def fetch_random_categories(amount=5):
        """
        Requests random categories.

        Default:
        - amount = 5
        """

        response = TavernAIService.fetch_catergories()

        categories: list[TavernAICategory] = []
        counter = 0

        while counter < amount:
            index = randint(1, len(response)) - 1
            if response[index].count > 4:
                categories.append(response[index])
                counter += 1

        return categories

    @staticmethod
    def download_card(card: TavernAICard):
        """
        Downloads a card from the API to the disk.
        """

        image = requests.get(card.img_url)
        image_path = Path("characters").joinpath(f"{card.name}.webp")
        data_path = Path("characters").joinpath(f"{card.name}.json")

        with image_path.open("wb") as f:
            f.write(image.content)

        with data_path.open("w") as data_file:
            exif = TavernAIService.__disect_exif(card)

            exif["short_description"] = exif.pop("personality", "")
            exif["char_name"] = exif.pop("name")
            exif["char_persona"] = exif.pop("description")
            exif["world_scenario"] = exif.pop("scenario")
            exif["char_greeting"] = exif.pop("first_mes")
            exif["example_dialogue"] = exif.pop("mes_example")

            data_file.write(json.dumps(exif))

        # convert to PNG for chat profile display (ooga booga doesn't accept .webp's as profile images)
        Image.open(image_path).convert("RGBA").save(
            Path("characters").joinpath(f"{card.name}.png"),
        )
        # delete original .webp (although it contains the original EXIF data) to not clutter the character folder
        image_path.unlink()

    @staticmethod
    def __disect_exif(card: TavernAICard) -> dict:
        img = Image.open(Path("characters").joinpath(f"{card.name}.webp"))

        exif = {
            ExifTags.TAGS[k]: v for k, v in img.getexif().items() if k in ExifTags.TAGS
        }

        img_bytes: bytes = exif.get("UserComment")
        hex_bytes = list(map(lambda x: hex(int(x))[2:], img_bytes[8:].split(b",")))

        chara_data = bytearray.fromhex(" ".join(hex_bytes).upper()).decode("utf-8")
        return json.loads(chara_data)

    @staticmethod
    def __category(recent=False, random=False, category: str | None = None):
        if recent or random:
            return f"${'recent' if recent else 'random'}/characters"

        if category is None:
            raise ValueError("Category cannot be None")

        return f"{TavernAIService.__url_encode(category)}/characters"

    @staticmethod
    def __parseAmount(decoded, amount):
        if amount == -1:
            return [TavernAICard.from_dict(entry) for entry in decoded]

        cards: list[TavernAICard] = []
        count = 0

        for entry in decoded:
            if count >= amount:
                break

            cards.append(TavernAICard.from_dict(entry))
            count += 1

        return cards

    @staticmethod
    def __url_encode(s: str):
        return urllib.parse.quote(s, safe="")

    @staticmethod
    def __encode_params(**kwargs):
        if "nsfw" in kwargs:
            kwargs["nsfw"] = "on" if kwargs.get("nsfw") else "off"

        return f"?{urllib.parse.urlencode(kwargs, quote_via=urllib.parse.quote)}"
