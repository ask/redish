from redish.client import Client


class ModelType(type):
    """Metaclass for :class:`Model`s."""

    def __new__(cls, name, bases, attrs):
        attrs.setdefault("name", name)
        protected_attrs = set(attrs.keys())
        for base in bases:
            protected_attrs.update(set(vars(base).keys()))
        attrs["_protected"] = protected_attrs
        return super(ModelType, cls).__new__(cls, name, bases, attrs)


def _unpickle_model(model, id, fields):
    return model(id=id, **fields)


class Model(dict):
    """A Model.

    :param manager: The :class:`Manager` for this model.
    :keyword id: Id of the entry, ``None`` if the entry has not been
        created yet.
    :keyword \*\*fields: Values of the entry.

    .. attribute:: name

        Name of the model.
        **REQUIRED**

        All models needs a name, this name is used to keep track of ids
        related to this model.

    .. attribute:: id

        The unique id for this entry.
        If the entry does not have an id, it means the entry has not yet
        been created and a new id will be automatically assigned when saved.

    .. attribute:: objects

        :class:`Manager` instance for this model.


    """
    __metaclass__ = ModelType

    id = None
    name = None
    objects = None

    def __init__(self, manager=None, id=None, **fields):
        self.objects = manager
        self.id = id
        dict.__init__(self, self.prepare_fields(fields))

    def __reduce__(self):
        return (_unpickle_model, (self.__class__, self.id, dict(self)), None)

    def save(self):
        """Save this entry.

        If the entry does not have an :attr:`id`, a new id will be assigned,
        and the :attr:`id` attribute set accordingly.

        Pre-save processing of the fields saved can be done by
        overriding the :meth:`prepare_save` method.

        Additional actions to be done after the save operation
        has been completed can be added by defining the
        :meth:`post_save` method.

        """
        id = self.id or self.objects.id(self.name)
        self.objects[id] = self.prepare_save(dict(self))
        self.id = id
        self.post_save()
        return id

    def delete(self):
        """Delete this entry."""
        del(self.objects[self.id])
        self.post_delete()

    def prepare_save(self, fields):
        """Prepare fields for saving."""
        return fields

    def prepare_fields(self, fields):
        """Prepare fields when creating an instance of this class."""
        return fields

    def post_save(self):
        """Additional actions to be done after a :meth:`save` operation has been
        completed."""
        pass

    def post_delete(self):
        """Additional actions to be done after a :meth:`delete` operation has
        been completed."""
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


class ManagerType(type):
    """Metaclass for :class:`Manager`s."""

    def __new__(cls, name, bases, attrs):
        if not attrs.get("abstract", False):
            model = attrs["model"]

            def instance(self, id=None, **fields):
                return model(self, id, **fields)

            attrs[model.name] = attrs["instance"] = instance
        attrs["abstract"] = False

        return super(ManagerType, cls).__new__(cls, name, bases, attrs)


class Manager(Client):
    """A manager.

    .. attribute model::
        The :class:`Model` this is a manager for.
        **REQUIRED**

    .. attribute abstract::
        Set this to ``True`` if this is an abstract class,
        (i.e not having a :attr:`model` instance assigned to it).

    .. attribute instance::

        Method returning an instance of the model that is
        connected to this manager.

    """
    __metaclass__ = ManagerType

    model = None
    abstract = True

    def get(self, id):
        """Get entry by id."""
        return self.instance(id, **self[id])

    def get_many(self, ids):
        """Get several entries at once."""
        return [self.instance(id, **fields)
                    for id, fields in zip(ids, self.api.mget(ids))]

    def __iter__(self):
        pattern = "%s:*" % self.model.name
        return (self.instance(id, **fields)
                        for id, fields in self.iteritems(pattern))

    def all(self):
        """Get all entries."""
        return list(iter(self))

    def create(self, **fields):
        """Create new entry."""
        entry = self.instance(**fields)
        entry.save()
        return entry
