# lab-instruments

# LCRメーター接続

```python
with lab_instruments.connect(dev="im3590") as lcr:
print(lcr.idn())
lcr.set_freq(1000)
result = lcr.measure()
print(f"測定結果: {result}")
```

## 🔧 高度な使用法

## 🔗 主な依存ライブラリ

研究室向け計測機器制御ライブラリ - **統一API**でSCPI対応機器を簡単制御

## ✨ 特徴

- **統一エントリポイント** - `lab_instruments.connect()` で全ての機器に対応
- **完全な型安全性** - IDE補完・エラー検出サポート
- **プラグイン自動検出** - 新機器は `plugins/` に追加するだけ
- **複数通信方式** - VISA/シリアル/ソケット対応
- **自動化対応** - スクリプト・測定シーケンス実行

## 🚀 クイックスタート

### インストール

```bash
uv sync
```

### 利用可能なデバイス確認

```python
import lab_instruments
print(lab_instruments.list_devices())
# ['im3590', 'plz164w', ...]
```

### 基本的な使い方

```python
import lab_instruments
```

### 新しいデバイスプラグインの追加

## 📁 プロジェクト構成

```
lab-instruments/
├── lab_instruments/     # メインパッケージ
│   ├── factory.py      # 統一ファクトリ
│   ├── registry.py     # プラグイン管理
│   ├── core/          # 通信・SCPI基盤
│   └── plugins/       # デバイスプラグイン
│       ├── im3590/    # LCRメーター
│       └── plz164w/   # 電子負荷
├── examples/          # 使用例
├── scripts/          # ユーティリティ
└── docs/            # ドキュメント
```

### 接続設定のカスタマイズ

```python
# 接続パラメータの上書き
with lab_instruments.connect(dev="im3590",
                           port="/dev/ttyUSB1",
                           baudrate=115200) as lcr:
    # 測定処理
    pass
```

### Raw接続（低レベル制御）

```python
with lab_instruments.connect(method="serial", port="/dev/ttyUSB0") as conn:
    conn.write("*IDN?")
    print(conn.read())
```

## 🛠️ 開発・拡張

```bash
python scripts/create_plugin.py <device_name>
```

### VISA アドレスの確認

```bash
python scripts/search_visa_address.py
```

### SCPI 対話シェル（デバッグ用）

```bash
python scripts/scpi_shell.py
```

## 📚 ドキュメント

- **[要件分析](docs/RequirementsAnalysis.md)** - プロジェクト全体の設計思想・アーキテクチャ
- **[使用例](examples/README.md)** - 実践的なコード例・サンプル
- **[プラグイン開発ガイド](docs/PluginDevelopment.md)** - 新機器対応の追加方法
- **[API リファレンス](docs/APIReference.md)** - 関数・クラスの詳細仕様


---

**2025年リファクタリング完了** - 統一ファクトリパターン + 完全型安全対応
