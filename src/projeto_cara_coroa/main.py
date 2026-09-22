import asyncio

from .client.client import Client

from .server.host import Host


async def main():
    host = Host()

    asyncio.create_task(host.run())

    client_1 = Client()
    client_2 = Client()
    
    c1_messages = [
        (
            {
                'type': 'create_room'
            },
            1,
            3
        )
    ]
    
    c2_messages = [
        (
            {
                'type': 'join_room',
                'room_id': 'abc'
            },
            6,
            8
        )
    ]

    await asyncio.gather(
        client_1.run(c1_messages),
        client_2.run(c2_messages),
    )


if __name__ == "__main__":
    asyncio.run(main())