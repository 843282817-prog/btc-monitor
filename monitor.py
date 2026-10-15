import time
import pandas as pd
import requests


def get_candles(inst_id="BTC-USDT", bar="4H", limit=50):
  """从 OKX 获取 K 线数据"""
  url = f"https://www.okx.com/api/v5/market/candles?instId={inst_id}&bar={bar}&limit={limit}"
  try:
    res = requests.get(url, timeout=10).json()
    if res.get("code") == "0" and res.get("data"):
      df = pd.DataFrame(
          res["data"],
          columns=[
              "time",
              "open",
              "high",
              "low",
              "close",
              "vol",
              "volCcy",
              "volCcyQuote",
              "sod",
          ],
      )
      for col in ["open", "high", "low", "close", "vol"]:
        df[col] = df[col].astype(float)
      df["time"] = pd.to_numeric(df["time"])
      df = df.sort_values("time").reset_index(drop=True)
      return df
  except Exception as e:
    print(f"获取 {bar} 数据失败: {e}")
  return None


def calculate_macd(df, fast=12, slow=26, signal=9):
  """计算 MACD 指标"""
  exp1 = df["close"].ewm(span=fast, adjust=False).mean()
  exp2 = df["close"].ewm(span=slow, adjust=False).mean()
  df["macd_dif"] = exp1 - exp2
  df["macd_dea"] = df["macd_dif"].ewm(span=signal, adjust=False).mean()
  df["macd_hist"] = 2 * (df["macd_dif"] - df["macd_dea"])
  return df


def check_strategy():
  print("=== 开始执行 BTC 复合策略扫描 ===")

  # 1. 获取 4H 数据检测 MACD 底背离
  df_4h = get_candles("BTC-USDT", "4H", limit=50)
  if df_4h is not None:
    df_4h = calculate_macd(df_4h)
    recent_low_price = df_4h["close"].iloc[-1] < df_4h["close"].iloc[-10:-2].min()
    recent_higher_macd = (
        df_4h["macd_dif"].iloc[-1] > df_4h["macd_dif"].iloc[-10:-2].min()
    )
    macd_divergence = recent_low_price and recent_higher_macd
  else:
    macd_divergence = False

  # 2. 获取 1H 数据检测均线金叉及放量收回
  df_1h = get_candles("BTC-USDT", "1H", limit=50)
  if df_1h is not None:
    df_1h["ma_fast"] = df_1h["close"].ewm(span=7, adjust=False).mean()
    df_1h["ma_slow"] = df_1h["close"].ewm(span=30, adjust=False).mean()

    ma_golden_cross = (
        df_1h["ma_fast"].iloc[-2] <= df_1h["ma_slow"].iloc[-2]
    ) and (df_1h["ma_fast"].iloc[-1] > df_1h["ma_slow"].iloc[-1])

    avg_vol = df_1h["vol"].iloc[-21:-1].mean()
    current_vol = df_1h["vol"].iloc[-1]
    is_high_volume = current_vol > (avg_vol * 2)

    recent_support = df_1h["low"].iloc[-6:-1].min()
    is_break_and_recover = (df_1h["low"].iloc[-1] < recent_support) and (
        df_1h["close"].iloc[-1] > df_1h["open"].iloc[-1]
    )

    volume_recovery = is_high_volume and is_break_and_recover
  else:
    ma_golden_cross = False
    volume_recovery = False

  print(f"[4H MACD 底背离状态]: {macd_divergence}")
  print(f"[1H 均线金叉状态]: {ma_golden_cross}")
  print(f"[1H 放量跌破收回状态]: {volume_recovery}")

  if macd_divergence and ma_golden_cross and volume_recovery:
    msg = (
        "🚨 【BTC 策略触发提醒】\n"
        "满足条件：4H出现MACD底背离 + 1H均线金叉 + 1H放量跌破收回！\n"
        "请及时人工复核盘面寻找机会！"
    )
    print(msg)
  else:
    print("当前未同时满足所有策略条件，继续潜伏监控...")


if __name__ == "__main__":
  check_strategy()
