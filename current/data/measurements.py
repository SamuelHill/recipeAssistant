measurements = dict()

measurements['bunch'] 		= "a collection of the ingredient, growing, fastened, or grouped together"
measurements['can'] 		= "a can is the entirety of the can of your ingredient. Most often packaged in 8 or 16 ounces"
measurements['clove'] 		= "a clove is 1 teaspoon of your chopped ingredient or half a teaspoon of your minced ingredient. This measurement is most often associated with garlic."
measurements['container'] 	= "a container is whatever holds the entirety of the ingredient"
measurements['envelope'] 	= "the amount of material in an envelope, or packet, varies. Refer to your list of ingredients for the exact measurement"
measurements['head'] 		= "a head usually refers to a single, intact, dense rosette of leaves which ultimately develops into a compact head. The weight of which is, on average, about one pound."
measurements['teaspoon'] 	= "a teaspoon is one third of a tablespoon. You can most often use one half of a small spoon to replicate this measurement."
measurements['tablespoon'] 	= "a tablespoon is 3 teaspoons. You can most often use a normal spoon to replicate this measurement."
measurements['fluid ounce'] = "a fluid ounce is 2 tablespoons of liquid material"
measurements['cup'] 		= "a cup is 8 fluid ounces"
measurements['pint'] 		= "a pint is about 2 cups or 16 fluid ounces"
measurements['quart'] 		= "a quart is 2 pints or 32 fluid ounces"
measurements['gallon'] 		= "a gallon is 4 quarts, 128 ounces, or just under 16 cups"
measurements['gram'] 		= "a gram is a standard unit of mass measurement in the international System of Units"
measurements['kilogram'] 	= "a kilogram is 1000 grams"
measurements['pound'] 		= "a pound is 16 ounces"
measurements['inch'] 		= "an inch is 2.54 centimeters or roughly the distance from the top knuckle on your thumb to your thumb tip. "
# measurements['cube'] 		= "a cube is a block of something with six sides. For example, a sugar cube is a cube of sugar."
measurements['to taste'] 	= "to taste is a method of adding flavor that requires you to frequently taste the result and adjust to your liking"


unit_types = dict()
# METRIC (volume, weight)
unit_types['milliliter'] = ['ml','milliliter','millilitre','cc','mL',
                            'milliliters','millilitres']
unit_types['liter']      = ['l','liter','litre','L','liters','litres']
unit_types['deciliter']  = ['dl','deciliter','decilitre','dL',
                            'deciliters','decilitres']
unit_types['milligram']  = ['mg','milligram','milligramme',
                            'milligrams','milligrammes']
unit_types['gram']       = ['g','gram','gramme','grams','grammes']
unit_types['kilogram']   = ['kg','kilogram','kilogramme',
                            'kilograms','kilogrammes']
# US CUSTOMARY (volume, weight)
unit_types['drop']         = ['drop','dr','gt','gtt','drops','drs']
unit_types['smidgen']      = ['smidgen','smdg','smi']
unit_types['pinch']        = ['pinch','pn','pinchs','pinches']
unit_types['dash']         = ['dash','ds','dashes']
unit_types['saltspoon']    = ['saltspoon','scruple','ssp',
                              'saltspoons','scruples','ssps']
unit_types['coffeespoon']  = ['coffeespoon','csp','coffeespoons','csps']
unit_types['fluid dram']   = ['fluid dram','fl.dr','fluid drams','fl.drs']
unit_types['dessertspoon'] = ['dessertspoon','dsp','dssp','dstspn',
                              'dessertspoons','dsps','dssps','dstspns']
unit_types['teaspoon']     = ['teaspoon','t','tsp','teaspoons','tsps']
unit_types['tablespoon']   = ['tablespoon','T','tbl','tbs','tbsp',
                              'tablespoons','tbls','tbsps']
unit_types['fluid ounce']  = ['fluid ounce','fl oz','fluid ounces',
                              'fl ozs']
unit_types['wineglass']    = ['wineglass','wgf','wineglasses','wgfs']
unit_types['gill']         = ['gill','teacup','gills','teacups']
unit_types['pottle']       = ['pottle','pot','pottles','pots']
unit_types['cup']          = ['cup','c','cups']
unit_types['pint']         = ['pint','p','pt','fl pt','pints','pts',
                              'fl pts']
unit_types['quart']        = ['quart','q','qt','fl qt','quarts','qts'
                              'fl qts']
unit_types['gallon']       = ['gallon','g','gal','gallons','gals']
unit_types['pound']        = ['pound','lb','pounds','lbs']
unit_types['ounce']        = ['ounce','oz','ounces','ozs']
# DISTANCE:
unit_types['millimeter'] = ['mm','millimeter','millimetre',
                            'millimeters','millimetres']
unit_types['centimeter'] = ['cm','centimeter','centimetre',
                            'centimeters','centimetres']
unit_types['inch']       = ['inch','\"','inches']
unit_types['foot']       = ['foot','\'','feet']
# ALL ABBREVIATIONS
abbrevs = [abbrev for abbrevs in unit_types.values()
                               for abbrev in abbrevs]
