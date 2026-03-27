import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    from app.config import get_settings
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'conversations'"))
            columns = [row[0] for row in result]
            print(f"Columns in conversations: {columns}")
            if "tenant_id" in columns:
                print("VERIFICATION SUCCESS: tenant_id exists")
            else:
                print("VERIFICATION FAILURE: tenant_id missing")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
