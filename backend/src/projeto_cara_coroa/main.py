import asyncio

from .server.host import Host


async def main():
    host = Host()

    await asyncio.create_task(host.run())


if __name__ == "__main__":
    asyncio.run(main())