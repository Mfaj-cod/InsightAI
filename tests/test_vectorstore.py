def test_vectorstore_add_search():
    from modules.vectorstore import VectorStore
    vs = VectorStore(dim=3)
    vecs = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
    metas = [{'a': 1}, {'b': 2}]
    ids = ['id1', 'id2']
    vs.add(vecs, metas, ids)
    res = vs.search([1.0, 1.0, 1.0], top_k=1)
    assert res and res[0][0] == 'id2'