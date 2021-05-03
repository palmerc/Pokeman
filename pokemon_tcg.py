import random
import requests
from bs4 import BeautifulSoup


base_url = 'https://www.pokemon.com'


class PokemonTCG(object):
    def __init__(self, number, name, image_url, card_url, expansion):
        self.number = number
        self.name = name
        self.image_url = image_url
        self.card_url = card_url
        self.expansion = expansion

    def __str__(self):
        return self.display()

    def display_name(self):
        return '{}, Expansion: {}, Card: {}'.format(self.name, self.expansion, self.number)

    def image(self):
        return self.image_url

    def url(self):
        return self.card_url


class PokemenTCG(object):
    def __init__(self, pokemon):
        self.pokemon = pokemon

    def all_cards(self):
        cards = []
        soup = self._pokemon_detail()
        for tcg_section in soup.findAll('section', {'id': 'trading-card-slider'}):
            for card_li in tcg_section.findAll('li', {'data-content-category': 'Card'}):
                name = card_li.find('div', {'class': 'card-name'}).h5.text
                image = card_li.find('div', {'class': 'card-img'}).img['data-preload-src']
                url = base_url + card_li.find('a')['href']
                number = card_li.find('span', {'class': 'card-number'}).text
                expansion = card_li.find('span', {'class': 'expansion-name'}).text

                cards.append(PokemonTCG(number, name, image, url, expansion))
        return cards

    def random_card(self):
        return random.sample(self.all_cards(), 1).pop()

    def _pokemon_detail(self):
        pokedex = base_url + '/us/pokedex/'

        request = requests.get(pokedex + self.pokemon.number)
        return BeautifulSoup(request.text, 'html.parser')
