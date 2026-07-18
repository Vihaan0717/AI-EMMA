import pytest
from services.data_layer import JarvisDataLayer, InteractionRecord

def test_local_interaction_log():
    # Use a temporary local DB for testing
    dl = JarvisDataLayer(db_path="memory/test_jarvis.db")
    record = InteractionRecord(
        channel="test",
        user_input="Hello",
        response="Hi",
        metadata={"test": True}
    )
    
    res = dl.feedback.log_interaction(record)
    assert res is not None
    
    # Verify local retrieval (Preferences as a proxy)
    dl.preferences.set_preference("mode", "stealth")
    val = dl.preferences.get_preference("mode")
    assert val == "stealth"

def test_cloud_fallback(mocker):
    # Mock db_manager to simulate cloud failure
    dl = JarvisDataLayer(db_path="memory/test_jarvis.db")
    mocker.patch.object(dl.store.cloud, "log_interaction", side_effect=Exception("Cloud Down"))
    
    record = InteractionRecord(
        channel="test",
        user_input="Cloud Fallback",
        response="Handled"
    )
    
    # Should not raise exception, but return local ID
    res = dl.feedback.log_interaction(record)
    assert res is not None
