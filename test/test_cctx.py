import ccxt

from src.core import settings

exchange = ccxt.okx({
    'apiKey': settings.OKX_API_KEY,
    'secret': settings.OKX_SECRET,
})
exchange.session.proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809",
}

if __name__ == '__main__':
    markets = exchange.load_markets()
    # 过滤获取所有永续合约币种
    swaps = [market for market in markets if markets[market]['type'] == 'swap']
    symbols = []
    i = 1
    for symbol in swaps:
        if not symbol.endswith('USDT'):
            continue
        symbols.append(symbol)
        i += 1

    print(symbols)
