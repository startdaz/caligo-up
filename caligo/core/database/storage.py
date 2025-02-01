# Taken from https://github.com/animeshxd/pyromongo

import asyncio
import inspect
import time
from typing import Any, List, Optional, Tuple, Union

from pymongo import UpdateOne
from pyrogram.raw.types.input_peer_channel import InputPeerChannel
from pyrogram.raw.types.input_peer_chat import InputPeerChat
from pyrogram.raw.types.input_peer_user import InputPeerUser
from pyrogram.storage.sqlite_storage import get_input_peer
from pyrogram.storage.storage import Storage

from . import AsyncDatabase


class PersistentStorage(Storage):
    """
    database: caligo AsyncDatabase
        required database object of AsyncDatabase
    remove_peers: bool = False
        remove peers collection on logout (by default, it will not remove peers)
    """

    db: AsyncDatabase
    lock: asyncio.Lock
    USERNAME_TTL = 8 * 60 * 60

    def __init__(self, database: AsyncDatabase, remove_peers: bool = False) -> None:
        # Propagate initialization
        super().__init__("")

        self.db = database
        self.lock = asyncio.Lock()

        self._peer = database["PEERS"]
        self._remove_peers = remove_peers
        self._session = database["SESSION"]

    async def open(self) -> None:
        print("Opening session storage...")
        """
        dc_id     INTEGER PRIMARY KEY,
        api_id    INTEGER,
        test_mode INTEGER,
        auth_key  BLOB,
        date      INTEGER NOT NULL,
        user_id   INTEGER,
        is_bot    INTEGER
        """

        session = await self._session.find_one({"_id": 0}, {})
        if session:
            print("Session found in MongoDB:", session)
            return
        #if await self._session.find_one({"_id": 0}, {}):
           # return

        print("No session found, creating new session in MongoDB...")
        await self._session.insert_one(
            {
                "_id": 0,
                "dc_id": 2,
                "api_id": None,
                "test_mode": None,
                "auth_key": b"",
                "date": 0,
                "user_id": 0,
                "is_bot": 0,
            }
        )

    
    async def update_usernames(self, usernames):
        print("Skipping update_usernames(), MongoDB storage does not require it.")
        return

    async def update_state(self, state):
        print("Skipping update_state(), MongoDB storage does not require it.")
        return

    async def save(self) -> None:
        print("Saving session to MongoDB...")

    async def close(self) -> None:
        pass

    async def delete(self) -> None:
        print("Deleting session from MongoDB...")
        try:
            await self._session.delete_one({"_id": 0})
            if self._remove_peers:
                await self._peer.delete_many({})
        except Exception as e:
            print(f"Error deleting session: {e}")
        #except Exception:  # skipcq: PYL-W0703
            #return

    async def update_peers(self, peers: List[Tuple[int, int, str, str, str]]) -> None:
        """(id, access_hash, type, username, phone_number)"""
        s = int(time.time())
        bulk = [
            UpdateOne(
                {"_id": i[0]},
                {
                    "$set": {
                        "access_hash": i[1],
                        "type": i[2],
                        "username": i[3],
                        "phone_number": i[4],
                        "last_update_on": s,
                    }
                },
                upsert=True,
            )
            for i in peers
        ]
        if not bulk:
            return

        await self._peer.bulk_write(bulk)

    async def get_peer_by_id(
        self, peer_id: int
    ) -> Union[InputPeerUser, InputPeerChat, InputPeerChannel]:
        # id, access_hash, type
        res = await self._peer.find_one(
            {"_id": peer_id}, {"_id": 1, "access_hash": 1, "type": 1}
        )
        if not res:
            raise KeyError(f"ID not found: {peer_id}")

        return get_input_peer(*res.values())

    async def get_peer_by_username(
        self, username: str
    ) -> Union[InputPeerUser, InputPeerChat, InputPeerChannel]:
        # id, access_hash, type, last_update_on,
        res = await self._peer.find_one(
            {"username": username},
            {"_id": 1, "access_hash": 1, "type": 1, "last_update_on": 1},
        )

        if not res:
            raise KeyError(f"Username not found: {username}")

        if abs(time.time() - res["last_update_on"]) > self.USERNAME_TTL:
            raise KeyError(f"Username expired: {username}")

        return get_input_peer(res["_id"], res["access_hash"], res["type"])

    async def get_peer_by_phone_number(
        self, phone_number: str
    ) -> Union[InputPeerUser, InputPeerChat, InputPeerChannel]:
        #  _id, access_hash, type,
        res = await self._peer.find_one(
            {"phone_number": phone_number}, {"_id": 1, "access_hash": 1, "type": 1}
        )

        if not res:
            raise KeyError(f"Phone number not found: {phone_number}")

        return get_input_peer(*res.values())

    async def _get(self) -> Optional[Any]:
        attr = inspect.stack()[2].function
        data = await self._session.find_one({"_id": 0}, {attr: 1})
        if not data:
            return

        return data[attr]

    async def _set(self, value: Any) -> None:
        attr = inspect.stack()[2].function
        await self._session.update_one({"_id": 0}, {"$set": {attr: value}}, upsert=True)

    async def _accessor(self, value: Any = object) -> Any:
        print(f"Accessing session attribute: {inspect.stack()[2].function}")
        return await self._get() if value == object else await self._set(value)

    async def dc_id(self, value=object) -> Optional[int]:
        return await self._accessor(value)

    async def api_id(self, value=object) -> Optional[int]:
        return await self._accessor(value)

    async def test_mode(self, value=object) -> Optional[bool]:
        return await self._accessor(value)

    async def auth_key(self, value=object) -> Optional[bytes]:
        return await self._accessor(value)

    async def date(self, value=object) -> Optional[int]:
        return await self._accessor(value)

    async def user_id(self, value=object) -> Optional[int]:
        return await self._accessor(value)

    async def is_bot(self, value=object) -> Optional[bool]:
        return await self._accessor(value)
