from web3.contract import AsyncContract
from client.client import Client
from utils.logger import logger


class Claimer:
    def __init__(self, client: Client, contract: AsyncContract):
        self.client = client
        self.claimer_contract = contract

    async def register(self):
        try:
            tx = await self.claimer_contract.functions.register().build_transaction(await self.client.prepare_tx())
            tx_hash = await self.client.sign_and_send_tx(tx)
            result = await self.client.wait_tx(tx_hash)
            return result
        except Exception as e:
            logger.error(f"{e}")

    async def claim(self):
        try:
            params = int(await self.client.to_wei_main(self.client.amount))
            tx = await self.claimer_contract.functions.claim(params).build_transaction(
                await self.client.prepare_tx())
            tx_hash = await self.client.sign_and_send_tx(tx)
            result = await self.client.wait_tx(tx_hash)
            return result
        except Exception as e:
            logger.error(f"{e}")
