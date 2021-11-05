import pokemon

import unittest

class TestPokemon(unittest.TestCase):
    def setUp(self) -> None:
        self.p = pokemon.Pokemon(number=133)

    def test_pokemon_by_number(self):
        self.assertEqual(self.p.short_name(), 'Bulbasaur')

    def test_evolutions(self):
        evolutions = self.p.evolutions()
        pass
