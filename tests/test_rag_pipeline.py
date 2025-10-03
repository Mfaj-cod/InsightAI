def test_rag_pipeline_interface():
    from modules.rag_pipeline import RAGPipeline # type: ignore
    rp = RAGPipeline(vector_dim=3)
    assert hasattr(rp, 'ingest_image')
    assert hasattr(rp, 'query')

