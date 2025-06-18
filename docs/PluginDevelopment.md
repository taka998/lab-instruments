# プラグインの作り方

このドキュメントでは、SCPI対応機器向けのプラグイン追加手順と、`common_scpi.py` の send コマンドの仕様・注意点について説明します。

## プラグイン作成手順

1. **雛形の自動生成**

   プラグイン雛形は以下のコマンドで自動生成できます。

   ```bash
   python plugins/scripts/create_plugin.py <機器名>
   ```

   例: IM3590用

   ```bash
   python plugins/scripts/create_plugin.py im3590
   ```

   これにより `plugins/im3590/` 配下に `config.json` と `im3590_scpi.py` が生成されます。

2. **SCPIラッパーの実装**

   生成された `<機器名>_scpi.py` を編集し、機器固有のSCPIコマンドをラップするクラス・メソッドを追加します。

   例:

   ```python
   from core.scpi.common_scpi import CommonSCPI

   class IM3590SCPI(CommonSCPI):
       def set_freq(self, freq):
           self.send(f"FREQ {freq}")
   ```

3. **config.json の編集**

   必要に応じて、機器の初期化パラメータやデフォルト値を `config.json` に記載します。

4. **テスト・動作確認**

   `examples/` ディレクトリのサンプルや独自スクリプトで動作確認を行ってください。

---

## common_scpi.py の send コマンド仕様

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

---

詳細な実装例やトラブルシューティングは `docs/RequirementsAnalysis.md` も参照してください。
