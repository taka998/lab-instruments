# プラグイン開発ガイド（2024年リファクタリング対応版）

このドキュメントでは、新しい統一アーキテクチャにおけるSCPI対応機器のプラグイン開発手順、自動型生成、レジストリシステムの活用方法について説明します。

## 新しいアーキテクチャの特徴

### 自動化された開発フロー
- **自動プラグイン検出**: プラグインを追加するだけで自動的にレジストリに登録
- **自動型生成**: 型スタブファイル（`.pyi`）が自動生成され、IDE補完が利用可能
- **統一エントリポイント**: `lab_instruments.connect()` で全ての機器に接続
- **設定検証**: プラグインの設定ファイルが自動的に検証される

### 開発者のメリット
- コードの型安全性向上
- IDE での自動補完とエラー検出
- 設定ミスの早期発見
- テストとデバッグの効率化

## プラグイン作成手順（更新版）

1. **雛形の自動生成**

   プラグイン雛形は以下のコマンドで自動生成できます。

   ```bash
   python scripts/create_plugin.py <機器名>
   ```

   例: IM3590用

   ```bash
   python scripts/create_plugin.py im3590
   ```

   これにより `lab_instruments/plugins/im3590/` 配下に以下のファイルが生成されます：
   - `__init__.py` - パッケージ初期化ファイル
   - `config.json` - 接続設定ファイル
   - `im3590_scpi.py` - SCPI ラッパークラス

2. **SCPIラッパーの実装**

   生成された `<機器名>_scpi.py` を編集し、機器固有のSCPIコマンドをラップするメソッドを追加します。

   **新しいテンプレート例**:

   ```python
   from ...core.scpi.common_scpi import CommonSCPI

   class IM3590SCPI(CommonSCPI):
       """IM3590 LCR Meter SCPI wrapper"""
       
       def __init__(self, connection):
           super().__init__(connection)
       
       def set_freq(self, freq):
           """Set measurement frequency"""
           self.send(f"FREQ {freq}")
       
       def get_freq(self):
           """Get current measurement frequency"""
           return float(self.query("FREQ?"))
       
       def measure(self):
           """Perform measurement and return result"""
           return self.query("FETCH?")
   ```

3. **config.json の編集**

   機器の接続パラメータとデフォルト値を `config.json` に設定します。
   
   **設定例**:
   ```json
   {
     "method": "serial",
     "serial_params": {
       "port": "/dev/ttyACM0",
       "baudrate": 9600,
       "timeout": 1.0,
       "terminator": "CRLF"
     },
     "socket_params": {
       "host": "192.168.0.10",
       "port": 1234,
       "timeout": 1.0,
       "terminator": "CRLF"
     },
     "visa_params": {
       "address": "USB0::0x0000::0x0000::INSTR",
       "timeout": 1.0,
       "terminator": "CRLF"
     }
   }
   ```

4. **自動登録とスタブ生成**

   プラグインを作成すると、次回パッケージ読み込み時に自動的に：
   - レジストリに登録される
   - 型スタブファイルが更新される
   - IDE での型補完が利用可能になる

5. **テスト・動作確認**

   以下の方法で動作確認を行ってください：
   
   **基本接続テスト**:
   ```python
   import lab_instruments
   
   # デバイスが登録されているか確認
   print("Available devices:", lab_instruments.list_devices())
   
   # 接続テスト
   with lab_instruments.connect(dev="im3590") as lcr:
       print("Device ID:", lcr.idn())
       lcr.set_freq(1000)
       print("Measurement:", lcr.measure())
   ```
   
   **設定検証**:
   ```python
   # 設定の妥当性を確認
   is_valid, errors = lab_instruments.validate_device("im3590")
   print(f"Configuration valid: {is_valid}")
   if not is_valid:
       print("Errors:", errors)
   ```
## 高度なプラグイン開発

### 1. 複数接続方式への対応

```python
class IM3590SCPI(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)
        # 接続方式に応じた初期化
        self._setup_device()
    
    def _setup_device(self):
        """デバイス固有の初期化"""
        # リセットして既知の状態にする
        self.send("*RST")
        self.send("*CLS")
        
        # デフォルト設定
        self.send("FUNC:IMP Z")  # インピーダンス測定モード
```

### 2. エラーハンドリングの強化

```python
class IM3590SCPI(CommonSCPI):
    def set_freq(self, freq):
        """Set frequency with validation"""
        if not (20 <= freq <= 200000):  # IM3590の周波数範囲
            raise ValueError(f"Frequency {freq} Hz out of range (20-200000 Hz)")
        
        try:
            self.send(f"FREQ {freq}")
        except Exception as e:
            raise RuntimeError(f"Failed to set frequency: {e}")
    
    def measure_with_retry(self, max_retries=3):
        """測定をリトライ機能付きで実行"""
        for attempt in range(max_retries):
            try:
                return self.query("FETCH?")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Measurement failed after {max_retries} attempts: {e}")
                time.sleep(0.1)  # 短い待機後リトライ
```

### 3. デバイス情報の充実

```python
class IM3590SCPI(CommonSCPI):
    """IM3590 LCR Meter SCPI Interface
    
    Supported measurement parameters:
    - Impedance (Z)
    - Admittance (Y) 
    - Capacitance (C)
    - Inductance (L)
    - Resistance (R)
    - Phase angle
    
    Frequency range: 20 Hz - 200 kHz
    """
    
    MEASUREMENT_PARAMS = ['Z', 'Y', 'C', 'L', 'R', 'PHASE']
    FREQ_MIN = 20
    FREQ_MAX = 200000
    
    def get_device_info(self):
        """Get comprehensive device information"""
        return {
            'model': 'IM3590',
            'manufacturer': 'HIOKI',
            'id': self.idn(),
            'supported_params': self.MEASUREMENT_PARAMS,
            'freq_range': (self.FREQ_MIN, self.FREQ_MAX),
            'current_freq': self.get_freq(),
            'current_param': self.query("FUNC:IMP?")
        }
```

