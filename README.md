# word_factori_calc

Calculator to determine optimal solutions for the game Word Factori: https://store.steampowered.com/app/2072840/Word_Factori/



# Files

recipes.json: game file describing symbol recipes - has unicode for door and key replaced with "d" and "k" to avoid unicode characters

symbol_map.yaml: file describing all symbol transformations based on data in recipes.json

dependency_map.yaml: file describing symbols required in order to make other symbols, e.g., L requires I & I1, X requires I & V

word_factori_calc.py: all code used to compute Word Factori solutions
