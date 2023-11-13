import sys
import json, yaml
import string
from ordered_set import OrderedSet
import itertools
from functools import reduce
import copy

# Format of a symbol in the mapping variable/file
def symbol_schema(symbol):
    return {symbol: []}

# Format of a recipe in the mapping variable/file
def recipe_schema(factory, input_symbols):
    if isinstance(input_symbols, list):
        return {'factory': factory, 'input_symbols': input_symbols}
    else:
        return {'factory': factory, 'input_symbols': [input_symbols]}

class word_factori_calc:
    def __init__(self, recipes_json, symbol_map_yaml, dependency_map_yaml):
        self.symbol_map_yaml = symbol_map_yaml
        self.dependency_map_yaml = dependency_map_yaml

        with open(self.symbol_map_yaml, 'r') as file:
            self.base_symbol_map = yaml.load(file, Loader=yaml.CLoader)
        with open(self.dependency_map_yaml, 'r') as file:
            self.base_dependency_map = yaml.load(file, Loader=yaml.CLoader)

        # Maps used for actual calculations - may have different symbols or factories banned
        self.adjusted_symbol_map = self.base_symbol_map
        self.adjusted_dependency_map = self.base_dependency_map

    # Recalculate the symbol_map and dependency_map - necessary when updating banned factories/symbols
    def recalculate_symbol_maps(self):
        self.base_symbol_map = self.create_symbol_map()
        self.base_dependency_map = self.create_dependency_map()

    # Convert recipe json file (unicode already changed) into a more useable mapping file that gives all recipes for a given letter
    def create_symbol_map(self):
        with open(self.recipes_json, 'r') as file:
            recipes = json.load(file)

        base_symbols = list(string.ascii_uppercase)
        base_symbols.extend(recipes['specials'])

        # Special symbols that are equivalent to rotations of each other
        aliased_symbols = {}
        for key,val in recipes['aliases'].items():
            key_alias = key[0]
            val_alias = val
            aliased_symbols.update({key_alias: val_alias, val_alias: key_alias})


        # Rotations & Reflections
        symbol_map = {}
        for symbol in base_symbols:
            symbol_map.update(symbol_schema(symbol))
            # Rotations
            if symbol in recipes['rotate4_symmetries']:
                symbol_map[symbol].append(recipe_schema('oRotate_cw', symbol))
                symbol_map[symbol].append(recipe_schema('oRotate_ccw', symbol))

                if symbol in recipes['horizontal_symmetries']:
                    symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol))
                    symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol))
                elif symbol in recipes['vertical_symmetries']:
                    raise ValueError('Atypical symmetry - manual map generation required')
                else: #Not present in vanilla game
                    symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                    symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol+'01'))
            else:
                symbol_map.update(symbol_schema(symbol+'1'))
                symbol_map[symbol].append(recipe_schema('oRotate_ccw', symbol+'1'))
                symbol_map[symbol+'1'].append(recipe_schema('oRotate_cw', symbol))

                if symbol in aliased_symbols: #Special treatment
                    symbol_map[symbol].append(recipe_schema('oRotate_cw', aliased_symbols[symbol]+'1'))
                    symbol_map[symbol+'1'].append(recipe_schema('oRotate_ccw', aliased_symbols[symbol]))

                    if symbol in recipes['horizontal_symmetries']: #Not present in vanilla game
                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))

                        symbol_map[symbol].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'1'))
                    elif symbol in recipes['vertical_symmetries']:
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))

                        symbol_map[symbol].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]+'1'))
                    else:
                        symbol_map.update(symbol_schema(symbol+'01'))
                        symbol_map.update(symbol_schema(symbol+'11'))

                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_cw', aliased_symbols[symbol]+'11'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_ccw', aliased_symbols[symbol]+'01'))

                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]+'01'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'11'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))

                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'1'))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                        
                elif symbol in recipes['rotate2_symmetries']:
                    symbol_map[symbol].append(recipe_schema('oRotate_cw', symbol+'1'))
                    symbol_map[symbol+'1'].append(recipe_schema('oRotate_ccw', symbol))
                        
                    if symbol in recipes['horizontal_symmetries']: #8 is included in horizontal_symmetries but not vertical_symmetries
                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    else:
                        symbol_map.update(symbol_schema(symbol+'01'))
                        symbol_map.update(symbol_schema(symbol+'11'))

                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_cw', symbol+'11'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_ccw', symbol+'01'))

                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol+'01'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'11'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))

                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_hor', symbol+'1'))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                        
                else:
                    symbol_map.update(symbol_schema(symbol+'2'))
                    symbol_map.update(symbol_schema(symbol+'3'))

                    symbol_map[symbol].append(recipe_schema('oRotate_cw', symbol+'3'))
                    symbol_map[symbol+'1'].append(recipe_schema('oRotate_ccw', symbol+'2'))
                    symbol_map[symbol+'2'].append(recipe_schema('oRotate_cw', symbol+'1'))
                    symbol_map[symbol+'2'].append(recipe_schema('oRotate_ccw', symbol+'3'))
                    symbol_map[symbol+'3'].append(recipe_schema('oRotate_cw', symbol+'2'))
                    symbol_map[symbol+'3'].append(recipe_schema('oRotate_ccw', symbol))
                    
                    if symbol in recipes['horizontal_symmetries']:
                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol+'2'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'3'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_hor', symbol+'2'))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'1'))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'3'))
                    elif symbol in recipes['vertical_symmetries']:
                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol+'2'))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'3'))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_vert', symbol+'2'))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'3'))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    else:
                        symbol_map.update(symbol_schema(symbol+'01'))
                        symbol_map.update(symbol_schema(symbol+'11'))
                        symbol_map.update(symbol_schema(symbol+'21'))
                        symbol_map.update(symbol_schema(symbol+'31'))

                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_cw', symbol+'31'))
                        symbol_map[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                        symbol_map[symbol+'11'].append(recipe_schema('oRotate_ccw', symbol+'21'))
                        symbol_map[symbol+'21'].append(recipe_schema('oRotate_cw', symbol+'11'))
                        symbol_map[symbol+'21'].append(recipe_schema('oRotate_ccw', symbol+'31'))
                        symbol_map[symbol+'31'].append(recipe_schema('oRotate_cw', symbol+'21'))
                        symbol_map[symbol+'31'].append(recipe_schema('oRotate_ccw', symbol+'01'))

                        symbol_map[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                        symbol_map[symbol].append(recipe_schema('oReflect_vert', symbol+'21'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'31'))
                        symbol_map[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_hor', symbol+'21'))
                        symbol_map[symbol+'2'].append(recipe_schema('oReflect_vert', symbol+'01'))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'11'))
                        symbol_map[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'31'))

                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                        symbol_map[symbol+'01'].append(recipe_schema('oReflect_vert', symbol+'2'))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_hor', symbol+'3'))
                        symbol_map[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                        symbol_map[symbol+'21'].append(recipe_schema('oReflect_hor', symbol+'2'))
                        symbol_map[symbol+'21'].append(recipe_schema('oReflect_vert', symbol))
                        symbol_map[symbol+'31'].append(recipe_schema('oReflect_hor', symbol+'1'))
                        symbol_map[symbol+'31'].append(recipe_schema('oReflect_vert', symbol+'3'))
        
        # I Factory
        for val in recipes['oIFactory']:
            symbol_map[val].append(recipe_schema('oIFactory', []))

        # Merges & Bends (not including mathematical expressions)
        for building in ['oMerger2', 'oMerger3', 'oMerger4', 'oBend']:
            for key,val in recipes[building].items():
                output_symbol = val.strip('_') # underscore indicates secret recipe - not relevant to calculations
                input_symbols = key.split()

                symbol_map[output_symbol].append(recipe_schema(building, input_symbols))

        # Subtraction
        for i in range(0, 9+1):
            for j in range(0, i+1):
                symbol_map[str(i-j)].append(recipe_schema('oMerger2', [str(i), str(j), 'I1']))

        # Addition
        for i in range(0, 9+1):
            for j in range(0, min(i, 9-i)+1):
                symbol_map[str(i+j)].append(recipe_schema('oMerger2', [str(i), str(j), '+']))
                symbol_map[str(i+j)].append(recipe_schema('oMerger2', [str(i), str(j)]))
                for k in range(0, min(i, j, 9-i-j)+1):
                    symbol_map[str(i+j+k)].append(recipe_schema('oMerger3', [str(i), str(j), str(k)]))
                    for l in range(0, min(i, j, k, 9-i-j-k)+1):
                        symbol_map[str(i+j+k+l)].append(recipe_schema('oMerger4', [str(i), str(j), str(k), str(l)]))

        self.base_symbol_map = symbols
        with open(self.symbol_map_yaml, 'w') as file:
            yaml.dump(symbols, file, default_flow_style=False)

    # Find what symbols are required to create other symbols
    def calc_dependent_symbols(self):
        dependency_map = {symbol:[] for symbol in self.base_symbol_map}
        for input_symbol in self.base_symbol_map:
            symbol_distance = optimize_all_symbols(optimized_metric='basic_factories', banned_symbols=[input_symbol], print_process=False)
            for dest_symbol in self.base_symbol_map:
                if (dest_symbol != input_symbol) & (dest_symbol not in symbol_distance):
                    dependency_map[dest_symbol].append(input_symbol)

        self.base_dependency_map = dependency_map
        with open(self.dependency_map_yaml, 'w') as file:
            yaml.dump(dependency_map, file, default_flow_style=False)

    # Simplify each reach to only include of a list of the necessary input symbols, and remove redundant/useless recipes
    def simplify_recipes(self, symbol_map, dependency_map, banned_symbols=[], banned_factories=[]):
        output_symbol_map = {}
        for symbol in [symbol for symbol in symbol_map if symbol not in banned_symbols]:
            supersets = []
            for recipe in symbol_map[symbol]:
                if recipe['factory'] not in banned_factories:
                    add_recipe = True
                    for recipe_symbol in recipe['input_symbols']:
                        if (recipe_symbol == symbol) or ((dependency_map is not None) and (symbol in dependency_map[recipe_symbol])):
                            add_recipe = False

                    if add_recipe:
                        supersets.append(set(recipe['input_symbols']))

            supersets.sort(key=len)
            subsets = []
            while supersets != []:
                curr = supersets[0]
                subsets.append(curr)
                supersets = [x for x in supersets[1:] if not curr <= x]

            output_symbol_map[symbol] = [list(subset) for subset in subsets]

        return output_symbol_map

    # Create a list of "free symbols" by seeing what required symbols can be created only using other required symbols. Remove these "free symbols" from the recipes in symbol_map
    def prune_symbol_map(self, symbol_map, dependency_map, required_symbols, free_symbols):
        free_symbols = []

        free_symbol_found = True
        while(free_symbol_found):
            free_symbol_found = False
            for required_symbol in required_symbols:
                if (required_symbol not in free_symbols) and ([] in symbol_map[required_symbol]):
                    free_symbol_found = True
                    free_symbols.append(required_symbol)

                    for symbol in symbol_map:
                        for recipe in symbol_map[symbol]:
                            if required_symbol in recipe:
                                recipe.remove(required_symbol)

        # Add all dependent symbols before pruning the recipes
        for symbol in symbol_map:
            supersets = []
            for recipe in symbol_map[symbol]:
                supersets.append(set(recipe))
                for recipe_symbol in recipe:
                    supersets[-1] |= set(dependency_map[recipe_symbol])

            supersets.sort(key=len)
            subsets = []
            while supersets != []:
                curr = supersets[0]
                subsets.append(curr)
                supersets = [x for x in supersets[1:] if not curr <= x]
            
            # Remove redundant dependent symbols from the recipe
            for subset in subsets:
                for subset_symbol in copy.copy(subset):
                    subset -= set(dependency_map[subset_symbol])
            subsets = [list(subset) for subset in subsets]

            symbol_map[symbol] = subsets

        return symbol_map, free_symbols

    # Optimize number of factories for all symbols given certain restrictions
    def optimize_all_symbols(self, optimized_metric='cycles', banned_symbols=[], banned_factories=[], print_process=True, max_factories=9999):
        symbol_map = copy.deepcopy(self.adjusted_symbol_map)
        dependency_map = copy.deepcopy(self.adjusted_dependency_map)

        formulas = None
        allowed_symbols = [symbol for symbol in symbol_map if symbol not in banned_symbols] #preserving order important so that 'word' is checked last if it exists

        symbol_distance = {}
        symbols_to_reach = {}
        symbol_found = True
        if optimized_metric == 'cycles': # optimizing number of factories while maintaining minimum cycles
            step = 1
            while True:
                if print_process: print(f'Step {step} of BFS')

                symbol_found = False
                # Perform a BFS on number of factories to reach each symbol
                for symbol in [symbol for symbol in allowed_symbols if symbol not in symbol_distance]:
                    if symbol == 'word':
                        for symbol_to_reach, recipe in symbols_to_reach.items():
                            if print_process: print(f'Adding symbol {symbol_to_reach}')
                            symbol_distance[symbol_to_reach] = {'distance': step, 'recipe': recipe}

                    for recipe in symbol_map[symbol]:
                        if (recipe['factory'] not in banned_factories) and (not (set(recipe['input_symbols']) - set(symbol_distance.keys()))):
                            symbol_found = True
                            recipe_distance = sum([symbol_distance[recipe_symbol]['distance'] for recipe_symbol in recipe['input_symbols']]) + 1
                            if symbol == 'word':
                                recipe_distance -= 1 # Solving doesn't cost anything

                            if recipe_distance == step:
                                if symbol in symbols_to_reach:
                                    symbols_to_reach[symbol].append(recipe)
                                else:
                                    symbols_to_reach[symbol] = [recipe]
                for symbol, recipe in symbols_to_reach.items():
                    if print_process: print(f'Adding symbol {symbol}')
                    symbol_distance[symbol] = {'distance': step, 'recipe': recipe}

                if print_process:
                    if symbols_to_reach:
                        print('')
                    else:
                        print('No symbols reached this step\n')

                step += 1
                symbols_to_reach = {}

                if (not symbol_found) or not (set(symbol_map.keys()) - set(banned_symbols) - set(symbol_distance.keys())) or (step>max_factories):
                    break

        elif optimized_metric == 'basic_factories': # quick & potentially incomplete optimization of number of factories
            step = 1
            while True:
                if print_process: print(f'Step {step} of BFS')

                symbol_found = False
                # Perform a BFS on number of factories to reach each symbol
                for symbol in [symbol for symbol in allowed_symbols if symbol not in symbol_distance]:
                    if symbol == 'word':
                        for symbol_to_reach, recipe in symbols_to_reach.items():
                            if print_process: print(f'Adding symbol {symbol_to_reach}')
                            symbol_distance[symbol_to_reach] = {'distance': step, 'recipe': recipe}

                    for recipe in symbol_map[symbol]:
                        if (recipe['factory'] not in banned_factories) and (not (set(recipe['input_symbols']) - set(symbol_distance.keys()))):
                            symbol_found = True

                            required_symbols = OrderedSet(recipe['input_symbols'])
                            tallied_symbols = OrderedSet([symbol])

                            while required_symbols - tallied_symbols:
                                next_symbol = (required_symbols-tallied_symbols)[0]
                                tallied_symbols.add(next_symbol)
                                required_symbols.update(symbol_distance[next_symbol]['recipe'][0]['input_symbols']) #Just using first result

                            recipe_distance = len(tallied_symbols)
                            if symbol == 'word':
                                recipe_distance -= 1 # Solving doesn't cost anything
                            
                            # Only combining symbols from previous step
                            # recipe_distance = sum([symbol_distance[recipe_symbol]['distance'] for recipe_symbol in set(recipe['input_symbols'])]) + 1
                            if recipe_distance == step:
                                if symbol in symbols_to_reach:
                                    #symbols_to_reach[symbol].append(recipe)
                                    pass
                                else:
                                    symbols_to_reach[symbol] = [recipe]
                for symbol_to_reach, recipe in symbols_to_reach.items():
                    if print_process: print(f'Adding symbol {symbol_to_reach}')
                    symbol_distance[symbol_to_reach] = {'distance': step, 'recipe': recipe}

                if print_process:
                    if symbols_to_reach:
                        print('')
                    else:
                        print('No symbols reached this step\n')

                step += 1
                symbols_to_reach = {}
                
                if (not symbol_found) or not (set(symbol_map.keys()) - set(banned_symbols) - set(symbol_distance.keys())) or (step>max_factories):
                    break

        elif optimized_metric == 'exhaustive_factories': # guaranteed minimum number of factories
            symbol_map = self.simplify_recipes(symbol_map, dependency_map, banned_symbols, banned_factories)

            required_symbols = dependency_map['word']
            free_symbols = []
            one_step_symbols = []

            symbol_map, free_symbols = self.prune_symbol_map(symbol_map, dependency_map, required_symbols, free_symbols)
            print(f'Required symbols: {required_symbols}')
            print(f'"Free symbols": {free_symbols}')

            step = 1
            print('')
            while True:
                print(f'\rStep {step} of search\t\t\t\t\t\t\t\t')

                symbol_found = False
                # Perform a BFS on number of factories to reach each symbol
                for symbol_num, symbol in enumerate(allowed_symbols): #preserve symbol 
                    if symbol == 'word':
                        for symbol_to_reach, symbol_sets in symbols_to_reach.items():
                            symbol_distance[symbol_to_reach] = symbol_sets
                        symbols_to_reach = {}

                    sys.stdout.write(f"\rCompleted {symbol_num}/{len(set(symbol_map.keys()) - set(banned_symbols))} symbols - Currently calculating {symbol}\t\t\t")
                    for recipe in symbol_map[symbol]:
                        if not (set(recipe) - set(symbol_distance.keys())):
                            symbol_found = True

                            if len(recipe) == 0:
                                if step == 1:
                                    symbols_to_reach[symbol] = [set()]

                            elif len(recipe) == 1:
                                input_symbol = recipe[0]

                                supersets = [formula | {input_symbol} for formula in symbol_distance[input_symbol]]
                                if symbol in symbol_distance:
                                    supersets += symbol_distance[symbol]
                                if symbol in symbols_to_reach:
                                    supersets += symbols_to_reach[symbol]

                                supersets.sort(key=len)
                                if set() not in supersets:
                                    subsets = []
                                    while supersets != []:
                                        curr = supersets[0]
                                        subsets.append(curr)
                                        supersets = [x for x in supersets[1:] if not curr <= x]

                                    if subsets:
                                        symbols_to_reach[symbol] = subsets

                            else:
                                #TODO Potential optimization: keep track of what symbols changed last loop - no need to recalculate with the same inputs
                                input_symbol_formulas = []
                                for input_symbol in recipe:
                                    input_symbol_formulas.append([formula | {input_symbol} for formula in symbol_distance[input_symbol]])


                                subsets = input_symbol_formulas[0]
                                for i in range(1, len(input_symbol_formulas)):
                                    is_last_loop = (i == len(input_symbol_formulas)-1)
                                    cross_product = [el for el in itertools.product(subsets, input_symbol_formulas[i])]
                                    reduced_product = [reduce(lambda x,y:x|y, tup, set()) for tup in cross_product]

                                    #TODO Test with simple for loops instead of list comprehensions
                                    #reduced_product = []
                                    #for tup in cross_product:
                                    #    reduced_product.append(reduce(lambda x,y:x|y, tup, set()))

                                    if symbol == 'word':
                                        supersets = [product for product in reduced_product if len(product)<=step] # No factory required to combine symbols into the solution word
                                    else:
                                        supersets = [product for product in reduced_product if len(product)+1<=step]

                                    # Removing any sets already larger than sets in symbol_distance
                                    if symbol in symbol_distance:
                                        for curr in symbol_distance[symbol]:
                                            supersets = [x for x in supersets if not curr <= x]

                                        if is_last_loop:
                                            supersets += symbol_distance[symbol]

                                    # Removing any sets already larger than sets in symbols_to_reach
                                    if symbol in symbols_to_reach:
                                        for curr in symbols_to_reach[symbol]:
                                            supersets = [x for x in supersets if not curr <= x]

                                        if is_last_loop:
                                            supersets += symbols_to_reach[symbol]

                                    supersets.sort(key=len)
                                    if set() not in supersets:
                                        subsets = []
                                        while supersets != []:
                                            curr = supersets[0]
                                            subsets.append(curr)
                                            supersets = [x for x in supersets[1:] if not curr <= x]

                                        if subsets:
                                            if is_last_loop:
                                                symbols_to_reach[symbol] = subsets

                for symbol_to_reach, symbol_sets in symbols_to_reach.items():
                    symbol_distance[symbol_to_reach] = symbol_sets
                symbols_to_reach = {}
                step += 1
                
                if ('word' in symbol_distance) or (not symbol_found) or not (set(allowed_symbols) - set(symbol_distance.keys())) or (step>max_factories):
                    break
        

        if print_process:
            if symbol_found:
                print(f'All symbols are possible with these constraints\n')
            else:
                print(f"Impossible symbols: {[symbol for symbol in symbol_map if symbol not in (banned_symbols+[*symbol_distance])]}\n")
                print(f"Impossible base symbols: {[symbol for symbol in symbol_map if (symbol not in (banned_symbols+[*symbol_distance])) and ((len(symbol)==1) or symbol=='word')]}\n")
            if ('word' in symbol_map) and ('word' not in symbol_distance):
                print(f"Could not create chosen word")
                    

            for key, val in symbol_distance.items():
                if (len(key)==1) or (key == 'word'):
                    print(f'{key} : {val}')

        if optimized_metric == 'exhaustive_factories':
            return symbol_distance, free_symbols
        else:
            return symbol_distance

    # Optimize number of factories for a word given certain restrictions
    def optimize_word(self, word, optimized_metric='cycles', banned_symbols=[], banned_factories=[]):
        if isinstance(word, str):
            symbol_list = [letter for letter in word]
        elif isinstance(word, list):
            symbol_list = word
        else:
            raise ValueError(f'Invalid type for word {word} - require string or list')

        self.adjusted_symbol_map = copy.deepcopy(self.base_symbol_map)
        self.adjusted_symbol_map['word'] = [recipe_schema('solve', symbol_list)]

        #TODO when symbols or factories are banned, the dependency map can be recalculated to potentially give more dependencies
        self.adjusted_dependency_map = copy.deepcopy(self.base_dependency_map)
        self.adjusted_dependency_map['word'] = []
        for symbol in symbol_list:
            if symbol not in self.adjusted_dependency_map['word']:
                self.adjusted_dependency_map['word'].append(symbol)
            for dependent_symbol in self.adjusted_dependency_map[symbol]:
                if dependent_symbol not in self.adjusted_dependency_map['word']:
                    self.adjusted_dependency_map['word'].append(dependent_symbol)


        if optimized_metric in ['cycles', 'basic_factories']:
            all_formulas = self.optimize_all_symbols(optimized_metric, banned_symbols, banned_factories, print_process=False)

            if 'word' in all_formulas:
                # Printing results
                printed_symbols = set()
                symbols_to_print = ['word']
                while symbols_to_print:
                    key = symbols_to_print[0]
                    val = all_formulas[key]
                    symbols_to_print.remove(key)
                    symbols_to_print.extend(val['recipe'][0]['input_symbols'])

                    if key == 'word':
                        symbol = word
                    else:
                        symbol = key

                    if symbol not in printed_symbols:
                        print(f'{symbol} : {val}')
                    printed_symbols.add(key)
            else:
                print(f'{word} is not possible to create with these restrictions')

        elif optimized_metric == 'exhaustive_factories':
            all_formulas_naive = self.optimize_all_symbols('basic_factories', banned_symbols, banned_factories, print_process=False)
            if 'word' in all_formulas_naive:
                prelim_distance = all_formulas_naive['word']['distance']
                print(f'\n{word} upper bound for required factories: {prelim_distance}')
                all_formulas, free_symbols = self.optimize_all_symbols('exhaustive_factories', banned_symbols, banned_factories, print_process=False, max_factories=prelim_distance)

                min_factories = min(len(symbol_set) for symbol_set in all_formulas['word']) + len(free_symbols)
                solutions = [symbol_set | set(free_symbols) for symbol_set in all_formulas['word']]
                print(f'\n\n{word} minimum factories: {min_factories}')

                symbol_dependencies = []
                solution_formulas = []
                for i, solution in enumerate(solutions):
                    print(f'\nSolution {i+1} of {len(solutions)}')

                    symbol_dependencies.append({word: [solution]})
                    for symbol in solution:
                        if symbol in free_symbols:
                            symbol_dependencies[i][symbol] = [set(free_symbols[:free_symbols.index(symbol)])]
                        else:
                            symbol_dependencies[i][symbol] = [symbol_set | set(free_symbols) for symbol_set in all_formulas[symbol] if not (symbol_set-set(solution))]
                    # Sorting by number of symbol dependencies in solution
                    symbol_dependencies[i] = dict(sorted(symbol_dependencies[i].items(), key=lambda items: len(items[1][0]), reverse=True))
                        
                    solution_formulas.append({})
                    for symbol in symbol_dependencies[i]:
                        solution_formulas[i][symbol] = []
                        if symbol == word:
                            solution_formulas[i][symbol].append(self.adjusted_symbol_map['word'])
                        else:
                            for recipe in self.base_symbol_map[symbol]:
                                recipe_added = False
                                for symbol_dependency_case in symbol_dependencies[i][symbol]:
                                    if (recipe['factory'] not in banned_factories) and not (set(recipe['input_symbols']) - set(symbol_dependency_case)):
                                        if not recipe_added:
                                            solution_formulas[i][symbol].append(recipe)
                                            recipe_added = True

                    #for key, val in symbol_dependencies[i].items():
                    #    print(f'{key} : {val}')
                    for key, val in solution_formulas[i].items():
                        print(f'{key} : {val}')
            else:
                print(f'{word} is not possible to create with these restrictions')
        else:
            print(f'Unsupported optimization metric: {optimized_metric}')
            all_formulas = None

        return all_formulas

if __name__ == '__main__':
    factory_names = factory_names = ['oMerger2', 'oMerger3', 'oMerger4', 'oBend', 'oReflect_hor', 'oReflect_hor', 'oRotate_cw', 'oRotate_ccw', 'oIFactory']

    #TODO Read from argparse
    recipes_json = 'recipes.json'
    symbol_map_yaml = 'symbol_map.yaml'
    dependency_map_yaml = 'dependency_map.yaml'

    word_calc_obj = word_factori_calc(recipes_json, symbol_map_yaml, dependency_map_yaml)
    #word_calc_obj.recalculate_symbol_maps() #TODO Determine when to do this based on input from args

    #word = '314159'
    #word = '$T@RG@RD3N'
    word = 'CLEFT'

    #optimized_metric = 'cycles'
    #optimized_metric = 'basic_factories'
    optimized_metric = 'exhaustive_factories'
    while True:
        all_formulas = word_calc_obj.optimize_word(word, optimized_metric=optimized_metric)
        import pdb; pdb.set_trace()
