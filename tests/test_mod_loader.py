from ck3_mod_manager.loader.mod_loader import ModLoader

def test_parse_mod_file(tmp_path):
    # Create a dummy .mod file
    mod_file = tmp_path / "test.mod"
    content = """
    name="Test Mod"
    path="mod/test_mod"
    supported_version="1.12.*"
    remote_file_id="123456"
    """
    mod_file.write_text(content, encoding="utf-8")
    
    loader = ModLoader()
    result = loader._parse_mod_file(mod_file)
    
    assert result is not None
    assert result['name'] == "Test Mod"
    assert result['path'] == "mod/test_mod"
    assert result['version'] == "1.12.*"
    assert result['remote_file_id'] == "123456"

def test_parse_simple_mod_file(tmp_path):
    # Test minimal file
    mod_file = tmp_path / "simple.mod"
    content = 'name="Simple Mod"'
    mod_file.write_text(content, encoding="utf-8")
    
    loader = ModLoader()
    result = loader._parse_mod_file(mod_file)
    
    assert result is not None
    assert result['name'] == "Simple Mod"
    # Should handle missing fields gracefully
