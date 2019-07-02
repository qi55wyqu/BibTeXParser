import re
import os
from BibtexEntry import BibtexEntry


class BibtexParser:
    def __init__(self):
        self.entries = []
        # maybe space then @ then type then maybe space then { then maybe space then key then maybe space then ,
        self.regex_type_key = re.compile(r'\s?@(?P<type>(.*?))\s?{\s?(?P<key>(.*?))\s?,')
        # maybe space then field then maybe space then = then maybe space then content then maybe space then }
        # $ means: ends with
        self.regex_field_content = re.compile(r'\s?(?P<field>(.*?))\s?=\s?{\s?(?P<content>(.*?))\s?}$')

    def parse(self, filename, append=False):
        assert os.path.isfile(filename)
        if not append:
            self.entries = []
        file = open(filename, 'r')
        opening_brackets, closing_brackets = 0, 0
        entry = ''
        while True:
            line = file.readline()
            if not line: break
            if line == '\n': continue
            entry += line
            for _ in re.finditer('{', line):
                opening_brackets += 1
            for _ in re.finditer('}', line):
                closing_brackets += 1
            if opening_brackets == closing_brackets:
                entry = entry.replace('\n', '')
                if entry[-1] == '}':
                    entry = entry[:-1]
                e = self.regex_type_key.search(entry)
                if not e: continue
                e_dict = e.groupdict()
                bibtexEntry = BibtexEntry(key=e_dict['key'], entryType=e_dict['type'])
                entry = entry[e.end():]
                entry_split = []
                idx_prev = 0
                opened, closed = 0, 0
                for i, char in enumerate(entry):
                    if char == '{':
                        opened +=1
                    elif char == '}':
                        closed += 1
                    if opened > 0 and opened == closed:
                        entry_split.append(entry[idx_prev:i+1])
                        idx_prev = i + 2
                        opened, closed = 0, 0
                for e in entry_split:
                    field = self.regex_field_content.search(e)
                    if field:
                        dict = field.groupdict()
                        bibtexEntry.set_field(dict['field'], dict['content'])
                self.entries.append(bibtexEntry)
                entry = ''
                opening_brackets, closing_brackets = 0, 0
        file.close()

    def write(self, filename, pretty_print=True, append=False):
        with open(filename, 'a+' if append else 'w+') as file:
            for entry in self.entries:
                output = ''
                output += '@' + entry.type + '{' + entry.key + ',\n'
                num_spaces = 0
                if pretty_print:
                    for field in entry.fields:
                        if len(field) > num_spaces:
                            num_spaces = len(field)
                for i, (field, content) in enumerate(zip(entry.fields, entry.contents)):
                    output += ' ' * 4 + field
                    if pretty_print:
                        output += ' ' * (num_spaces-len(field))
                    output += ' = ' + '{' + content + '}'
                    if i < len(entry.fields) - 1:
                        output += ','
                    output += '\n'
                output += '}\n\n'
                file.write(output)

    def get_all_keys(self):
        return [entry.key for entry in self.entries]

    def get_entry(self, key):
        keys = self.get_all_keys()
        return self.entries[keys.index(key)] if key in keys else None

    def set_order_of_fields(self, order, keys=None):
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.set_order_of_fields(order)

    def set_field_last(self, field):
        for entry in self.entries:
            entry.set_field_last(field)

    def use_field_in_field_as_href(self, from_field='url', to_field='title', keys=None, remove_from_field=True):
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.use_field_in_field_as_href(from_field, to_field, remove_from_field)

    def use_url_in_title_as_href(self):
        self.use_field_in_field_as_href(from_field='url', to_field='title', keys=None, remove_from_field=True)

    def use_href_from_title_as_url(self, keys=None):
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.use_href_from_title_as_url()