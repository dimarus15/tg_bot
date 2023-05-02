"""
Module with sqlite3 database structure
"""

from pony import orm

db = orm.Database()

class def_dtb():
    @staticmethod
    def get_dtb(name: str) -> db.Entity:
        if name == 'DesiredFilm':
            return DesiredFilm
        elif name == 'WatchedFilm':
            return WatchedFilm
        elif name == 'User':
            return User

def convert_from_py2sqlite(data):
    if isinstance(data, int) and data == -1000:
        return None
    else:
        return data

class DesiredFilm(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str, 100)
    release_year = orm.Required(int)
    url = orm.Optional(str)
    priority = orm.Required(int)
    username = orm.Required(str, 100)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'title': self.title,
            'release_year': self.release_year,
            'url': self.url,
            'priority': self.priority,
            'username': self.username
        }

class WatchedFilm(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str, 100)
    release_year = orm.Required(int)
    url = orm.Optional(str)
    rate = orm.Required(int)
    comment = orm.Optional(str, 500)
    username = orm.Required(str, 100)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'title': self.title,
            'release_year': self.release_year,
            'url': self.url,
            'rate': self.rate,
            'comment': self.comment,
            'username': self.username
        }