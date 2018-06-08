import sys

sys.path.append('sites')
# import sys; sys.path.append('sites')

from epicurious import Epicurious

recipe = Epicurious("http://www.epicurious.com/recipes/food/views/Chocolate-Almond-and-Banana-Parfaits-357369")

# recipe.save()
# Save doesn't seem to be working...

print recipe.getTitle()
print recipe.getIngredients()
print recipe.getDirections()