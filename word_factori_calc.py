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

# Convert recipe json file (unicode already changed) into a more useable mapping file that gives all recipes for a given letter
def create_map(input_recipes_json, output_symbol_map_yaml):
    with open(input_recipes_json, 'r') as file:
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
    symbols = {}
    for symbol in base_symbols:
        symbols.update(symbol_schema(symbol))
        # Rotations
        if symbol in recipes['rotate4_symmetries']:
            symbols[symbol].append(recipe_schema('oRotate_cw', symbol))
            symbols[symbol].append(recipe_schema('oRotate_ccw', symbol))

            if symbol in recipes['horizontal_symmetries']:
                symbols[symbol].append(recipe_schema('oReflect_hor', symbol))
                symbols[symbol].append(recipe_schema('oReflect_vert', symbol))
            elif symbol in recipes['vertical_symmetries']:
                raise ValueError('Atypical symmetry - manual map generation required')
            else: #Not present in vanilla game
                symbols[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                symbols[symbol].append(recipe_schema('oReflect_vert', symbol+'01'))
        else:
            symbols.update(symbol_schema(symbol+'1'))
            symbols[symbol].append(recipe_schema('oRotate_ccw', symbol+'1'))
            symbols[symbol+'1'].append(recipe_schema('oRotate_cw', symbol))

            if symbol in aliased_symbols: #Special treatment
                symbols[symbol].append(recipe_schema('oRotate_cw', aliased_symbols[symbol]+'1'))
                symbols[symbol+'1'].append(recipe_schema('oRotate_ccw', aliased_symbols[symbol]))

                if symbol in recipes['horizontal_symmetries']: #Not present in vanilla game
                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))

                    symbols[symbol].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'1'))
                elif symbol in recipes['vertical_symmetries']:
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))

                    symbols[symbol].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]+'1'))
                else:
                    symbols.update(symbol_schema(symbol+'01'))
                    symbols.update(symbol_schema(symbol+'11'))

                    symbols[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                    symbols[symbol+'01'].append(recipe_schema('oRotate_cw', aliased_symbols[symbol]+'11'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_ccw', aliased_symbols[symbol]+'01'))

                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                    symbols[symbol].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]+'01'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'11'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))

                    symbols[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol+'01'].append(recipe_schema('oReflect_vert', aliased_symbols[symbol]))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_hor', aliased_symbols[symbol]+'1'))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    
            elif symbol in recipes['rotate2_symmetries']:
                symbols[symbol].append(recipe_schema('oRotate_cw', symbol+'1'))
                symbols[symbol+'1'].append(recipe_schema('oRotate_ccw', symbol))
                    
                if symbol in recipes['horizontal_symmetries']: #8 is included in horizontal_symmetries but not vertical_symmetries
                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))
                else:
                    symbols.update(symbol_schema(symbol+'01'))
                    symbols.update(symbol_schema(symbol+'11'))

                    symbols[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                    symbols[symbol+'01'].append(recipe_schema('oRotate_cw', symbol+'11'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_ccw', symbol+'01'))

                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol+'01'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'11'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))

                    symbols[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol+'01'].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_hor', symbol+'1'))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    
            else:
                symbols.update(symbol_schema(symbol+'2'))
                symbols.update(symbol_schema(symbol+'3'))

                symbols[symbol].append(recipe_schema('oRotate_cw', symbol+'3'))
                symbols[symbol+'1'].append(recipe_schema('oRotate_ccw', symbol+'2'))
                symbols[symbol+'2'].append(recipe_schema('oRotate_cw', symbol+'1'))
                symbols[symbol+'2'].append(recipe_schema('oRotate_ccw', symbol+'3'))
                symbols[symbol+'3'].append(recipe_schema('oRotate_cw', symbol+'2'))
                symbols[symbol+'3'].append(recipe_schema('oRotate_ccw', symbol))
                
                if symbol in recipes['horizontal_symmetries']:
                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol+'2'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'3'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_hor', symbol+'2'))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'1'))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'3'))
                elif symbol in recipes['vertical_symmetries']:
                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol+'2'))
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'1'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'3'))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_vert', symbol+'2'))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'3'))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'1'))
                else:
                    symbols.update(symbol_schema(symbol+'01'))
                    symbols.update(symbol_schema(symbol+'11'))
                    symbols.update(symbol_schema(symbol+'21'))
                    symbols.update(symbol_schema(symbol+'31'))

                    symbols[symbol+'01'].append(recipe_schema('oRotate_cw', symbol+'31'))
                    symbols[symbol+'01'].append(recipe_schema('oRotate_ccw', symbol+'11'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_cw', symbol+'01'))
                    symbols[symbol+'11'].append(recipe_schema('oRotate_ccw', symbol+'21'))
                    symbols[symbol+'21'].append(recipe_schema('oRotate_cw', symbol+'11'))
                    symbols[symbol+'21'].append(recipe_schema('oRotate_ccw', symbol+'31'))
                    symbols[symbol+'31'].append(recipe_schema('oRotate_cw', symbol+'21'))
                    symbols[symbol+'31'].append(recipe_schema('oRotate_ccw', symbol+'01'))

                    symbols[symbol].append(recipe_schema('oReflect_hor', symbol+'01'))
                    symbols[symbol].append(recipe_schema('oReflect_vert', symbol+'21'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_hor', symbol+'31'))
                    symbols[symbol+'1'].append(recipe_schema('oReflect_vert', symbol+'11'))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_hor', symbol+'21'))
                    symbols[symbol+'2'].append(recipe_schema('oReflect_vert', symbol+'01'))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_hor', symbol+'11'))
                    symbols[symbol+'3'].append(recipe_schema('oReflect_vert', symbol+'31'))

                    symbols[symbol+'01'].append(recipe_schema('oReflect_hor', symbol))
                    symbols[symbol+'01'].append(recipe_schema('oReflect_vert', symbol+'2'))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_hor', symbol+'3'))
                    symbols[symbol+'11'].append(recipe_schema('oReflect_vert', symbol+'1'))
                    symbols[symbol+'21'].append(recipe_schema('oReflect_hor', symbol+'2'))
                    symbols[symbol+'21'].append(recipe_schema('oReflect_vert', symbol))
                    symbols[symbol+'31'].append(recipe_schema('oReflect_hor', symbol+'1'))
                    symbols[symbol+'31'].append(recipe_schema('oReflect_vert', symbol+'3'))
    
    # I Factory
    for val in recipes['oIFactory']:
        symbols[val].append(recipe_schema('oIFactory', []))

    # Merges & Bends (not including mathematical expressions)
    for building in ['oMerger2', 'oMerger3', 'oMerger4', 'oBend']:
        for key,val in recipes[building].items():
            output_symbol = val.strip('_') # underscore indicates secret recipe - not relevant to calculations
            input_symbols = key.split()

            symbols[output_symbol].append(recipe_schema(building, input_symbols))

    # Subtraction
    for i in range(0, 9+1):
        for j in range(0, i+1):
            symbols[str(i-j)].append(recipe_schema('oMerger2', [str(i), str(j), 'I1']))

    # Addition
    for i in range(0, 9+1):
        for j in range(0, min(i, 9-i)+1):
            symbols[str(i+j)].append(recipe_schema('oMerger2', [str(i), str(j), '+']))
            symbols[str(i+j)].append(recipe_schema('oMerger2', [str(i), str(j)]))
            for k in range(0, min(i, j, 9-i-j)+1):
                symbols[str(i+j+k)].append(recipe_schema('oMerger3', [str(i), str(j), str(k)]))
                for l in range(0, min(i, j, k, 9-i-j-k)+1):
                    symbols[str(i+j+k+l)].append(recipe_schema('oMerger4', [str(i), str(j), str(k), str(l)]))
            

    #with open(output_symbol_map_json, 'w') as file:
    #    file.write(json.dumps(symbols, indent=2))
    with open(output_symbol_map_yaml, 'w') as file:
        yaml.dump(symbols, file, default_flow_style=False)

# Optimize number of factories for all symbols given certain restrictions
def optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_symbols=[], banned_factories=[], print_process=True, max_factories=9999):
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

            #test = [symbol for symbol in allowed_symbols if symbol not in symbol_distance]
            #import pdb; pdb.set_trace()


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
                    if (recipe['factory'] not in banned_factories) and (not (set(recipe['input_symbols']) - set(symbol_distance.keys()))):
                        symbol_found = True

                        input_symbols = list(set(recipe['input_symbols'])) # list of unique symbols used in recipe

                        if len(input_symbols) == 0:
                            if step == 1:
                                symbols_to_reach[symbol] = [set()]

                        elif len(input_symbols) == 1:
                            input_symbol = input_symbols[0]

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
                            for input_symbol in input_symbols:
                                input_symbol_formulas.append([formula | {input_symbol} for formula in symbol_distance[input_symbol]])


                            subsets = input_symbol_formulas[0]
                            for i in range(1, len(input_symbol_formulas)):
                                is_last_loop = (i == len(input_symbol_formulas)-1)
                                cross_product = [el for el in itertools.product(subsets, input_symbol_formulas[i])]
                                reduced_product = [reduce(lambda x,y:x|y, tup, set()) for tup in cross_product]

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

    return symbol_distance

# Optimize number of factories for a word given certain restrictions
def optimize_word(word, symbol_map, optimized_metric='cycles', banned_symbols=[], banned_factories=[]):
    if isinstance(word, str):
        symbol_list = [letter for letter in word]
    elif isinstance(word, list):
        symbol_list = word
    else:
        raise ValueError(f'Invalid type for word {word} - require string or list')

    adjusted_symbol_map = copy.deepcopy(symbol_map)
    adjusted_symbol_map['word'] = [recipe_schema('solve', symbol_list)]

    if optimized_metric in ['cycles', 'basic_factories']:
        all_formulas = optimize_all_symbols(adjusted_symbol_map, optimized_metric, banned_symbols, banned_factories, print_process=False)

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

    elif optimized_metric in ['exhaustive_factories']:
        all_formulas_naive = optimize_all_symbols(adjusted_symbol_map, 'basic_factories', banned_symbols, banned_factories, print_process=False)
        if 'word' in all_formulas_naive:
            prelim_distance = all_formulas_naive['word']['distance']
            print(f'\n{word} upper bound for required factories: {prelim_distance}')
            all_formulas = optimize_all_symbols(adjusted_symbol_map, 'exhaustive_factories', banned_symbols, banned_factories, print_process=False, max_factories=prelim_distance)

            min_factories = min(len(symbol_set) for symbol_set in all_formulas['word'])
            solutions = [symbol_set for symbol_set in all_formulas['word'] if len(symbol_set)==min_factories]
            print(f'\n\n{word} minimum factories: {min_factories}')

            symbol_dependencies = []
            solution_formulas = []
            for i, solution in enumerate(solutions):
                print(f'\nSolution {i+1} of {len(solutions)}')

                symbol_dependencies.append({word: [solution]})
                for symbol in solution:
                    symbol_dependencies[i][symbol] = [symbol_set for symbol_set in all_formulas[symbol] if not (symbol_set-set(solution))]
                # Sorting by number of symbol dependencies in solution
                symbol_dependencies[i] = dict(sorted(symbol_dependencies[i].items(), key=lambda items: len(items[1][0]), reverse=True))
                    
                solution_formulas.append({})
                for symbol in symbol_dependencies[i]:
                    solution_formulas[i][symbol] = []
                    if symbol == word:
                        solution_formulas[i][symbol].append(adjusted_symbol_map['word'])
                    else:
                        for recipe in symbol_map[symbol]:
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
    factory_names = ['oMerger2', 'oMerger3', 'oMerger4', 'oBend', 'oReflect_hor', 'oReflect_hor', 'oRotate_cw', 'oRotate_ccw', 'oIFactory']

    recipes_json = 'recipes.json'
    symbol_map_yaml = 'symbol_map.yaml'

    create_map(recipes_json, symbol_map_yaml)

    with open(symbol_map_yaml, 'r') as file:
        symbol_map = yaml.load(file, Loader=yaml.CLoader)


    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oMerger2'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oMerger3'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oMerger4'])

    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oBend'])

    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oReflect_hor'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oReflect_vert'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oReflect_hor', 'oReflect_vert'])

    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oRotate_cw'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oRotate_ccw'])
    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oRotate_cw', 'oRotate_ccw'])

    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles', banned_factories=['oIFactory'])

    #all_formulas = optimize_all_symbols(symbol_map, optimized_metric='cycles')

    #word = '314159'
    #word = '$T@RG@RD3N'
    word = 'TEDDY'

    #optimized_metric = 'cycles'
    #optimized_metric = 'basic_factories'
    optimized_metric = 'exhaustive_factories'
    while True:
        all_formulas = optimize_word(word, symbol_map, optimized_metric=optimized_metric)
        import pdb; pdb.set_trace()