## デバッグとトラブルシューティング

### 1. プラグイン登録の確認

```python
import lab_instruments

# 登録状況の確認
print("Registered devices:", lab_instruments.list_devices())

# 詳細情報の確認
device_info = lab_instruments.get_device_info("im3590")
print("Device info:", device_info)

# 設定検証
is_valid, errors = lab_instruments.validate_device("im3590")
if not is_valid:
    print("Configuration errors:", errors)
```

### 2. レジストリとスタブの状態確認

```python
# レジストリの統計情報
registry_stats = lab_instruments.registry.get_discovery_stats()
print("Registry stats:", registry_stats)

# スタブ生成状況
stub_stats = lab_instruments.stub_manager.get_generation_stats()
print("Stub stats:", stub_stats)

# システム全体の診断
diagnosis = lab_instruments.diagnose_system()
print("System diagnosis:", diagnosis)
```

### 3. 手動でのプラグイン更新

```python
# プラグインの再検出
refresh_result = lab_instruments.refresh_plugins()
print("Refresh result:", refresh_result)

# スタブファイルの強制再生成
success = lab_instruments.stub_manager.force_regenerate()
print("Stub regeneration success:", success)
```

## ベストプラクティス

### 1. 型安全性を活用

```python
# 型ヒントを活用した開発
from typing import Union, Optional

class IM3590SCPI(CommonSCPI):
    def set_freq(self, freq: Union[int, float]) -> None:
        """型ヒント付きメソッド定義"""
        self.send(f"FREQ {freq}")
    
    def get_freq(self) -> float:
        """戻り値の型を明示"""
        return float(self.query("FREQ?"))
```

### 2. 設定ファイルの活用

```json
{
  "method": "serial",
  "serial_params": {
    "port": "/dev/ttyACM0",
    "baudrate": 9600,
    "timeout": 2.0,
    "terminator": "CRLF"
  },
  "device_specific": {
    "default_freq": 1000,
    "measurement_delay": 0.1,
    "max_retries": 3
  }
}
```

### 3. ログ活用

```python
import logging

class IM3590SCPI(CommonSCPI):
    def __init__(self, connection):
        super().__init__(connection)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def set_freq(self, freq):
        self.logger.debug(f"Setting frequency to {freq} Hz")
        self.send(f"FREQ {freq}")
        self.logger.info(f"Frequency set to {freq} Hz")
```

---

## 関連ドキュメント

- `docs/RequirementsAnalysis.md` - アーキテクチャ詳細と設計指針
- `examples/README.md` - 使用例とサンプルコード
- `examples/basic_usage.py` - 基本的な使用パターン
- `examples/advanced_usage.py` - 高度な使用例

## トラブルシューティング

よくある問題と解決方法：

1. **プラグインが認識されない**
   - ファイル名が正しいか確認（`<device>_scpi.py`）
   - クラス名が正しいか確認（`<DEVICE>SCPI`）
   - インポートパスが正しいか確認（相対インポート使用）

2. **型補完が効かない**
   - パッケージを再インポート
   - `lab_instruments.refresh_plugins()` を実行
   - IDEを再起動

3. **接続エラー**
   - `lab_instruments.validate_device()` で設定確認
   - `lab_instruments.diagnose_system()` でシステム診断
   - ログレベルをDEBUGに設定して詳細確認

---

（本ドキュメントは2024年リファクタリング後の最新仕様に基づいています）

### 仕様

- `send(command, safe=True, timeout=5.0, interval=0.1)`
  - SCPIコマンドを送信します。
  - `safe=True` の場合、`*OPC`（完了ビットセット）と `*ESR?`（イベントステータスレジスタ）で完了・エラー監視を行います。
  - コマンド送信後、`*OPC` を送信し、`*ESR?` をポーリングして完了を待ちます。
  - ESR値にエラーフラグが含まれていれば `SCPIError` を送出します。
  - `timeout` でタイムアウト秒数、`interval` でポーリング間隔を指定できます。

### 注意点

- `safe=True` で利用する場合、機器が `*OPC`/`*ESR?` に対応している必要があります。
- タイムアウト値は機器の応答速度に応じて調整してください。
- `*ESR?` の値がパースできない場合や、完了ビット以外のエラーフラグが立っている場合は例外が発生します。
- コマンドによっては完了判定が遅れる場合があるため、`interval` を適切に設定してください。
- `safe=False` では完了・エラー監視を行わず即時復帰します（高速だが安全性低下）。

### 拡張された機能（新アーキテクチャ）

新しいアーキテクチャでは、以下の追加機能が利用可能です：

- **接続プール**: 同じ設定での再接続時に接続を再利用
- **自動検証**: 接続後にデバイスIDを取得して接続を確認
- **統計情報**: 接続試行回数、成功率、エラー履歴を記録
- **診断機能**: システム全体の健全性をチェック

```python
# 接続プールを使用した高速接続
with lab_instruments.connect(dev="im3590", use_pool=True) as lcr:
    pass

# 接続検証を無効化（高速化）
with lab_instruments.connect(dev="im3590", validate_connection=False) as lcr:
    pass
```
---

詳細な実装例やトラブルシューティングは `docs/RequirementsAnalysis.md` も参照してください。
