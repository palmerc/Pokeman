from pokemon import Pokemon

import re
import random
import requests
from bs4 import BeautifulSoup


class Pokemen:
    def __init__(self):
        pass

    @classmethod
    def select_pokemon(cls, number=None):
        if number:
            pokemen = list(filter(lambda p: p.number == number, Pokemen.gather_pokemen()))
        else:
            pokemen = random.sample(Pokemen.gather_pokemen(), 1)

        return pokemen.pop()

    @classmethod
    def gather_pokemen(cls):
        pokedex = 'https://www.pokemon.com/us/pokedex/'

        request = requests.get(pokedex)
        soup = BeautifulSoup(request.text, 'html.parser')

        pokedex_re = re.compile('^National Pokédex$')
        pokemon_re = re.compile('(\d+) - (\w+)')

        pokemen = []
        for header in soup.find_all('h2', text=pokedex_re):
            ul_tag = header.findNext('ul')
            for a_tag in ul_tag.find_all('a'):
                match = re.match(pokemon_re, a_tag.text)
                number = match.group(1)
                name = match.group(2)
                pokemen.append(Pokemon(name, number))

        pokemen.sort(key=lambda p: p.number)
        return pokemen
