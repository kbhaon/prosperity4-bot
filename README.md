# prosperity4-bot

A minimal, ready-to-extend shell for an [IMC Prosperity 4](https://prosperity.imc.com/) trading bot.

I didn't get a chance to compete in Prosperity 4 since I had other commitments, but prior to round 1 I built this skeleton and tested it with a simple EMA strategy: it implements the exact `Trader` interface Prosperity
expects, wires up per-product strategy dispatch, persists state across ticks, and
respects position limits. Drop in your strategy logic and upload — it runs as-is.

## How it works

Prosperity calls `Trader.run(state)` once per tick (per timestamp). Each call must
return three things:

```python
def run(self, state: TradingState) -> tuple[dict[str, list[Order]], int, str]:
    return orders, conversions, trader_data
```

- **`orders`** — a `dict` mapping each product symbol to a list of `Order` objects to place this tick.
- **`conversions`** — an `int` for conversion requests (left at `0` here; only some rounds use it).
- **`trader_data`** — a string the engine hands back to you on the next tick. It's how you carry state forward.

## What the shell already handles

- **Per-product dispatch.** `run` loops over every listed symbol and routes it to the
  matching strategy method (`strategy_osmium`, `strategy_pepper`). Add a branch per product.
- **Persistent memory.** `state.traderData` is decoded from JSON into a `dict` at the
  start of each tick and re-encoded at the end. Each strategy gets its own slice
  (`memory[symbol]`) to read and write — use it to remember prices, fair values,
  rolling windows, etc. between ticks.
- **Position limits.** `POSITION_LIMITS` holds Prosperity's per-product caps (exceeding
  them voids your orders for that product). Each strategy receives its limit and current
  position so it can size orders safely.
- **Order-book helpers.** `best_bid`, `best_ask`, and `mid_price` pull the obvious
  numbers off an `OrderDepth`.

## Adding a strategy

Each strategy receives the current order book, your position, the position limit, and
this product's slice of persistent memory. Return the orders to place plus the
(possibly updated) memory:

```python
def strategy_osmium(
    self, depth: OrderDepth, position: int, limit: int, memory: dict
) -> tuple[list[Order], dict]:
    orders: list[Order] = []

    fair = self.mid_price(depth)
    ask  = self.best_ask(depth)
    bid  = self.best_bid(depth)

    # Example: buy anything offered below fair, sell anything bid above it.
    if fair is not None:
        if ask is not None and ask < fair and position < limit:
            qty = min(-depth.sell_orders[ask], limit - position)
            orders.append(Order(ASH_COATED_OSMIUM, ask, qty))   # positive qty = buy
        if bid is not None and bid > fair and position > -limit:
            qty = min(depth.buy_orders[bid], limit + position)
            orders.append(Order(ASH_COATED_OSMIUM, bid, -qty))  # negative qty = sell

    return orders, memory
```

Notes on the `OrderDepth` / `Order` conventions:

- `depth.buy_orders` and `depth.sell_orders` are `{price: volume}` dicts.
- In `sell_orders`, volumes are **negative** (they represent asks you can buy into).
- An `Order(symbol, price, quantity)` with **positive** quantity is a buy, **negative** is a sell.

## Adding a new product

1. Add its symbol constant and its cap to `POSITION_LIMITS`.
2. Add an `elif symbol == ...` branch in `run` pointing at a new strategy method.
3. Implement that method following the signature above.

## Files

- `pudo.py` — the entire bot. This is the file you upload to Prosperity. 

## Running it

`pudo.py` imports `datamodel` (`Order`, `OrderDepth`, `TradingState`), which is provided
by the Prosperity platform — you don't ship it. 
