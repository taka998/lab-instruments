研究室向け計測機器自動制御・データ取得フレームワーク  
（SCPI対応機器の統一制御・自動化・拡張プラグイン対応）

## 特徴

- VISA/シリアル/ソケット通信による機器制御
- SCPIコマンド送信・応答取得・エラーチェック
- 機器ごとのプラグインラッパーで拡張容易
- 測定データの取得・保存・ログ出力
- 測定自動化スクリプト対応

## ディレクトリ構成例

core/  
　factory.py（ファクトリ関数）  
　interfaces/（通信インターフェース）  
　scpi/（共通SCPIラッパー）  
plugins/  
　IM3590/  
　　im3590_scpi.py  
　　config.json  
examples/（使い方例）
scripts/（プラグイン雛形生成）  
docs/（ドキュメント）

## インストール

依存ライブラリ

- pyvisa
- pyserial

```bash
uv sync
```

## 使い方

ファクトリ関数 connect() で機器インスタンスを取得し、SCPIコマンドを実行できます。

```python
from core.factory import connect

with connect(dev="im3590", method="serial", port="/dev/ttyACM0") as ins:
    print(ins.idn())
    ins.set_freaq(1000)
    ins.measure()
```

## プラグイン追加・拡張

### プラグイン雛形の自動生成

プラグイン雛形はスクリプトで自動生成できます。

```bash
python plugins/scripts/create_plugin.py <機器名>
```

例: IM3590用の雛形作成

```bash
python plugins/scripts/create_plugin.py im3590
```

これにより plugins/im3590/ 配下に config.json と im3590_scpi.py が生成されます。

### VISA address の特定

You can list available VISA addresses using the following script:

```bash
python plugins/scripts/visa_address.py
```

---

詳細は docs/RequirementsAnalysis.md を参照してください。
