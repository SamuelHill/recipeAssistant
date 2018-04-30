from ._abstract import AbstractScraper
from ._utils import get_minutes, normalize_string


class Cookstr(AbstractScraper):

    @classmethod
    def host(self):
        return 'cookstr.com'

    def title(self):
        return normalize_string(self.soup.find('h1', {'class': 'articleHeadline'}).get_text())

    def total_time(self):
        sections = self.soup.findAll('div', {'class': 'articleAttrSection'})
        total_time = 0
        for section in sections:
            time = section.find(text='Total Time')
            if time:
                total_time += get_minutes(time.parent.parent)
        return total_time

    def ingredients(self):
        ingredients_html = self.soup.find('div', {'class': "recipeIngredients"})

        return [
            normalize_string(ingredient.get_text())
            for ingredient in ingredients_html.findAll('li')
        ]

    def instructions(self):

        instructions_html = self.soup.find('div', {'class': 'stepByStepInstructionsDiv'})

        return '\n'.join([
            normalize_string(instruction.get_text())
            for instruction in instructions_html.findAll('p')
        ])
