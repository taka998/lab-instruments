# lab-instruments 要件分析

### 統一ファクトリパターン（2024年リファクタリング後）

## 📋 概要

研究室で使用する各種計測機器（主にSCPI対応機器）を**統一的に制御・自動化**し、測定データの取得・管理・出力を効率化するためのPythonライブラリ。

**主な特徴：**

- 単一エントリポイント `lab_instruments.connect()` による統一接続
- プラグインベースの機器サポート
- 完全な型安全性とIDE統合
- 自動化スクリプト対応

## 想定ユーザー

- 研究者・技術者（プラグイン開発者含む）
- 測定自動化スクリプトを作成・利用するユーザー

---

## 🎯 機能要件

### コア機能

- VISA/シリアル/ソケット通信による機器接続・切断・再接続
- SCPIコマンドの送信・応答取得
- コマンド送信後の完了確認（\*OPC? など）
- エラーチェック（\*ESR? など）
- 共通SCPIコマンドセットの提供（リセット、ID取得、エラー取得等）
- 測定データの取得・保存（CSV/Excel/JSON等）
- ログ出力・操作履歴記録

### プラグイン機能

- 機器ごとのSCPIコマンドラッパー作成が容易
- よく使うコマンドセットのテンプレート化
- プラグイン自動検出・動的ロード・レジストリ管理
- 型安全なデバイス接続（自動型推論）
- 設定ファイルによる接続パラメータ管理

### スクリプト自動化

- 測定シーケンスの自動化・ステップ実行
- エラー発生時のリカバリ・通知
- 進捗・状態表示
- SCPI対話シェル（デバッグ・テスト用）
- VISA アドレス自動探索

### 非機能要件

- 拡張性（新規機器・コマンド追加が容易）
- 保守性（共通処理の抽象化、テスト容易性）
- 型安全性（IDEサポート・コード補完・エラー検出）
- ドキュメント整備（プラグイン開発ガイド等）
- 自動スタブ生成（型ヒント・IDE統合）

---

## 🔧 技術スタック

### 推奨ライブラリ

- pyvisa（VISA通信）
- pyserial（シリアル通信）
- numpy, pandas（データ処理・出力）
- loguru または logging（ログ出力）
- pytest（テスト）
- python-dotenv（設定管理、必要に応じて）

---

## 🏗️ アーキテクチャ

### 統一ファクトリパターン

- **単一エントリポイント**: `lab_instruments.connect()` 関数ですべての接続を統一
- **レジストリシステム**: プラグイン自動検出・登録・管理
- **型安全性**: 自動スタブ生成による完全な型サポート
- **設定管理**: JSON設定ファイルによる接続パラメータ管理

### レイヤー構造

```
Applications Layer (ユーザーコード)
         ↓
Factory Layer (lab_instruments.connect)
         ↓
Registry Layer (自動プラグイン管理)
         ↓
Core Layer (接続・SCPI基盤)
         ↓
Interface Layer (Serial/Socket/VISA)
```

## 今回のリファクタリングで達成されたこと

### ✅ 解決された課題

1.  **重複コードの排除**: factory.py と core/connection_factory.py の機能重複を解消
2.  **統一インターフェース**: 単一の `lab_instruments.connect()` で全ての接続を統一
3.  **型安全性の向上**: 自動スタブ生成によるIDEサポート強化
4.  **保守性の向上**: レジストリベースの管理による拡張容易性
5.  **開発体験の向上**: 手動型アノテーション不要、自動補完対応

### 🔧 技術的改善点

- **アーキテクチャの簡素化**: 2つのファクトリから1つの統一ファクトリへ
- **自動化の強化**: プラグイン検出・登録・スタブ生成の完全自動化
- **相対インポートの統一**: パッケージ内インポートの一貫性確保
- **エラーハンドリングの改善**: より分かりやすいエラーメッセージ

### 📈 今後の拡張性

- 新しいデバイスプラグインは `plugins/` に追加するだけで自動認識
- 型情報は自動生成されるためIDE統合が自動的に向上
- 設定変更はJSONファイルの編集のみで完結
- テストとドキュメントの自動生成基盤が整備済み

---

