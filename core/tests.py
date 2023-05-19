from fuzzywuzzy import fuzz

list_ = [{'pk': 2, 'name': 'Medicine 2'},
         {'pk': 6, 'name': 'Medicine 6'},
         {'pk': 8, 'name': 'Medicine 8'},
         {'pk': 1, 'name': 'Medicine 1'},
         {'pk': 7, 'name': 'Medicine 7'},
         {'pk': 9, 'name': 'Medicine 9'},
         {'pk': 3, 'name': 'Medicine 3'},
         {'pk': 4, 'name': 'Medicine 4'},
         {'pk': 5, 'name': 'Medicine 5'},
         {'pk': 10, 'name': 'Medicine 10'}]
similar_words = [word['pk'] for word in list_ if fuzz.ratio('Med 1', word['name']) > 65]
print(similar_words)