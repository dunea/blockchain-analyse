import ccxt

exchange = ccxt.okx({
    'options': {
        'defaultType': 'swap',  # OKX使用swap表示永续合约
    },
    'apiKey': "5506151e-dd90-4c2e-8090-6e75ba46107c",
    'secret': "C6B142F118A207039E530B38C7C6920D",
    'password': "Aa147258.",  # OKX需要交易密码
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
