# Holder vs protocol revenue

Pull DefiLlama's two fee series for one or more protocol slugs and print the
last 30 days of protocol revenue against holder revenue.

If the two numbers match, holders are being paid. If protocol is real and
holders are zero, you are looking at a treasury option.

## Run it

```bash
python3 holder_revenue.py aave uniswap lido
```

JSON:

```bash
python3 holder_revenue.py aave --json
```

## Verify it

```bash
python3 -m unittest test_holder_revenue.py
```

## Licence

MIT
