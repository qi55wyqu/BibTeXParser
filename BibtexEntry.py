import re

class BibtexEntry:
    def __init__(self, key: str, entryType='article'):
        self.key = key
        self.type = entryType
        self.fields = []
        self.contents = []
        self.get_url_from_latex_url = re.compile(r'\\url\{\s*(.*)\s*\}')
        self.get_url_from_href = re.compile(r'\\href\{(.*)\}\{.*\}')
        self.get_title_from_href = re.compile(r'\\href\{.*\}\{(.*)\}')

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

    def set_order_of_fields(self, order):
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
        if field not in self.fields: return False
        idx = self.fields.index(field)
        self.fields.append(self.fields.pop(idx))
        self.contents.append(self.contents.pop(idx))
        return True

    def use_field_in_field_as_href(self, from_field='url', to_field='title', remove_from_field=True):
        if not (from_field in self.fields and to_field in self.fields):
            return False
        idx_from = self.fields.index(from_field)
        idx_to = self.fields.index(to_field)
        from_content = self.contents[idx_from]
        to_content = self.contents[idx_to]
        if '\\url{' in from_content:
            from_content = self.get_url_from_latex_url.search(from_content).group(1)
        self.contents[idx_to] = '\href{' + from_content + '}{' + to_content + '}'
        if remove_from_field:
            self.fields.pop(idx_from)
            self.contents.pop(idx_from)
        return True

    def use_url_in_title_as_href(self):
        self.use_field_in_field_as_href(from_field='url', to_field='title', remove_from_field=True)

    def use_href_from_title_as_url(self, replace=True, use_url_package=True):
        if not 'title' in self.fields: return False
        idx_title = self.fields.index('title')
        url = self.get_url_from_href.search(self.contents[idx_title])
        if url is None: return False
        title = self.get_title_from_href.search(self.contents[idx_title])
        if title is None: return False
        title = title.group(1)
        url = '\\url{' + url.group(1) + '}' if use_url_package else url.group(1)
        if replace and 'url' in self.fields:
            self.contents[self.fields.index('url')] = url
        else:
            self.fields.append('url')
            self.contents.append(url)
        self.contents[idx_title] = title
        return True

    def fix_special_characters(self, fields=None, replace_chars=None, only_if_url_or_href=False):
        if replace_chars is None:
            replace_chars = [['%', '\%'], ['&', '\&']]
        if fields is None:
            fields = self.fields
        for field in fields:
            if field not in self.fields: continue
            idx = self.fields.index(field)
            if only_if_url_or_href and ('\\url{' not in self.contents[idx] and '\\href{' not in self.contents[idx]):
                continue
            for replacement in replace_chars:
                if replacement[1] in self.contents[idx]: continue
                self.contents[idx] = self.contents[idx].replace(replacement[0], replacement[1])

    def remove_fields(self, fields):
        for field in fields:
            if not field in self.fields: continue
            idx = self.fields.index(field)
            self.fields.pop(idx)
            self.contents.pop(idx)