```
lab-instruments/
├── lab_instruments/
│   ├── __init__.py         # パッケージエントリポイント
│   ├── factory.py          # 統一ファクトリ関数
│   ├── registry.py         # デバイス登録管理システム
│   ├── stub_manager.py     # 自動型スタブ生成
│   ├── core/               # コア機能層
│   │   ├── connection_factory.py  # 低レベル接続作成
│   │   ├── interfaces/     # 通信インターフェース
│   │   │   ├── serial_interface.py
│   │   │   ├── socket_interface.py
│   │   │   └── visa_interface.py
│   │   └── scpi/          # 共通SCPI基盤
│   │       └── common_scpi.py
│   └── plugins/           # デバイスプラグイン
│       ├── im3590/        # IM3590 LCRメーター
│       │   ├── config.json
│       │   └── im3590_scpi.py
│       └── plz164w/       # PLZ164W 電子負荷
│           ├── config.json
│           └── plz164w_scpi.py
├── examples/              # 使用例・サンプル
│   ├── simple_example.py
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── README.md
├── scripts/               # ユーティリティスクリプト
│   ├── scpi_shell.py     # SCPI対話シェル
│   ├── create_plugin.py  # プラグイン作成ツール
│   └── search_visa_address.py
└── docs/                 # ドキュメント
```

## 注意点・設計指針

- SCPIコマンド送信後は完了確認・エラーチェックを必ず行う
- プラグイン開発者が安全・簡単にラッパーを作れるよう、共通基底クラスで処理を抽象化
- 機器固有の癖や例外処理も考慮した設計
- 型安全性を重視し、IDEでの開発体験を向上
- 設定とコードの分離による保守性向上

## 実装方針（統一ファクトリ＋レジストリシステム）

- **統一エントリポイント**: `lab_instruments.connect()` 関数で全ての機器接続を統一
- **自動プラグイン検出**: 起動時にplugins配下を自動スキャンしレジストリに登録
- **設定ファイルベース**: 各機器ディレクトリのconfig.jsonで接続パラメータを管理
- **動的型生成**: プラグイン情報から自動的に型スタブ（.pyi）を生成
- **レジストリ管理**: DeviceRegistryクラスでデバイス情報・クラス・設定を一元管理
- **型安全な接続**: 静的解析・IDE補完・ランタイム型チェックをサポート

### アーキテクチャ詳細

```
# 新しい統一アーキテクチャ
lab_instruments.connect()  ← 統一エントリポイント
 ├─ DeviceRegistry        ← プラグイン管理・型情報
 ├─ StubManager          ← 自動型スタブ生成
 └─ ConnectionFactory    ← 低レベル接続作成

# 既存の基盤構造（継承）
ConnectionInterface（抽象基底クラス: 通信インターフェース）
 ├─ SerialConnection
 ├─ SocketConnection
 └─ VisaConnection

CommonSCPI（共通SCPIコマンドラッパー）
 ├─ IM3590SCPI（LCRメーター）
 ├─ PLZ164WSCPI（電子負荷）
 └─ その他機器固有クラス
```

### 主要コンポーネント

```
# シンプルなデバイス接続
import lab_instruments

with lab_instruments.connect(dev="im3590") as lcr:
    print(lcr.idn())
    lcr.set_freq(1000)
    print(lcr.measure())
```

### 高度な使用法

#### 1. Factory Layer (`factory.py`)

```python
def connect(dev=None, method=None, **kwargs) -> Union[CommonSCPI, ConnectionInterface]:
    """統一接続関数 - デバイス固有またはRaw接続"""

def list_devices() -> list[str]:
    """利用可能デバイス一覧"""
```

#### 2. Registry System (`registry.py`)

```python
class DeviceRegistry:
    """プラグイン自動検出・登録・管理"""
    def register(name: str, device_class: Type, config_path: str)
    def auto_discover(plugins_dir: str)
    def get_typed_connect(name: str) -> Callable
```

#### 3. Stub Management (`stub_manager.py`)

```python
class StubManager:
    """自動型スタブ生成・更新管理"""
    def generate_stub()
    def update_stub_if_needed()
```

### 従来構造との比較

#### 旧アーキテクチャ

```python
# 分散した複数のファクトリ関数
from core.factory import connect
from core.connection_factory import connect  # 重複！

# 手動型アノテーション必要
with connect(dev="im3590") as ins:
    ins: IM3590SCPI  # 手動で型指定
```

#### 新アーキテクチャ

```python
# 単一エントリポイント
import lab_instruments

# 自動型推論
with lab_instruments.connect(dev="im3590") as lcr:
    # 自動的にIM3590SCPIとして認識
    lcr.set_freq(1000)  # IDE補完が効く
```

## 使用例の変化

### 基本的な使用法

```python
# 設定オーバーライド
with lab_instruments.connect(dev="im3590",
                           port="/dev/ttyUSB1",
                           baudrate=115200) as lcr:
    pass

# Raw接続
with lab_instruments.connect(method="serial", port="/dev/ttyUSB0") as conn:
    conn.write("*IDN?")
    print(conn.read())

# 型付き接続関数（自動生成）
with lab_instruments.connect_im3590() as lcr:
    pass
```

---

（本ファイルは2024年大型リファクタリング後の設計・実装・レビューの指針とする）
