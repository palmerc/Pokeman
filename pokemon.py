import os
import requests
from bs4 import BeautifulSoup

from pokemon_tcg import PokemenTCG


class Pokemon(object):
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self._form = 0
        self._forms = []

    def __str__(self):
        return self.name()

    def short_name(self):
        return self.name

    def display_name(self):
        if len(self.available_forms()) > 1:
            form = self.current_form()['form']
            return '{} ({}) - {}'.format(self.name, form, self._padded_number())
        else:
            return '{} - {}'.format(self.name, self._padded_number())

    def img_url(self):
        form = self.current_form()
        img_url = ''
        if form:
            img_url = form['img']
        return img_url

    def random_card(self):
        return PokemenTCG(self).random_card()

    def png(self):
        name = 'Pokémon'
        png = None
        if self.img_url():
            name = 'pokemon' + os.path.basename(self.img_url())
            png = requests.get(self.img_url()).content
        return name, png

    def current_form(self):
        forms = self.available_forms()
        form = None
        if forms:
            form = forms[self._form]
        return form

    def available_forms(self):
        if len(self._forms) == 0:
            self._get_pokemon_formes()
        return self._forms

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
        detail_url = pokedex + self.number
        response = Pokemon._request_get(detail_url)
        return BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def _request_get(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15'}
        response = requests.head(url, headers=headers, allow_redirects=True)
        detail_url = response.url
        return requests.get(detail_url, headers=headers, cookies=response.cookies)

