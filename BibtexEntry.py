import re

class BibtexEntry:
    def __init__(self, key: str, entryType='article'):
        self.key = key
        self.type = entryType
        self.fields = []
        self.contents = []

    def set_field(self, field: str, content: str):
        if field in self.fields:
            self.contents[self.fields.index(field)] = content
        else:
            self.fields.append(field)
            self.contents.append(content)

    def __str__(self):
        str = self.type + ' ' + self.key + '\n'
        for field, content in zip(self.fields, self.contents):
            str += field + ' = ' + content + '\n'
        str += '\n'
        return str

    def set_order_of_fields(self, order=['title', 'author', 'journal', 'year']):
        ordered_fields, ordered_contents = [], []
        remaining_fields, remaining_contents = [], []
        for sort_field in order:
            if sort_field not in self.fields: continue
            idx_field = self.fields.index(sort_field)
            ordered_fields.append(sort_field)
            ordered_contents.append(self.contents[idx_field])
        for field in self.fields:
            if field in order: continue
            idx_field = self.fields.index(field)
            remaining_fields.append(field)
            remaining_contents.append(self.contents[self.fields.index(field)])
        self.fields = ordered_fields + remaining_fields
        self.contents = ordered_contents + remaining_contents

    def set_field_last(self, field: str):
        if field not in self.fields: return
        idx = self.fields.index(field)
        self.fields.append(self.fields.pop(idx))
        self.contents.append(self.contents.pop(idx))

    def use_field_in_field_as_href(self, from_field='url', to_field='title', remove_from_field=True):
        if not (from_field in self.fields and to_field in self.fields):
            return
        idx_from = self.fields.index(from_field)
        idx_to = self.fields.index(to_field)
        from_content = self.contents[idx_from]
        to_content = self.contents[idx_to]
        if '\\url{' in from_content:
            from_content = re.search(r'\\url{\s?(.*)\s?}', from_content).group(1)
        self.contents[idx_to] = '\href{' + from_content + '}{' + to_content + '}'
        if remove_from_field:
            self.fields.pop(idx_from)
            self.contents.pop(idx_from)

    def use_url_in_title_as_href(self):
        self.use_field_in_field_as_href(from_field='url', to_field='title', remove_from_field=True)
