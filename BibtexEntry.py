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
