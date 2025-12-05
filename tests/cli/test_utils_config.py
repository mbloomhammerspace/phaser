"""Tests for config manager."""

import pytest
import yaml
from pathlib import Path
from cli.utils.config import ConfigManager


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_load_default_config(self, temp_dir):
        """Test loading default config when file doesn't exist."""
        config_file = temp_dir / "nonexistent.yaml"
        manager = ConfigManager(config_file)
        config = manager.load()
        
        assert "blueprint_version" in config
        assert "nodes" in config
    
    def test_load_existing_config(self, config_file, sample_config):
        """Test loading existing config file."""
        from pathlib import Path
        manager = ConfigManager(Path(config_file))
        config = manager.load()
        
        assert config["blueprint_version"] == sample_config["blueprint_version"]
    
    def test_save_config(self, temp_dir, sample_config):
        """Test saving configuration."""
        config_file = temp_dir / "test-config.yaml"
        manager = ConfigManager(config_file)
        manager.save(sample_config)
        
        assert config_file.exists()
        with open(config_file) as f:
            loaded = yaml.safe_load(f)
        assert loaded["blueprint_version"] == sample_config["blueprint_version"]
    
    def test_validate_config_pass(self, sample_config):
        """Test config validation passes for valid config."""
        manager = ConfigManager()
        errors = manager.validate(sample_config)
        
        assert len(errors) == 0
    
    def test_validate_config_fail_missing_version(self):
        """Test config validation fails for missing blueprint_version."""
        manager = ConfigManager()
        config = {"nodes": []}
        errors = manager.validate(config)
        
        assert len(errors) > 0
        assert any("blueprint_version" in error for error in errors)
    
    def test_validate_config_fail_no_nodes(self):
        """Test config validation fails for missing nodes."""
        manager = ConfigManager()
        config = {"blueprint_version": "v2.2.1"}
        errors = manager.validate(config)
        
        assert len(errors) > 0
        assert any("nodes" in error.lower() or "inventory" in error.lower() for error in errors)
    
    def test_generate_template(self, temp_dir):
        """Test template generation."""
        output_file = temp_dir / "template.yaml"
        manager = ConfigManager()
        manager.generate_template(output_file)
        
        assert output_file.exists()
        with open(output_file) as f:
            template = yaml.safe_load(f)
        assert "blueprint_version" in template
        assert "nodes" in template

