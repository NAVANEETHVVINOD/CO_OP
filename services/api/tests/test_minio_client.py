"""Tests for MinIO client operations."""
import pytest
from unittest.mock import MagicMock, patch
from minio.error import S3Error
from app.core.minio_client import init_minio, upload_file, get_file, delete_file


@pytest.mark.asyncio
async def test_init_minio_creates_buckets():
    """Test that init_minio creates required buckets"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.bucket_exists.return_value = False
        
        init_minio()
        
        # Should check and create all three buckets
        assert mock_client.bucket_exists.call_count == 3
        assert mock_client.make_bucket.call_count == 3
        
        # Verify bucket names
        created_buckets = [call[0][0] for call in mock_client.make_bucket.call_args_list]
        assert "raw-documents" in created_buckets
        assert "parsed-chunks" in created_buckets
        assert "co-op-documents" in created_buckets


@pytest.mark.asyncio
async def test_init_minio_skips_existing_buckets():
    """Test that init_minio skips buckets that already exist"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.bucket_exists.return_value = True
        
        init_minio()
        
        # Should check buckets but not create them
        assert mock_client.bucket_exists.call_count == 3
        assert mock_client.make_bucket.call_count == 0


@pytest.mark.asyncio
async def test_init_minio_handles_errors():
    """Test that init_minio handles S3 errors gracefully"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.bucket_exists.side_effect = S3Error(
            "TestError", "test", "test", "test", "test", "test"
        )
        
        # Should not raise exception
        init_minio()


@pytest.mark.asyncio
async def test_upload_file_success():
    """Test successful file upload"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.put_object.return_value = None
        
        data = b"test file content"
        result = upload_file("test-bucket", "test-file.txt", data, "text/plain")
        
        assert result is True
        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args
        # MinIO put_object uses keyword arguments
        content_type = call_args.kwargs.get("content_type") or \
                      (call_args.args[4] if len(call_args.args) > 4 else None)
        assert content_type == "text/plain"


@pytest.mark.asyncio
async def test_upload_file_default_content_type():
    """Test file upload with default content type"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.put_object.return_value = None
        
        data = b"binary data"
        result = upload_file("test-bucket", "test-file.bin", data)
        
        assert result is True
        call_args = mock_client.put_object.call_args
        # MinIO put_object uses keyword arguments
        content_type = call_args.kwargs.get("content_type") or \
                      (call_args.args[4] if len(call_args.args) > 4 else None)
        assert content_type == "application/octet-stream"


@pytest.mark.asyncio
async def test_upload_file_handles_errors():
    """Test file upload error handling"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.put_object.side_effect = S3Error(
            "UploadError", "test", "test", "test", "test", "test"
        )
        
        data = b"test data"
        result = upload_file("test-bucket", "test-file.txt", data)
        
        assert result is False


@pytest.mark.asyncio
async def test_get_file_success():
    """Test successful file retrieval"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_response = MagicMock()
        mock_response.read.return_value = b"file content"
        mock_client.get_object.return_value = mock_response
        
        result = get_file("test-bucket", "test-file.txt")
        
        assert result == b"file content"
        mock_client.get_object.assert_called_once_with("test-bucket", "test-file.txt")
        mock_response.close.assert_called_once()
        mock_response.release_conn.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_not_found():
    """Test file retrieval when file doesn't exist"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.get_object.side_effect = S3Error(
            "NoSuchKey", "test", "test", "test", "test", "test"
        )
        
        result = get_file("test-bucket", "nonexistent.txt")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_file_handles_errors():
    """Test file retrieval error handling"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        # get_file catches S3Error, not generic Exception
        mock_client.get_object.side_effect = S3Error(
            "ConnectionError", "test", "test", "test", "test", "test"
        )
        
        result = get_file("test-bucket", "test-file.txt")
        
        assert result is None


@pytest.mark.asyncio
async def test_delete_file_success():
    """Test successful file deletion"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.remove_object.return_value = None
        
        result = delete_file("test-bucket", "test-file.txt")
        
        assert result is True
        mock_client.remove_object.assert_called_once_with("test-bucket", "test-file.txt")


@pytest.mark.asyncio
async def test_delete_file_handles_errors():
    """Test file deletion error handling"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.remove_object.side_effect = S3Error(
            "DeleteError", "test", "test", "test", "test", "test"
        )
        
        result = delete_file("test-bucket", "test-file.txt")
        
        assert result is False


@pytest.mark.asyncio
async def test_upload_large_file():
    """Test uploading large file"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.put_object.return_value = None
        
        # 10MB file
        large_data = b"x" * (10 * 1024 * 1024)
        result = upload_file("test-bucket", "large-file.bin", large_data)
        
        assert result is True
        call_args = mock_client.put_object.call_args
        assert call_args[0][3] == len(large_data)


@pytest.mark.asyncio
async def test_upload_empty_file():
    """Test uploading empty file"""
    with patch("app.core.minio_client.minio_client") as mock_client:
        mock_client.put_object.return_value = None
        
        result = upload_file("test-bucket", "empty.txt", b"")
        
        assert result is True
        call_args = mock_client.put_object.call_args
        assert call_args[0][3] == 0
