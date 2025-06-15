# 要件分析（Requirements Analysis）

## 目的

研究室で使用する各種計測機器（主にSCPI対応機器）を統一的に制御・自動化し、測定データの取得・管理・出力を効率化する。

## 想定ユーザー

- 研究者・技術者（プラグイン開発者含む）
- 測定自動化スクリプトを作成・利用するユーザー

## 機能要件

### 1. コア機能

- VISA/シリアル通信による機器接続・切断・再接続
- SCPIコマンドの送信・応答取得
- コマンド送信後の完了確認（\*OPC? など）
- エラーチェック（\*ESR? など）
- 共通SCPIコマンドセットの提供（リセット、ID取得、エラー取得等）
- 測定データの取得・保存（CSV/Excel/JSON等）
- ログ出力・操作履歴記録

### 2. プラグイン機能

- 機器ごとのSCPIコマンドラッパー作成が容易
- よく使うコマンドセットのテンプレート化
- プラグイン自動検出・動的ロード

### 3. スクリプト自動化

- 測定シーケンスの自動化・ステップ実行
- エラー発生時のリカバリ・通知
- 進捗・状態表示

## 非機能要件

- 拡張性（新規機器・コマンド追加が容易）
- 保守性（共通処理の抽象化、テスト容易性）
- ドキュメント整備（プラグイン開発ガイド等）

## 推奨ライブラリ

- pyvisa（VISA通信）
- pyserial（シリアル通信）
- numpy, pandas（データ処理・出力）
- loguru または logging（ログ出力）
- pytest（テスト）
- python-dotenv（設定管理、必要に応じて）

## ディレクトリ構成

```
lab-instruments/
├── core/           # コア機能（通信・共通SCPI・出力）
├── plugins/        # 機器ごとのラッパー
├── scripts/        # 測定自動化スクリプト
├── docs/           # ドキュメント
└── ...             # その他管理ファイル
```

## 注意点・設計指針

- SCPIコマンド送信後は完了確認・エラーチェックを必ず行う
- プラグイン開発者が安全・簡単にラッパーを作れるよう、共通基底クラスで処理を抽象化
- 機器固有の癖や例外処理も考慮した設計

## 実装方針（ファクトリ関数＋プラグイン設定ファイル）

- コア側（core/factory.py）にファクトリ関数 `connect()` を設置し、利用者はここから機器インスタンスを取得する。
- ファクトリ関数は、plugins配下の各機器ディレクトリ（例: plugins/IM3590/）にある設定ファイル（config.json等）を参照し、通信方式や初期化パラメータ、SCPIラッパークラス名などを取得する。
- 必要に応じて該当SCPIラッパークラス（例: plugins/IM3590/im3590_scpi.py）を動的importし、設定に従いConnection/SCPIラッパーを初期化して返す。
- 機器追加や設定変更はplugins配下の設定ファイル・実装のみで完結できるため、ファクトリ関数の肥大化を防ぎ、拡張性・保守性が高い。

### クラス構造の全体像

```
ConnectionInterface（抽象基底クラス: 通信インターフェース）
 ├─ SerialConnection
 └─ SocketConnection

CommonSCPI（共通SCPIコマンドラッパー）
 └─ IM3590SCPI など（機器ごとにサブクラス）

connect()（ファクトリ関数: core/factory.py）
 └─ plugins/{dev}/config.json, {dev}_scpi.py を参照して初期化
```

### ディレクトリ例

```
core/
    factory.py
    interfaces/
        connection.py
        serial_interface.py
        socket_interface.py
    scpi/
        common_scpi.py
plugins/
    IM3590/
        im3590_scpi.py
        config.json
    ...
```

### 使い方例

```python
from core.factory import connect
with connect(dev="im3590", method="serial", port="/dev/ttyACM0") as ins:
    ins.idn()
    ins.set_freaq(1000)
    ins.measure()
```

---

（本ファイルは今後の設計・実装・レビューの指針とする）

## Advanced（発展要件）

- 機器自動検出・自動接続機能
  - 複数の通信方式（シリアル・ソケット等）を順次試行し、\*IDN?応答から機器を自動判別
  - 機器ごとの推奨通信方式・デフォルトパラメータをプラグイン側で管理
  - 機器判別後、対応するラッパークラスを自動ロード・インスタンス化  
    `inst = auto_connect()`
