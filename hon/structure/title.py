"""
    hon.structure.title
    ~~~~~

    Module representing the ``Title`` structural element.
"""


class Title():
    """A structural element representing a title of a book component.

    Books, Summaries, and Chapters can all have titles.
    """
    def __init__(self, text=None):
        self.text = text
    
    def __str__(self):
        return str(self.text)
    
    def __repr__(self):
        return ('Title(text={})'.format(repr(self.text)))