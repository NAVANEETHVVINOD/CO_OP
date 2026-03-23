import pytest
from unittest.mock import patch

from app.core.hardware_detector import detect_and_store_hardware
from app.db.models import SystemSetting

@pytest.mark.asyncio
async def test_detect_and_store_hardware(db_session):
    with patch("app.core.hardware_detector.psutil") as mock_psutil:
        
        # Mock RAM
        mock_virtual_memory = mock_psutil.virtual_memory.return_value
        mock_virtual_memory.total = 32 * 1024 * 1024 * 1024  # 32GB
        
        mock_psutil.cpu_count.return_value = 16
        
        with patch("app.db.session.AsyncSessionLocal") as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = db_session
            
            # Run detection
            result = await detect_and_store_hardware()
            assert result["tier"] == "AGENCY"

        
        # Verify it was saved to the DB
        from sqlalchemy import select
        result = await db_session.execute(select(SystemSetting).filter(SystemSetting.key == "hardware_tier"))
        setting = result.scalar_one_or_none()
        assert setting is not None
        assert setting.value["tier"] == "AGENCY"
        assert "ram_gb" in setting.value
        assert "cpu_cores" in setting.value
