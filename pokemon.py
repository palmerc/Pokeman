import os
import requests


class Pokemon:
    def __init__(self, name, number):
        self.name = name
        self.number = number

    def __str__(self):
        return self.name()

    def name(self):
        return f'{self.name} - {self._padded_number()}'

    def img_url(self):
        return f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{self._padded_number()}.png'

    def png(self):
        name = 'pokemon' + os.path.basename(self.img_url())
        png = requests.get(self.img_url()).content
        return name, png

    def _padded_number(self):
        return f'{int(self.number):03}'
