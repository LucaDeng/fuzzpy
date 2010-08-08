"""\
Indexed set module. Contains the indexed set class, a set that is indexed like
a dict.

@author: Aaron Mavrinac
@organization: University of Windsor
@contact: mavrin1@uwindsor.ca
@license: LGPL-3
"""

from copy import copy


class IndexedMember(object):
    """\
    Indexed member class. This is a special type of object which has mutable
    properties but a special immutable property (called the index) which is
    used for hashing and equality, allowing it to be stored in a set or to be
    used as a dict key.
    """
    def __init__(self, index):
        """\
        Constructor.

        @param index: The index object (immutable).
        @type index: C{object}
        """
        if not hasattr(type(index), '__hash__') \
        or not hasattr(type(index), '__eq__'):
            raise TypeError("index object must be immutable")
        self._index = index

    @property
    def index(self):
        """\
        Return the index object.

        @rtype: C{object}
        """
        return self._index

    def __hash__(self):
        """\
        Return a hash of the index object.

        @return: The index hash.
        @rtype: C{int}
        """
        return hash(self.index)

    def __eq__(self, other):
        """\
        Return whether the index objects match.

        @return: True if equal, false otherwise.
        @rtype: C{bool}
        """
        try:
            return self.index == other.index
        except AttributeError:
            return False

    def __ne__(self, other):
        """\
        Return whether the index objects do not match.

        @return: True if not equal, false otherwise.
        @rtype: C{bool}
        """
        return not self == other


class IndexedSet(set):
    """\
    Indexed set class. This is a special type of set whose members are mutable
    objects with an immutable attribute. These overall-mutable members can then
    be accessed in dict style, using the index as key.
    """
    def __init__(self, iterable = set()):
        """\
        Constructor.

        @param iterable: The iterable to intialize the set with.
        @type iterable: C{iterable}
        """
        set.__init__(self)
        self.update(iterable)

    def __getitem__(self, key):
        """\
        Return a set item indexed by key.

        @param key: The index of the item to get.
        @type key: C{object}
        @return: The matching item.
        @rtype: C{object}
        """
        for item in self:
            if item.index == key:
                return item
        raise KeyError(key)

    def __setitem__(self, key, item):
        """\
        Assign an item by key. Normally, new items are added via add() and
        existing items modified via object reference; this is included for
        completeness.

        @param key: The index of the item to assign.
        @type key: C{object}
        @param item: The item to assign.
        @type item: C{object}
        """
        if not item.index == key:
            raise ValueError("key does not match item index attribute")
        if key in self:
            self.remove(key)
        set.add(self, item)

    def __contains__(self, key):
        """\
        Return whether an item is a member of the set, by key or by object.

        @param key: The index or object to test for.
        @type key: C{object}
        @return: True if member, false otherwise.
        @rtype: C{bool}
        """
        try:
            for item in self:
                if item.index == key:
                    return True
        except AttributeError:
            pass
        return set.__contains__(self, key)

    def add(self, item):
        """\
        Add an item to the set. Uses a copy since IndexedMembers have mutable
        properties.

        @param item: The item to add.
        @type item: L{IndexedMember}
        """
        if not isinstance(item, IndexedMember):
            raise TypeError("item to add must be an IndexedMember")
        set.add(self, copy(item))

    def update(self, iterable):
        """\
        Update the set by adding all items in an iterable to it.

        @param iterable: The iterable containing the items to add.
        @type iterable: C{iterable}
        """
        for item in iterable:
            self.add(item)

    def remove(self, key):
        """\
        Remove an item from the set by key or by object.

        @param key: The index or object to remove.
        @type key: C{object}
        """
        try:
            set.remove(self, self[key])
        except KeyError:
            set.remove(self, key)

    def keys(self):
        """\
        Return a list of keys in the set.

        @return: List of keys in the set.
        @rtype: C{list}
        """
        return [item.index for item in self]

    def has_key(self, key):
        """\
        Return whether this set contains an item with a given index.

        @param key: The index to test for.
        @type key: C{object}
        @return: True if a matching key exists, false otherwise.
        @rtype: C{bool}
        """
        return key in self.keys()
