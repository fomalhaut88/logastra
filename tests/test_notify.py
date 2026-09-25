from unittest import IsolatedAsyncioTestCase

from src.monitor import notify


class TestNotify(IsolatedAsyncioTestCase):
    async def test(self):
        await notify("unit test notification")

    async def test_failure_1(self):
        track_name = "antares"
        fail_detail = """ConnectionResetError
[Errno 104] Connection reset by peer

Traceback (most recent call last):
  File "/app/src/monitor.py", line 67, in handle_track
    await asyncio.wait_for(coro, timeout=TIMEOUT)
  File "/usr/local/lib/python3.12/asyncio/tasks.py", line 520, in wait_for
    return await fut
           ^^^^^^^^^
  File "/app/src/handlers.py", line 67, in process
    async with asyncssh.connect(self._host, self._port):
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncssh/misc.py", line 459, in __aenter__
    self._coro_result = await self._coro
                        ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncssh/connection.py", line 9250, in connect
    return await asyncio.wait_for(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/tasks.py", line 520, in wait_for
    return await fut
           ^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncssh/connection.py", line 544, in _connect
    await options.waiter
ConnectionResetError: [Errno 104] Connection reset by peer"""  # noqa: E501
        text = f"Service {track_name} failed:\n\n```\n{fail_detail}\n```"
        await notify(text)
