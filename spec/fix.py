import logging
from enum import Enum
from pydantic import BaseModel, ValidationError
from typing import List
from tester import Tester


class TesterConfig(BaseModel):
    host: str
    port: int


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TesterParameter(BaseModel):
    order_type: OrderType


class FixTester(Tester):
    def __init__(self, config: TesterConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger

    @classmethod
    def get_config_model(cls):
        return TesterConfig

    @classmethod
    def get_parameter_model(cls):
        return TesterParameter

    def run_test(self, parameter: TesterParameter):
        self.logger.info(f"Host: {self.config.host}")
        self.logger.info(f"Port: {self.config.port}")
        self.logger.info(f"Order Type: {parameter.order_type}")

        for order_type in parameter.order_type:
            if order_type == OrderType.MARKET:
                self.logger.info("Market Order")
            elif order_type == OrderType.LIMIT:
                self.logger.info("Limit Order")
