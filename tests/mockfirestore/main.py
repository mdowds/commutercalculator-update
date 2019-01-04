import operator
from functools import reduce
from typing import Dict, Any, List, Tuple, NamedTuple, TypeVar, Sequence

from fn.iters import take

KeyValuePair = Tuple[str, Dict[str, Any]]
Document = Dict[str, Any]
Collection = Dict[str, Document]
Store = Dict[str, Collection]

GeoPoint = NamedTuple('GeoPoint', (('latitude', float), ('longitude', float)))


class DocumentSnapshot:
    def __init__(self, doc: Document):
        self._doc = doc

    @property
    def exists(self):
        return self._doc != {}

    def to_dict(self):
        return self._doc


class DocumentReference:
    def __init__(self, data: Store, path: List[str]):
        self._data = data
        self._path = path

    def get(self):
        return DocumentSnapshot(get_by_path(self._data, self._path))

    def set(self, data: Document):
        set_by_path(self._data, self._path, data)

    def update(self, data: Dict[str, Any]):
        get_by_path(self._data, self._path).update(data)

    def collection(self, name):
        document = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in document:
            set_by_path(self._data, new_path, {})
        return CollectionReference(self._data, new_path)


class Query:
    def __init__(self, data: Collection):
        self._data = data

    def get(self) -> List[DocumentSnapshot]:
        return [DocumentSnapshot(doc) for doc in self._data.values()]

    def order_by(self, key: str) -> 'Query':
        sorted_items: List[KeyValuePair] = sorted(self._data.items(), key=lambda doc: doc[1][key])
        return Query(dict(sorted_items))

    def limit(self, limit_amount: int) -> 'Query':
        limited = take(limit_amount, self._data.items())
        return Query(dict(limited))


class CollectionReference:
    def __init__(self, data: Store, path: List[str]):
        self._data = data
        self._path = path

    def document(self, name: str) -> DocumentReference:
        collection = get_by_path(self._data, self._path)
        new_path = self._path + [name]
        if name not in collection:
            set_by_path(self._data, new_path, {})
        return DocumentReference(self._data, new_path)

    def get(self) -> List[DocumentSnapshot]:
        collection = get_by_path(self._data, self._path)
        return [DocumentSnapshot(doc) for doc in collection.values()]

    def order_by(self, key: str) -> Query:
        collection = get_by_path(self._data, self._path)
        return Query(collection).order_by(key)

    def limit(self, limit_amount: int) -> Query:
        collection = get_by_path(self._data, self._path)
        return Query(collection).limit(limit_amount)


class MockFirestore:

    _data: Store = {}

    def collection(self, name: str) -> CollectionReference:
        if name not in self._data:
            self._data[name] = {}
        return CollectionReference(self._data, [name])


T = TypeVar('T')


def get_by_path(data: Dict[str, T], path: Sequence[str]) -> T:
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, path, data)


def set_by_path(data: Dict[str, T], path: Sequence[str], value: T):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(data, path[:-1])[path[-1]] = value
