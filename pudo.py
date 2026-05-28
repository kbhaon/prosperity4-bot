import json
from datamodel import Order, OrderDepth, TradingState

ASH_COATED_OSMIUM    = "ASH_COATED_OSMIUM"
INTARIAN_PEPPER_ROOT = "INTARIAN_PEPPER_ROOT"

POSITION_LIMITS: dict[str, int] = {
    ASH_COATED_OSMIUM:    80,
    INTARIAN_PEPPER_ROOT: 80,
}


class Trader:

    def run(self, state: TradingState) -> tuple[dict[str, list[Order]], int, str]:
        memory: dict = json.loads(state.traderData) if state.traderData else {}
        orders: dict[str, list[Order]] = {}
        conversions: int = 0

        for symbol in state.listings:
            depth    = state.order_depths.get(symbol, OrderDepth())
            position = state.position.get(symbol, 0)
            limit    = POSITION_LIMITS.get(symbol, 0)
            prod_mem = memory.get(symbol, {})

            if symbol == ASH_COATED_OSMIUM:
                result, prod_mem = self.strategy_osmium(depth, position, limit, prod_mem)
            elif symbol == INTARIAN_PEPPER_ROOT:
                result, prod_mem = self.strategy_pepper(depth, position, limit, prod_mem)
            else:
                result = []

            if result:
                orders[symbol] = result
            memory[symbol] = prod_mem

        return orders, conversions, json.dumps(memory)

    def strategy_osmium(
        self, depth: OrderDepth, position: int, limit: int, memory: dict
    ) -> tuple[list[Order], dict]:
        # implement strategy
        orders: list[Order] = []
        return orders, memory

    def strategy_pepper(
        self, depth: OrderDepth, position: int, limit: int, memory: dict
    ) -> tuple[list[Order], dict]:
        # implement strategy
        orders: list[Order] = []
        return orders, memory

    # ── Helpers ───────────────────────────────────────────────────────────────

    def best_bid(self, depth: OrderDepth) -> int | None:
        return max(depth.buy_orders) if depth.buy_orders else None

    def best_ask(self, depth: OrderDepth) -> int | None:
        return min(depth.sell_orders) if depth.sell_orders else None

    def mid_price(self, depth: OrderDepth) -> float | None:
        bid, ask = self.best_bid(depth), self.best_ask(depth)
        return (bid + ask) / 2 if bid is not None and ask is not None else None
