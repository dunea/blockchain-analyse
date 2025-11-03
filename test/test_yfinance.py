import pandas as pd
import yfinance as yf

if __name__ == '__main__':
    yf.set_config(proxy={
        "http": "http://sp321weaes:gDVljM64x6feY3lvt+@dc.decodo.com:10000",
        "https": "http://sp321weaes:gDVljM64x6feY3lvt+@dc.decodo.com:10000",
    })

    # 使用 yfinance 获取 BTC-USD 最近 200 根 1 分钟 K 线
    # Ticker: "BTC-USD"
    # 对于 1 分钟周期可以使用 period="200m" + interval="1m" 来尝试获取最近 200 分钟的数据
    # 作为备用方案，获取更长 period（如 "1d"）然后取最后 200 条
    ticker = yf.Ticke_r("BTC-USD")

    # 直接请求最近一天的 1 分钟间隔数据
    df = ticker.history(period="1d", interval="1m", prepost=False)

    # 取最后 200 根 k 线（若不足则返回实际条数）
    last_200 = df.tail(df.size).copy()

    # 规范化列名（可选）
    last_200 = last_200.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    # 将索引（时间）重置为列，并转换为 ISO 字符串，方便后续处理或序列化
    last_200 = last_200.reset_index()
    if isinstance(last_200.loc[0, "Datetime"] if "Datetime" in last_200.columns else last_200.loc[0, "Datetime"],
                  pd.Timestamp):
        # 不强制假设索引名，处理常见情况
        if "Datetime" in last_200.columns:
            last_200["datetime"] = last_200["Datetime"].dt.tz_convert(None).dt.strftime("%Y-%m-%dT%H:%M:%S")
            last_200 = last_200.drop(columns=["Datetime"])
        elif "index" in last_200.columns:
            last_200["datetime"] = pd.to_datetime(last_200["index"]).dt.tz_convert(None).dt.strftime(
                "%Y-%m-%dT%H:%M:%S")
            last_200 = last_200.drop(columns=["index"])
        else:
            # 常见 yfinance 返回的是以 Datetime 为列名或索引，若不匹配尝试获取第0列名作为时间列
            time_col = last_200.columns[0]
            last_200["datetime"] = pd.to_datetime(last_200[time_col]).dt.tz_convert(None).dt.strftime(
                "%Y-%m-%dT%H:%M:%S")
            last_200 = last_200.drop(columns=[time_col])
    else:
        # 如果上述判断失败，仍尝试把 index 转为列
        last_200["datetime"] = pd.to_datetime(last_200.index).tz_localize(None).strftime("%Y-%m-%dT%H:%M:%S")
        last_200 = last_200.reset_index(drop=True)

    # 只保留我们关心的字段并按时间升序排列（从旧到新）
    cols_keep = ["datetime", "open", "high", "low", "close", "volume"]
    available_cols = [c for c in cols_keep if c in last_200.columns]
    result = last_200[available_cols].sort_values("datetime").reset_index(drop=True)

    # 为避免 pandas 关于在 fillna/ffill/bfill 链中对 object dtype 下沉（downcasting）的 FutureWarning，
    # 建议先对整个 DataFrame 调用 infer_objects(copy=False) 以让 pandas 推断合理的具体 dtype，
    # 然后再对 volume 列进行替换与填充操作。
    result = result.infer_objects(copy=False)
    _vol = result["volume"].replace(0, pd.NA)
    _vol = _vol.ffill().fillna(0)
    result["volume"] = _vol

    # 如果你想保留原始列并新增一列填充后的结果，使用下面一行（把上一行注释掉）：
    # result["volume_ffill"] = result["volume"].replace(0, pd.NA).ffill().fillna(0)

    print(f"Retrieved {len(result)} candles (最多 200).")
    print(result.tail(10))  # 展示最近 10 根作为示例
