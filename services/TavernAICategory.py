# TavernAICategory.py
"""
Generic class for Tavern AI style categories.

This module provides a class that represents a Tavern AI style categories.
Site specfic information is not included in this class and will be handled
by the respective extended classes for each card source.
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


class TavernAICategory:
    def __init__(self, id: int, name: str, name_view: str, count: int):
        self._id = id
        self._name = name
        self._name_view = name_view
        self._count = count

    @property
    def id(self):
        """
        Category's ID.
        """
        return self._id

    @property
    def name(self):
        """
        Category name.
        """
        return self._name

    @property
    def name_view(self):
        """
        Category name for displaying purposes.
        """
        return self._name_view

    @property
    def count(self):
        """
        Amount of characters this category has been linked to.
        """
        return self._count

    @staticmethod
    def from_dict(entry: dict):
        """
        Creates a `TavernAICategory` category from a `dict`.
        """

        return TavernAICategory(
            entry.get("id"),
            entry.get("name"),
            entry.get("name_view"),
            entry.get("count"),
        )

    def to_dict(self) -> dict:
        """
        Convert all category information to a `dict`.
        """

        return {
            "id": self._id,
            "name": self._name,
            "name_view": self._name_view,
            "count": self._count,
        }

    def category_url(self, nsfw=True):
        return f"{CATEGORIES}/{self._name}/characters?nsfw={'on' if nsfw else 'off'}"


