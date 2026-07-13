from symspellpy import SymSpell, Verbosity
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
sym_spell.load_dictionary("/Users/sankalpomar/Documents/HomeLab/the-watcher/assets/frequency_dictionary_en_82_765.txt", 0, 1)
word="ceertain conditinaas durring seveal ggeneratioons aree modiffied in thhe sae maner"

suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=1)
if suggestions:
    print(suggestions[0])
else:
    print("No suggestions")
