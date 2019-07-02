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
