from pathlib import Path
from symspellpy import SymSpell, Verbosity

dict_path = Path(__file__).resolve().parent.parent / "assets" / "frequency_dictionary_en_82_765.txt"
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
sym_spell.load_dictionary(str(dict_path), 0, 1)
word="ceertain conditinaas durring seveal ggeneratioons aree modiffied in thhe sae maner"

suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=1)
if suggestions:
    print(suggestions[0])
else:
    print("No suggestions")
