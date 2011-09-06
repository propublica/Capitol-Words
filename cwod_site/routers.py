class NgramRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ngrams':
            return 'ngrams'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ngrams':
            return 'ngrams'
        return None
