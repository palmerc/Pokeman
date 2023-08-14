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

        pokemon = pokemen.pop()

        return pokemon

    @classmethod
    def gather_pokemen(cls):
        pokedex = 'https://www.pokemon.com/us/pokedex/'

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15'}
        request = requests.get(pokedex, headers=headers, allow_redirects=True)
        soup = BeautifulSoup(request.text, 'html.parser')

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
