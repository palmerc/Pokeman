import random
import re

from bs4 import BeautifulSoup

from pokemon.browser import Browser
from pokemon.pokemon import Pokemon


class Pokemen:
    def __init__(self):
        pass

    @classmethod
    def select_pokemon(cls, number=None):
        if number:
            pokemen = list(filter(lambda p: p.number == number, Pokemen.gather_pokemen()))
        else:
            pokemen = random.sample(Pokemen.gather_pokemen(), 1)

        if pokemen:
            pokemon = pokemen.pop()
            return pokemon
        return None

    @classmethod
    def gather_pokemen(cls):
        pokedex = 'https://www.pokemon.com/us/pokedex/'

        page_source = Browser().get(pokedex)
        soup = BeautifulSoup(page_source, 'html.parser')

        pokedex_re = re.compile('^National Pokédex$')
        pokemon_re = re.compile('(\d+) - (.+)$')

        pokemen = []
        for header in soup.findAll('h2', text=pokedex_re):
            ul_tag = header.findNext('ul')
            for a_tag in ul_tag.find_all('a'):
                poketext = a_tag.text.strip()
                match = re.match(pokemon_re, poketext)
                if match:
                    number = match.group(1)
                    name = match.group(2)
                    pokemen.append(Pokemon(name, number))

        pokemen.sort(key=lambda p: p.number)
        return pokemen
