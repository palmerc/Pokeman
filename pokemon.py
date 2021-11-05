import os
import requests
from bs4 import BeautifulSoup

from pokemon_tcg import PokemenTCG


class Pokemon(object):
    def __init__(self, number=None):
        self.number = number
        self.name = None
        self._form = 0
        self._forms = []
        self._update_name()

    def __str__(self):
        return self.display_name()

    def short_name(self):
        return self.name

    def display_name(self):
        if len(self.available_forms()) > 1:
            form = self.current_form()['form']
            return '{} ({}) - {}'.format(self.name, form, self._padded_number())
        else:
            return '{} - {}'.format(self.name, self._padded_number())

    def img_url(self):
        return self.current_form()['img']

    def random_card(self):
        return PokemenTCG(self).random_card()

    def png(self):
        name = 'pokemon' + os.path.basename(self.img_url())
        png = requests.get(self.img_url()).content
        return name, png

    def current_form(self):
        return self.available_forms()[self._form]

    def available_forms(self):
        if len(self._forms) == 0:
            self._get_pokemon_formes()
        return self._forms

    def evolutions(self):
        evolutions = {}
        soup = self._pokemon_detail()
        for stages in soup.findAll('ul', {'class': 'evolution-profile'}):
            positions = ['first', 'middle', 'last']
            for position in positions:
                for stage in stages.findAll('li', {'class': position}):
                    evolutions[position] = []
                    for evolution in stage.findAll('h3'):
                        pokemon_numbers = evolution.findAll('span', {'class': 'pokemon-number'})
                        for pokemon_number in pokemon_numbers:
                            evolution_text = evolution.text.strip()
                            number = pokemon_number.text.strip()
                            name = evolution_text.removesuffix(number)
                            number = number.removeprefix('#')
                            name = name.strip()
                            evolutions[position].append((name, number))
        return evolutions

    def _update_name(self):
        if self.number:
            detail = self._pokemon_detail()
            title = detail.title.text
            self.name = title.removesuffix('| Pokédex').strip()

    def _padded_number(self):
        return f'{int(self.number):03}'

    def _get_pokemon_formes(self):
        soup = self._pokemon_detail()
        for pokemon_details in soup.findAll('section', {'class': 'pokedex-pokemon-details'}):
            profile_images = pokemon_details.findNext('div', {'class': 'profile-images'})
            for a_tag in profile_images.findAll('img'):
                self._forms.append({'form': a_tag['alt'], 'img': a_tag['src']})

    def _pokemon_detail(self):
        pokedex = 'https://www.pokemon.com/us/pokedex/'

        request = requests.get(pokedex + str(self.number))
        return BeautifulSoup(request.text, 'html.parser')
