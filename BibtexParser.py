import re
import os
import subprocess
import platform
from BibtexEntry import BibtexEntry


class BibtexParser:
    def __init__(self, entries=None):
        self.entries = [] if entries is None else entries
        self.regex_type_key = re.compile(r'\s*@(?P<type>(.*?))\s*\{\s*(?P<key>(.*?))\s*,')
        self.regex_field_content = re.compile(r'^\s*(?P<field>(\w+))\s*=\s*\{(?P<content>(.*))\}')
        self.get_citation = re.compile(r'(?<!\\)%.*|(\\(?:no)?cite\w*\{(?P<keys>((?!\*)[^{}]+))\})')
        self.current_iter = 0

    def parse(self, filename: str, append=False):
        assert os.path.isfile(filename)
        if not append:
            self.entries = []
        file = open(filename, 'r', encoding='utf8')
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

    def write(self, filename: str, pretty_print=True, append=False):
        with open(filename, 'a+' if append else 'w+', encoding='utf8') as file:
            for entry in self.entries:
                output = ''
                output += '@' + entry.type + '{' + entry.key + ',\n'
                num_spaces = 0
                if pretty_print:
                    for field in entry.fields:
                        if len(field) > num_spaces:
                            num_spaces = len(field)
                for i, field in enumerate(entry.fields):
                    output += ' ' * 4 + field
                    if pretty_print:
                        output += ' ' * (num_spaces-len(field))
                    output += ' = ' + '{' + entry.fields[field] + '}'
                    if i < len(entry) - 1:
                        output += ','
                    output += '\n'
                output += '}\n\n'
                file.write(output)

    def append_entries(self, entries):
        self.entries += entries

    def add_entries(self, entries, replace=True):
        if not replace:
            self.append_entries(entries)
        else:
            keys = self.get_all_keys()
            for entry in entries:
                if entry.key in keys:
                    self.entries[keys.index(entry.key)] = entry
                else:
                    self.entries.append(entry)

    def append_entry(self, entry):
        self.entries += [entry]

    def add_endtry(self, entry, replace=True):
        self.add_entries([entry], replace)

    def __str__(self):
        str = ''
        for entry in self.entries:
            str += entry.__str__() + '\n'
        return str

    def __name__(self):
        return 'BibtexParser'

    def __add__(self, other):
        entries = self.entries.copy()
        bibtex = BibtexParser(entries)
        if isinstance(other, BibtexEntry):
            bibtex.add_endtry(other, replace=False)
        elif isinstance(other, BibtexParser):
            for entry in other:
                bibtex.append_entry(entry)
        else:
            raise ValueError('added object must be BibtexEntry or BibtexParser')
        return bibtex

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        if isinstance(other, BibtexEntry):
            self.add_endtry(other, replace=False)
        elif isinstance(other, BibtexParser):
            for entry in other:
                self.append_entry(entry)
        else:
            raise ValueError('added object must be BibtexEntry or BibtexParser')
        return self

    def __iter__(self):
        self.current_iter = 0
        return self

    def __next__(self):
        if self.current_iter < len(self.entries):
            self.current_iter += 1
            return self.entries[self.current_iter-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.entries[index]

    def __setitem__(self, index, entry):
        self.entries[index] = entry

    def __len__(self):
        return len(self.entries)

    def __contains__(self, item):
        if type(item) == str:
            return item in self.get_all_keys()
        elif isinstance(item, BibtexEntry):
            return item in self.entries
        return False

    def __delitem__(self, item):
        keys = self.get_all_keys()
        if type(item) == str and item in keys:
            del self.entries[keys.index(item)]
        elif type(item).__name__ == 'BibtexEntry' and item in self:
            del item

    def __copy__(self):
        return BibtexParser(self.entries)

    def __deepcopy__(self, memo={}):
        bibtex = BibtexParser()
        bibtex.entries += [entry.__deepcopy__() for entry in self.entries]
        return bibtex

    def get_all_keys(self):
        return [entry.key for entry in self.entries]

    def get_entry(self, key: str):
        keys = self.get_all_keys()
        return self.entries[keys.index(key)] if key in keys else None

    def get_entries_where_field_equals_content(self, field, content):
        entries = []
        for entry in self.entries:
            if field in entry.fields:
                if entry.contents[entry.fields.index(field)] == content:
                    entries.append(entry)
        return BibtexParser(entries)

    def get_entries_in_year(self, year):
        return self.get_entries_where_field_equals_content('year', str(year))

    def get_entries_where_content_is_in_field(self, content, field):
        entries = []
        for entry in self.entries:
            if field in entry.fields:
                if content in entry.contents[entry.fields.index(field)]:
                    entries.append(entry)
        return BibtexParser(entries)

    def get_entries_with_author(self, author):
        return self.get_entries_where_content_is_in_field(author, 'author')

    def set_order_of_fields(self, order: list, keys=None):
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.set_order_of_fields(order)

    def set_field_last(self, field: str):
        for entry in self.entries:
            entry.set_field_last(field)

    def use_field_in_field_as_href(self, from_field='url', to_field='title', keys=None, remove_from_field=True, exclude_types=None):
        if keys is None:
            keys = self.get_all_keys()
        if exclude_types is None:
            exclude_types = []
        exclude_types = [tpe.lower() for tpe in exclude_types]
        for entry in self.entries:
            if entry.key in keys:
                if entry.type.lower() not in exclude_types:
                    entry.use_field_in_field_as_href(from_field, to_field, remove_from_field)

    def use_url_in_title_as_href(self):
        self.use_field_in_field_as_href(from_field='url', to_field='title', keys=None, remove_from_field=True, exclude_types=None)

    def use_href_from_title_as_url(self, keys=None, replace=True, use_url_package=True):
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.use_href_from_title_as_url(replace, use_url_package)

    def sort_by_key(self, reverse=False):
        self.entries.sort(key=lambda entry: entry.key, reverse=reverse)

    def fix_special_characters(self, keys=None, fields=None, replace_chars=None, only_if_url_or_href=False):
        if replace_chars is None:
            replace_chars = [['%', '\%'], ['&', '\&']]
        if keys is None:
            keys = self.get_all_keys()
        for entry in self.entries:
            if entry.key in keys:
                entry.fix_special_characters(fields, replace_chars, only_if_url_or_href)

    def get_entries_with_type(self, type):
        ret = BibtexParser()
        type_lower = type.lower()
        for entry in self.entries:
            if entry.type.lower() == type_lower:
                ret.append_entries([entry])
        return ret

    def get_index_of_key(self, key):
        if key not in self.get_all_keys():
            return -1
        for idx, entry in enumerate(self.entries):
            if entry.key == key:
                return idx

    def remove_keys(self, keys):
        all_keys = self.get_all_keys()
        for key in keys:
            if not key in all_keys: continue
            idx = self.get_index_of_key(key)
            if idx == -1: continue
            self.entries.pop(idx)

    def remove_fields_from_keys(self, fields, keys=None):
        if keys is None:
            keys = self.get_all_keys()
        for key in keys:
            idx = self.get_index_of_key(key)
            if idx == -1: continue
            self.entries[idx].remove_fields(fields)

    def remove_fields(self, fields):
        self.remove_fields_from_keys(fields, keys=None)

    def remove_entries_with_type(self, type):
        type_lower = type.lower()
        for i, entry in enumerate(self.entries):
            if entry.type.lower() == type_lower:
                self.entries.pop(i)

    def check_for_duplicates(self):
        keys = self.get_all_keys()
        counted_keys = []
        count = []
        for key in keys:
            if not key in counted_keys:
                counted_keys.append(key)
                count.append(1)
            else:
                count[counted_keys.index(key)] += 1
        duplicate_keys = []
        for i, key in enumerate(counted_keys):
            if count[i] > 1:
                duplicate_keys.append(key)
        return duplicate_keys

    def get_entries_cited_in_files(self, files):
        all_keys = self.get_all_keys()
        out = BibtexParser()
        keys = []
        for file in files:
            if not os.path.isfile(file): continue
            try:
                with open(file, 'r', encoding='utf8') as input_file:
                    while True:
                        line = input_file.readline()
                        if not line: break
                        match = self.get_citation.search(line)
                        if not match: continue
                        matched_keys = match.groupdict()['keys']
                        if not matched_keys: continue
                        matched_keys = matched_keys.split(',')
                        matched_keys = [key.strip() for key in matched_keys]
                        for key in matched_keys:
                            if key not in all_keys or key in keys: continue
                            keys.append(key)
                            out.append_entries([self.entries[all_keys.index(key)]])
            except UnicodeDecodeError:
                continue
        return out

    def get_entries_cited_in_folders(self, folders, include_subfolders=False, file_extensions=None):
        if file_extensions is None:
            file_extensions = ['.tex']
        tex_files = []
        def _append_file(file):
            if os.path.isdir(file): return
            _, ext = os.path.splitext(file)
            if file_extensions is not None and ext not in file_extensions: return
            tex_files.append(file)
        for folder in folders:
            if include_subfolders:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        _append_file(os.path.join(root, file))
            else:
                for file in os.listdir(folder):
                    _append_file(os.path.join(folder, file))
        return self.get_entries_cited_in_files(tex_files)

    def get_keys_cited_in_files(self, files):
        return [entry.key for entry in self.get_entries_cited_in_files(files)]

    def get_string_of_keys_cited_in_files(self, files):
        return ', '.join(self.get_keys_cited_in_files(files))

    def get_keys_cited_in_folder(self, folders, include_subfolders=False, file_extensions=None):
        return [entry.keys for entry in self.get_entries_cited_in_folders(folders, include_subfolders, file_extensions)]

    def get_string_of_keys_cited_in_folder(self, folders, include_subfolders=False, file_extensions=None):
        return ', '.join(self.get_keys_cited_in_folder(folders, include_subfolders, file_extensions))

    def create_pdf(self, output_filename, open_file=False):
        output_filename, ext = os.path.splitext(output_filename)
        ext = '.tex'
        output_dir = os.path.dirname(output_filename)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        bib_filename = os.path.join(output_dir, 'references_tmp.bib')
        tex = '\\documentclass{article}\n\n'
        tex += '\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}\n\\usepackage[english]{babel}\n\\usepackage{amsmath,amssymb}\n\\usepackage{xcolor}\n\\usepackage[backend=biber,sorting=none,style=reading]{biblatex}\n\\usepackage{hyperref}\n\\usepackage[margin=2cm, includefoot]{geometry}\n\n'
        tex += '\\addbibresource[]{references_tmp.bib}\n\n'
        tex += '\\hypersetup{\n\tcolorlinks,\n\tcitecolor = black,\n\tfilecolor = black,\n\turlcolor = blue!50!black,\n\tpdfstartview = FitH\n}\n\n'
        tex += '\\begin{document}\n\t\\nocite{*}\n\t\\printbibliography\n\end{document}\n'
        self.write(bib_filename)
        with open(output_filename + ext, 'w+', encoding='utf8') as out:
            out.write(tex)
        self._compile_tex_file(output_filename + ext)
        self._run_biber(output_filename)
        self._compile_tex_file(output_filename + ext)
        returncode = self._compile_tex_file(output_filename + ext)
        pdf_created = returncode == 0
        os.remove(bib_filename)
        for ext in ['.tex', '.log', '.aux', '.bcf', '.out', '.run.xml', '.bbl', '.blg']:
            try:
                os.remove(output_filename + ext)
            except Exception as ee:
                continue
        if pdf_created:
            if open_file:
                self._start_file(output_filename + '.pdf')
        else:
            try:
                os.remove(output_filename + '.pdf')
            except Exception as e:
                pass
        return pdf_created

    @staticmethod
    def _compile_tex_file(output_filename):
        proc = subprocess.Popen(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', output_filename], stdout=None)
        proc.communicate()
        return proc.returncode

    @staticmethod
    def _run_biber(output_filename):
        proc = subprocess.Popen(['biber', output_filename], stdout=None)
        proc.communicate()
        return proc.returncode

    @staticmethod
    def _start_file(filename):
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filename))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(filename)
        else:  # linux variants
            subprocess.call(('xdg-open', filename))
