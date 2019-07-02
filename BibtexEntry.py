class BibtexEntry:
    def __init__(self, key: str, entryType='article', fields=[], contents=[]):
        assert len(fields) == len(contents)
        self.key = key
        self.type = entryType
        self.fields = fields
        self.contents = contents

    def set_field(self, field: str, content: str):
        if field in self.fields:
            self.contents[self.fields.index(field)] = content
        else:
            self.fields.append(field)
            self.contents.append(content)
