from .substitutions import substitutions
from .measurements import measurements
from .measurements import unit_types
from .measurements import abbrevs
from .preparations import preparations
from .primary_cooking_methods import primary
from .vegan import nontype as vegan_nontype
from .vegan import rtype as vegan_rtype
from .vegetarian import nontype as vegetarian_nontype
from .vegetarian import rtype as vegetarian_rtype
# stackoverflow.com/questions/22511792/python-from-dotpackage-import-syntax
# The . is a shortcut that tells it search in current package before rest of
# the PYTHONPATH.