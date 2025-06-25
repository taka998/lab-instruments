# lab-instruments 使用例集

統一ファクトリパターンによる計測機器制御ライブラリの使用例です。

## 基本的な使用方法

```python
import lab_instruments

# LCRメーター測定
with lab_instruments.connect(dev="im3590") as lcr:
    print(lcr.idn())
    lcr.set_freq(1000)
    result = lcr.measure()
    print(f"インピーダンス: {result['Z']:.3f}Ω")

# 電子負荷測定
with lab_instruments.connect(dev="plz164w") as load:
    load.set_mode("CC")
    load.set_current(1.0)
    load.load_on()
    voltage = load.measure_voltage()
    load.load_off()
    print(f"電圧: {voltage:.3f}V")
```

## 周波数特性測定

```python
import numpy as np
import pandas as pd

def measure_frequency_response(frequencies):
    results = []
    with lab_instruments.connect(dev="im3590") as lcr:
        for freq in frequencies:
            lcr.set_freq(freq)
            measurement = lcr.measure()
            results.append({
                'frequency': freq,
                'impedance': measurement['Z'],
                'phase': measurement['theta']
            })
    return pd.DataFrame(results)

# 実行例
frequencies = np.logspace(1, 6, 50)  # 10Hz - 1MHz
df = measure_frequency_response(frequencies)
df.to_csv('frequency_response.csv', index=False)
```

## Raw接続（低レベル制御）

```python
# シリアル接続
with lab_instruments.connect(method="serial", port="/dev/ttyUSB0") as conn:
    conn.write("*IDN?")
    result = conn.read()
    print(f"機器情報: {result}")

# VISA接続
with lab_instruments.connect(method="visa", address="GPIB0::1::INSTR") as conn:
    idn = conn.query("*IDN?")
    print(f"VISA機器: {idn}")
```

## 設定のカスタマイズ

```python
# ポート設定変更
with lab_instruments.connect(dev="im3590",
                           port="/dev/ttyUSB1",
                           baudrate=115200) as lcr:
    result = lcr.measure()
```

## エラー処理

```python
try:
    with lab_instruments.connect(dev="im3590") as lcr:
        result = lcr.measure()
except ValueError as e:
    print(f"デバイスエラー: {e}")
    print(f"利用可能デバイス: {lab_instruments.list_devices()}")
except ConnectionError as e:
    print(f"接続エラー: {e}")
```

## ユーティリティスクリプト

```bash
# SCPI対話シェル
python scripts/scpi_shell.py im3590

# VISAアドレス探索
python scripts/search_visa_address.py

# プラグイン作成
python scripts/create_plugin.py keithley2400
```

## 関連ドキュメント

- [メインREADME](../README.md) - プロジェクト概要
- [開発者向けAPI](DevAPI.md) - API詳細仕様
- [プラグイン開発ガイド](PluginDevelopment.md) - 新機器対応

## ベストプラクティス

1. `with`文でリソース確実解放
2. 適切なエラーハンドリング
3. 設定の外部化
4. デバッグ時の詳細ログ活用

