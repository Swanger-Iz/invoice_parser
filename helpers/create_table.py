import asyncio

from app.database.queries_orm import DDL_queries


async def main():
    await DDL_queries.truncate_tables()
    await DDL_queries.create_table_user_requests()


if __name__ == "__main__":
    asyncio.run(main())
