"""
Module with sqlite3 database structure
"""

from pony import orm

db = orm.Database()

class def_dtb():
    @staticmethod
    def get_dtb(name: str) -> db.Entity:
        if name == 'WordCard':
            return WordCard
        elif name == 'Lesson':
            return Lesson

def convert_from_py2sqlite(data):
    if isinstance(data, int) and data == -1000:
        return None
    else:
        return data

class WordCard(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    word = orm.Required(str, 30)
    translation = orm.Required(str, 30)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'word': self.word,
            'translation': self.translation
        }

class Lesson(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    number = orm.Required(int)
    difficulty = orm.Required(int)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'number': self.number,
            'difficulty': self.difficulty
        }