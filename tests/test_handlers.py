from unittest import IsolatedAsyncioTestCase

from src.handlers import PortAvailability, WebAvailability


class TestHandlers(IsolatedAsyncioTestCase):
    async def test_port_availability(self):
        await PortAvailability(host='78.186.183.41', port=14732).process()
        await PortAvailability(host='78.186.183.41', port=31552).process()
        await PortAvailability(host='78.186.183.41', port=5772).process()

    async def test_web_availability(self):
        await WebAvailability(url='https://alexfomalhaut.com/').process()
        await WebAvailability(url='https://chat.alexfomalhaut.com/').process()
        await WebAvailability(
            url='http://78.186.183.41:5772/node/info',
            result_json={
                "version": "0.1.4",
                "wallet": "AB2EEF9614F27BFBE34B01B6461580F2"
                          "B495A2EB4D01874C40BEFCCAB2A649BF",
                "fee": "D32",
                "free_split": True,
                "lite_mode": False,
            },
        ).process()
