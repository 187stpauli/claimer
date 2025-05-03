from config.configvalidator import ConfigValidator
from client.client import Client
from modules.claim import Claimer
from utils.logger import logger
import asyncio
import json

with open("abi/claimer_abi.json", "r", encoding="utf-8") as f:
    CLAIMER_ABI = json.load(f)


async def main():
    try:
        logger.info("🚀 Запуск скрипта...\n")
        # Загрузка параметров
        logger.info("⚙️ Загрузка и валидация параметров...\n")
        validator = ConfigValidator("config/settings.json")
        settings = await validator.validate_config()

        with open("constants/constants.json", "r", encoding="utf-8") as file:
            constants = json.load(file)

        # Инициализация клиента
        client = Client(
            proxy=settings["proxy"],
            amount=settings["amount"],
            rpc_url=constants["rpc_url"],
            chain_id=constants["chain_id"],
            private_key=settings["private_key"],
            explorer_url=constants["explorer_url"],
            contract_address=constants["contract_address"]
        )

        # Инициализация контракта
        claimer_contract = await client.get_contract(client.contract_address, CLAIMER_ABI)

        # Инициализация клеймера
        claimer = Claimer(client, claimer_contract)

        # Поиск адреса в списке зарегистрированных
        result = await claimer_contract.functions.registeredUsers(client.address).call()
        if not result:
            # Регистрация пользователя
            register = await claimer.register()
            if register:
                logger.info(f"✅ Адрес успешно зарегистрирован на клейм!\n")
            else:
                logger.error(f"❌ Не удалось зарегистрировать адрес!\n")

        # Проверка доступных токенов
        amount_in_wei = await client.to_wei_main(client.amount)
        tokens = await claimer_contract.functions.claimableTokens(client.address).call()
        if tokens == 0:
            logger.error(f"❗️ Запас токенов исчерпан!")
            exit(1)
        if tokens < amount_in_wei:
            logger.error(f"❗️ Введите меньшее значение для клейма!"
                         f" Остаток токенов {await client.from_wei_main(tokens)}.")
            exit(1)

        # Клейм токенов
        claim = await claimer.claim()
        if claim:
            logger.info(f"✅ Успешно заклейили {client.amount} токена!")

    except Exception as e:
        logger.error(f"Произошла ошибка в основном пути: {e}")


if __name__ == "__main__":
    asyncio.run(main())
