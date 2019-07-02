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
