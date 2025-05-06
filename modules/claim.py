from web3.contract import AsyncContract
from client.client import Client
from utils.logger import logger
from typing import Optional, Union, Dict, Any, List


class Claimer:
    def __init__(self, client: Client, contract: AsyncContract):
        self.client = client
        self.claimer_contract = contract

    async def register(self) -> bool:
        """
        Регистрирует адрес в смарт-контракте
        
        Returns:
            bool: Результат операции (True - успешно, False - ошибка)
        """
        try:
            tx = await self.claimer_contract.functions.register().build_transaction(await self.client.prepare_tx())
            tx_hash = await self.client.sign_and_send_tx(tx)
            if not tx_hash:
                return False
            result = await self.client.wait_tx(tx_hash)
            return result
        except Exception as e:
            logger.error(f"{e}")
            return False

    async def claim(self) -> bool:
        """
        Клеймит токены из смарт-контракта
        
        Returns:
            bool: Результат операции (True - успешно, False - ошибка)
        """
        try:
            params = int(await self.client.to_wei_main(self.client.amount))
            tx = await self.claimer_contract.functions.claim(params).build_transaction(
                await self.client.prepare_tx())
            tx_hash = await self.client.sign_and_send_tx(tx)
            if not tx_hash:
                return False
            result = await self.client.wait_tx(tx_hash)
            return result
        except Exception as e:
            logger.error(f"{e}")
            return False
