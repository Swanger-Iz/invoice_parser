import asyncio
import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).parent.parent))


from database.queries_orm import DDL_queries


async def main():
    await DDL_queries.truncate_tables()
    await DDL_queries.create_table_user_requests()


if __name__ == "__main__":
    asyncio.run(main())
