# BibTeXParser

## Installation
```
pip install git+https://github.com/qi55wyqu/BibTeXParser.git
```

### Usage example: 

```python
import os
from BibtexParser import BibtexParser

input_filename = 'C:\\Users\\User\\Path\\To\\Your\\BibtexFile\\references.bib'
folder, filename = os.path.split(input_filename)
filename, ext = os.path.splitext(filename)
output_filename = os.path.join(folder, filename+'_edited'+ext)

bibtex = BibtexParser()
bibtex.parse(input_filename)
bibtex.use_field_in_field_as_href(from_field='url', to_field='title')
bibtex.set_order_of_fields(order=['author', 'title', 'journal', 'year'])
bibtex.set_field_last('abstract')
bibtex.fix_special_characters(only_if_url_or_href=True)
bibtex.sort_by_key()
bibtex.write(output_filename)

articles = bibtex.get_entries_with_type('article')
print(articles)
```