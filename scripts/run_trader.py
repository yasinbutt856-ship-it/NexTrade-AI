async def main():
    from shared.logger import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("trader_bot_starting")
    # TODO: Phase 3 - Subscribe to signals, execute trades


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
