
class AuthRouter(object):
    labels = ['auth', 'user_profile']
    labels_relation = ['auth', 'user_profile', 'records']
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label in self.labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label in self.labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label in self.labels or \
           obj2._meta.app_label in self.labels:
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label in self.labels:
            return db == 'default'
        return None


class RecordsRouter(object):
    labels = ['records']
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'records':
            return 'records_db'


    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label in self.labels or \
           obj2._meta.app_label in self.labels:
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        return None
