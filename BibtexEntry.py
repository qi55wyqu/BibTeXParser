import re
from collections import OrderedDict

class BibtexEntry:
    def __init__(self, key: str, entryType='article'):
        self.key = key
        self.type = entryType
        self.fields = OrderedDict()
        self.get_url_from_latex_url = re.compile(r'\\url\{\s*(.*)\s*\}')
        self.get_url_from_href = re.compile(r'\\href\{(.*)\}\{.*\}')
        self.get_title_from_href = re.compile(r'\\href\{.*\}\{(.*)\}')

    def set_field(self, field: str, content: str):
        self.fields[field] = content

    def get_field(self, field: str):
        return self.fields[field]

    def __name__(self):
        return 'BibtexEntry'

    def __str__(self):
        str = self.type + ' ' + self.key + '\n'
        for field in self.fields:
            str += field + ' = ' + self.fields[field] + '\n'
        return str

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.fields.keys())

    def __getattr__(self, field):
        if 'fields' in self.__dict__:
            if field in self.__dict__['fields']:
                return self.__dict__['fields'][field]
            else:
                 raise AttributeError('Entry has no field ' + field)

    def __copy__(self):
        entry = BibtexEntry(key=self.key, entryType=self.type)
        entry.fields = self.fields
        return entry

    def __deepcopy__(self, memo={}):
        entry = BibtexEntry(key=self.key, entryType=self.type)
        entry.fields = OrderedDict()
        for field in self.fields:
            entry[field] = self.fields[field]
        return entry

    def set_order_of_fields(self, order):
        new_fields = OrderedDict()
        for field in order:
            if field in self.fields:
                new_fields[field] = self.fields[field]
        for field in self.fields:
            if field not in order:
                new_fields[field] = self.fields[field]
        self.fields = new_fields

    def set_field_last(self, field: str):
        try:
            self.fields.move_to_end(field)
            return True
        except KeyError:
            return False

    def use_field_in_field_as_href(self, from_field='url', to_field='title', remove_from_field=True):
        if not (from_field in self.fields and to_field in self.fields):
            return False
        from_content = self.fields[from_field]
        if '\\url{' in from_content:
            from_content = self.get_url_from_latex_url.search(from_content).group(1)
        self.fields[to_field] = '\href{' + from_content + '}{' + self.fields[to_field] + '}'
        if remove_from_field:
            del self.fields[from_field]
        return True

    def use_url_in_title_as_href(self):
        self.use_field_in_field_as_href(from_field='url', to_field='title', remove_from_field=True)

    def use_href_from_title_as_url(self, replace=True, use_url_package=True):
        if not 'title' in self.fields: return False
        url = self.get_url_from_href.search(self.fields['title'])
        if url is None: return False
        title = self.get_title_from_href.search(self.field['title'])
        if title is None: return False
        title = title.group(1)
        url = '\\url{' + url.group(1) + '}' if use_url_package else url.group(1)
        if replace and 'url' in self.fields:
            self.fields['url'] = url
        else:
            self.field['url'] = url
        self.contents['title'] = title
        return True

    # def fix_special_characters(self, fields=None, replace_chars=None, only_if_url_or_href=False):
    #     if replace_chars is None:
    #         replace_chars = [['%', '\%'], ['&', '\&']]
    #     if fields is None:
    #         fields = [field for field in self.fields]
    #     for field in fields:
    #         if field not in self.fields: continue
    #         if only_if_url_or_href and ('\\url{' not in self.fields[field] and '\\href{' not in self.fields[field]):
    #             continue
    #         for replacement in replace_chars:
    #             if replacement[1] in self.fields[field]: continue
    #             self.fields[field] = self.fields[field].replace(replacement[0], replacement[1])

    def remove_fields(self, fields):
        for field in fields:
            try:
                del self.fields[field]
            except KeyError:
                continue
