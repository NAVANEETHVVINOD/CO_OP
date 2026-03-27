from minio import Minio
from minio.error import S3Error
from app.config import get_settings
import io
import structlog

logger = structlog.get_logger(__name__)
settings = get_settings()

# Extract hostname from MINIO_URL (remove http:// or https:// prefix)
minio_url = settings.MINIO_URL.replace("http://", "").replace("https://", "")

minio_client = Minio(
    minio_url,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False
)

def init_minio():
    buckets = ["raw-documents", "parsed-chunks", "co-op-documents"]
    for bucket in buckets:
        try:
            if not minio_client.bucket_exists(bucket):
                minio_client.make_bucket(bucket)
                logger.info("Created MinIO bucket", bucket=bucket)
        except S3Error as err:
            logger.error("MinIO error", error=str(err))

def upload_file(bucket_name: str, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> bool:
    try:
        minio_client.put_object(
            bucket_name,
            object_name,
            io.BytesIO(data),
            len(data),
            content_type=content_type
        )
        return True
    except S3Error as err:
        logger.error("MinIO upload error", error=str(err))
        return False

def get_file(bucket_name: str, object_name: str) -> bytes | None:
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except S3Error as err:
        logger.error("MinIO get error", error=str(err))
        return None

def delete_file(bucket_name: str, object_name: str) -> bool:
    try:
        minio_client.remove_object(bucket_name, object_name)
        return True
    except S3Error as err:
        logger.error("MinIO delete error", error=str(err))
        return False
