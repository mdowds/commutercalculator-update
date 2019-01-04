from unittest import TestCase

from tests.mockfirestore import MockFirestore


class TestCollectionReference(TestCase):
    def test_collection_get_returnsDocuments(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1},
            'second': {'id': 2}
        }}
        docs = fs.collection('foo').get()
        self.assertEqual({'id': 1}, docs[0].to_dict())
        self.assertEqual({'id': 2}, docs[1].to_dict())

    def test_collection_get_collectionDoesNotExist(self):
        fs = MockFirestore()
        docs = fs.collection('foo').get()
        self.assertEqual([], docs)

    def test_collection_get_nestedCollection(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {
                'id': 1,
                'bar': {
                    'first_nested': {'id': 1.1}
                }
            }
        }}
        docs = fs.collection('foo').document('first').collection('bar').get()
        self.assertEqual({'id': 1.1}, docs[0].to_dict())

    def test_collection_get_nestedCollection_collectionDoesNotExist(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1}
        }}
        docs = fs.collection('foo').document('first').collection('bar').get()
        self.assertEqual([], docs)

    def test_collection_orderBy(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'order': 2},
            'second': {'order': 1}
        }}

        docs = fs.collection('foo').order_by('order').get()
        self.assertEqual({'order': 1}, docs[0].to_dict())
        self.assertEqual({'order': 2}, docs[1].to_dict())

    def test_collection_limit(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'id': 1},
            'second': {'id': 2}
        }}
        docs = fs.collection('foo').limit(1).get()
        self.assertEqual({'id': 1}, docs[0].to_dict())
        self.assertEqual(1, len(docs))

    def test_collection_limitAndOrderBy(self):
        fs = MockFirestore()
        fs._data = {'foo': {
            'first': {'order': 2},
            'second': {'order': 1},
            'third': {'order': 3}
        }}
        docs = fs.collection('foo').limit(2).order_by('order').get()
        self.assertEqual({'order': 1}, docs[0].to_dict())
        self.assertEqual({'order': 2}, docs[1].to_dict())