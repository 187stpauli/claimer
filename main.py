from config.configvalidator import ConfigValidator
from client.client import Client
from modules.claim import Claimer
from utils.logger import logger
import asyncio
import json
from typing import Dict, Any, Tuple

with open("abi/claimer_abi.json", "r", encoding="utf-8") as f:
    CLAIMER_ABI = json.load(f)


async def load_settings() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Загрузка и валидация настроек"""
    logger.info("⚙️ Загрузка и валидация параметров...\n")
    validator = ConfigValidator("config/settings.json")
    settings = await validator.validate_config()

    with open("constants/constants.json", "r", encoding="utf-8") as file:
        constants = json.load(file)
    
    return settings, constants


async def initialize_client(settings: Dict[str, Any], constants: Dict[str, Any]) -> Client:
    """Инициализация клиента"""
    return Client(
        proxy=settings["proxy"],
        amount=settings["amount"],
        rpc_url=constants["rpc_url"],
        chain_id=constants["chain_id"],
        private_key=settings["private_key"],
        explorer_url=constants["explorer_url"],
        contract_address=constants["contract_address"]
    )


async def check_registration(client: Client, claimer_contract, claimer: Claimer) -> bool:
    """Проверка и выполнение регистрации, если необходимо"""
    result = await claimer_contract.functions.registeredUsers(client.address).call()
    if not result:
        register = await claimer.register()
        if register:
            logger.info(f"✅ Адрес успешно зарегистрирован на клейм!\n")
            return True
        else:
            logger.error(f"❌ Не удалось зарегистрировать адрес!\n")
            return False
    return True


async def check_available_tokens(client: Client, claimer_contract) -> bool:
    """Проверка доступных токенов для клейма"""
    amount_in_wei = await client.to_wei_main(client.amount)
    tokens = await claimer_contract.functions.claimableTokens(client.address).call()
    
    if tokens == 0:
        logger.error(f"❗️ Запас токенов исчерпан!")
        return False
    
    if tokens < amount_in_wei:
        logger.error(f"❗️ Введите меньшее значение для клейма!"
                    f" Остаток токенов {await client.from_wei_main(tokens)}.")
        return False
    
    return True


async def main():
    try:
        logger.info("🚀 Запуск скрипта...\n")
        
        # Загрузка настроек
        settings, constants = await load_settings()
        
        # Инициализация клиента
        client = await initialize_client(settings, constants)

        # Инициализация контракта
        claimer_contract = await client.get_contract(client.contract_address, CLAIMER_ABI)

        # Инициализация клеймера
        claimer = Claimer(client, claimer_contract)

        # Регистрация пользователя при необходимости
        if not await check_registration(client, claimer_contract, claimer):
            return

        # Проверка доступных токенов
        if not await check_available_tokens(client, claimer_contract):
            return

        # Клейм токенов
        claim = await claimer.claim()
        if claim:
            logger.info(f"✅ Успешно заклеймили {client.amount} токена!")

    except Exception as e:
        logger.error(f"Произошла ошибка в основном пути: {e}")


if __name__ == "__main__":
    asyncio.run(main())
