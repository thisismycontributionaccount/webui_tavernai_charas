# TavernAICard.py
"""
Generic class for Tavern AI style character cards.

This module provides a class that represents a Tavern AI style character card.
Site specfic information is not included in this class and will be handled
by the respective extended classes.
"""
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
#from TavernAICategory import TavernAICategory
from TavernAICard import TavernAICard
from TavernAIService import TavernAIService

TAGS = ["chara", "UserComment", "Chara"]
IFD_CODE_LOOKUP = {i.value: i.name for i in ExifTags.IFD}
API_URL = "https://tavernai.net"
CATEGORIES = f"{API_URL}/api/categories"
CHARACTERS = f"{API_URL}/api/characters"
USERS = f"{API_URL}/api/users"
RECENT_CHARAS = f"{CHARACTERS}/board"



class TavernAICard:
    """
    A character card instance for online fetched character cards.
    """

    def __init__(
        self,
        id: int,
        public_id: str,
        public_id_short: str,
        user_id: int,
        user_name: str,
        user_name_view: str,
        name: str,
        short_description: str,
        create_date: str,
        status: int,
        nsfw: bool,
    ):
        self._id: int = id
        self._public_id: str = public_id
        self._public_id_short: str = public_id_short
        self._user_id: int = user_id
        self._user_name: str = user_name
        self._user_name_view: str = user_name_view
        self._name: str = name
        self._short_description: str = short_description
        self._create_date: str = create_date
        self._status: int = status
        self._nsfw: bool = nsfw

    @property
    def id(self):
        """
        The card's ID.
        """
        return self._id

    @property
    def public_id(self):
        """
        The public card's ID.
        """
        return self._public_id

    @property
    def public_id_short(self):
        """
        The first few characters of the card's public ID.
        """
        return self._public_id_short

    @property
    def user_id(self):
        """
        ID of the author's username.
        """
        return self._user_id

    @property
    def user_name(self):
        """
        Author's username.
        """
        return self._user_name

    @property
    def user_name_view(self):
        """
        Author's username for displaying purposes.
        """
        return self._user_name_view

    @property
    def name(self):
        """
        Character name.
        """
        return self._name

    @property
    def short_description(self):
        """
        Character short description.
        """
        return self._short_description

    @property
    def create_date(self):
        """
        Creation date of the card.
        """
        return self._create_date

    @property
    def status(self):
        """
        Card's status. Not really used.
        """
        return self._status

    @property
    def nsfw(self):
        """
        If the card is SFW or not. Commonly mis-used by the community.
        """
        return self._nsfw

    @property
    def img_url(self):
        """
        The URL relevant the character's image/portrait.
        """
        return f"{API_URL}/{self.user_name}/{self.public_id_short}.webp"

    @staticmethod
    def from_dict(entry: dict):
        """
        Creates a `TavernAICard` card from a `dict`.
        """

        return TavernAICard(
            entry.get("id"),
            entry.get("public_id"),
            entry.get("public_id_short"),
            entry.get("user_id"),
            entry.get("user_name"),
            entry.get("user_name_view"),
            entry.get("name"),
            entry.get("short_description"),
            entry.get("create_date"),
            entry.get("status"),
            entry.get("nsfw") == 1,
        )

    def to_dict(self):
        """
        Convert all card information to a `dict`.
        """

        return {
            "id": self.id,
            "public_id": self.public_id,
            "public_id_short": self.public_id_short,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_name_view": self.user_name_view,
            "name": self.name,
            "short_description": self.short_description,
            "create_date": self.create_date,
            "status": self.status,
            "nsfw": 1 if self.nsfw else 0,
        }

