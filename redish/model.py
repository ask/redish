from redish.client import Client


class ModelType(type):

    def __new__(cls, name, bases, attrs):
        attrs.setdefault("name", name)
        protected_attrs = set(attrs.keys())
        for base in bases:
            protected_attrs.update(set(vars(base).keys()))
        attrs["_protected"] = protected_attrs
        return super(ModelType, cls).__new__(cls, name, bases, attrs)



class Model(dict):
    id = None
    name = None
    objects = None
    __metaclass__ = ModelType

    def __init__(self, manager, id=None, **fields):
        self.objects = manager
        self.id = id
        dict.__init__(self, self.prepare_fields(fields))

    def save(self):
        id = self.id or self.objects.id(self.name)
        self.objects[id] = self.prepare_save(dict(self))
        self.id = id
        self.post_save()
        return id

    def delete(self):
        del(self.objects[self.id])
        self.post_delete()

    def prepare_save(self, fields):
        return fields

    def prepare_fields(self, fields):
        return fields

    def post_save(self):
        pass

    def post_delete(self):
        pass

    def __repr__(self):
        return "<%s %s>" % (self.id, super(Model, self).__repr__())

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key not in self._protected:
            self[key] = value
        else:
            object.__setattr__(self, key, value)


class WithModelRelation(type):

    def __new__(cls, name, bases, attrs):
        if not attrs.get("abstract", False):
            model = attrs["model"]

            def instance(self, id=None, **fields):
                return model(self, id, **fields)

            attrs[model.name] = attrs["instance"] = instance
        attrs["abstract"] = False

        return super(WithModelRelation, cls).__new__(cls, name, bases, attrs)


class Manager(Client):
    __metaclass__ = WithModelRelation
    model = None
    abstract = True

    def get(self, id):
        return self.instance(id, **self[id])

    def get_many(self, ids):
        return [self.instance(id, **fields)
                    for id, fields in zip(ids, self.api.mget(ids))]

    def __iter__(self):
        pattern = ":*" % self.model.name
        return (self.instance(id, **fields)
                        for id, fields in self.iteritems(pattern))

    def all(self):
        return list(iter(self))

    def create(self, **data):
        entry = self.instance(**data)
        entry.save()
        return entry
