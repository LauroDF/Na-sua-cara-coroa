import asyncio

from .client.client import Client

from .server.host import Host


async def main():
    host = Host()

    asyncio.create_task(host.run())

    client_1 = Client()
    client_2 = Client()

    await asyncio.gather(
        client_1.run(),
        client_2.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())