def test_get_embedding_callable():
    from modules.embeddings import get_embedding
    assert callable(get_embedding)

