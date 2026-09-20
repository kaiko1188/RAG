# RAG評価レポート
検索精度チェック OK: 9 / 10 問


## Q1: E-204とは何か？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.139)
  - NMシリーズ 保守技術ガイド p.2 (document_type=maintenance_guide, source=vector, score=0.125)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.118)
  - NMシリーズ 保守技術ガイド p.5 (document_type=maintenance_guide, source=vector, score=0.111)
  - NMシリーズ 保守技術ガイド p.4 (document_type=maintenance_guide, source=vector, score=0.091)
  - NMシリーズ 保守技術ガイド p.4 (document_type=maintenance_guide, source=vector, score=0.084)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- 2. 駆動系エラーの切り分け
3.1 E-204 左駆動系過負荷
左モーター電流が規定値を連続2秒超えた場合に停止します。『走行中に左へ寄る』『左輪が重い』『赤い204』
などの申告があります。...
  出典：NMシリーズ 保守技術ガイド p.2
- | コード | 正式名称 |  | 現場での呼称 | 区別 |
|---|---|---|---|---|
| E-204 | 左駆動系過負荷 |  | 204エラー / 赤い204 / 左モーター過負荷 | 停止・赤表示 |
| W-20...
  出典：NMシリーズ 保守技術ガイド p.1

---

## Q2: NM-100SのE-204の基本的な確認項目は？

- 検索精度チェック: NG
- 取得チャンクのdocument_type: ['asset_ledger', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.125)
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.124)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.5 (document_type=maintenance_guide, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.206)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.159)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.129)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- | 項目 | 条件 |
|---|---|
| 機種 | NM-100S |
| 製造ロット | L2406〜L2410 |
| FW | 3.1.0〜3.1.6 |
| 症状 | E-204が異物・積載異常なしで再発 |...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- | 機種 | 用途 | 標準LiDAR | 駆動制御基板 | FW系列 |
|---|---|---|---|---|
| NM-100 | 一般搬送 | LDS-10X | DRV-42A / DRV-42B | 3.x |
| NM-1...
  出典：NMシリーズ 保守技術ガイド p.1

---

## Q3: R-104の機種・ロット・FWは？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'case_history', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.031)
  - NMシリーズ 保守技術ガイド p.2 (document_type=maintenance_guide, source=vector, score=0.108)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.048)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.038)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.035)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.051)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- | 項目 | 条件 |
|---|---|
| 機種 | NM-100S |
| 製造ロット | L2406〜L2410 |
| FW | 3.1.0〜3.1.6 |
| 症状 | E-204が異物・積載異常なしで再発 |...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- | 優先 | 確認 |  | 判断 |
|---|---|---|---|
| 1 | 積載質量 |  | 上限超過なら荷を降ろして再試験 |
| 2 | 左駆動輪の異物 |  | フィルムや紐を除去 |
| 3 | 床面・段差 |  |...
  出典：NMシリーズ 保守技術ガイド p.2
- | 顧客 | 拠点 | 機体ID | 機種 | ロット | FW | 主要交換部品 |
|---|---|---|---|---|---|---|
| 東都物流 | 有明DC | R-104 | NM-100S | L2408 | 3.1....
  出典：NMシリーズ 運用記録・サービス速報 p.1

---

## Q4: R-104はSB-2026-014の対象か？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'case_history', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.160)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.282)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.050)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.025)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.025)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.083)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- | 機体ID | 予定 |  | 期限 | 理由 |  |
|---|---|---|---|---|---|
| R-104 | FW 3.2.1更新 |  | 2026-04-10 | SB-2026-014対象候補 |  |
| M-...
  出典：NMシリーズ 運用記録・サービス速報 p.1
- | 顧客 | 拠点 | 機体ID | 機種 | ロット | FW | 主要交換部品 |
|---|---|---|---|---|---|---|
| 東都物流 | 有明DC | R-104 | NM-100S | L2408 | 3.1....
  出典：NMシリーズ 運用記録・サービス速報 p.1

---

## Q5: R-104でE-204が再発した場合、最初に何をするべきか？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['case_history', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.182)
  - NMシリーズ 保守技術ガイド p.5 (document_type=maintenance_guide, source=vector, score=0.131)
  - NMシリーズ 保守技術ガイド p.2 (document_type=maintenance_guide, source=vector, score=0.081)
  - NMシリーズ 保守技術ガイド p.2 (document_type=maintenance_guide, source=vector, score=0.063)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.058)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.085)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- 5.4 締め付け・判定基準
5.5 復旧判定走行
直線10 m、左右90度旋回各2回、最大積載質量の50%での発進・停止を含むコースを3周します。E-204、E-240
、W-204が再発せず、電流値と停止位置が基準内であることを確認します...
  出典：NMシリーズ 保守技術ガイド p.5
- 3.2 W-204 左駆動系一時負荷警告
負荷が0.5秒未満で解消した場合に記録され、走行を継続することがあります。同一地点で3回以上発生する場合
は段差や床面継ぎ目を確認します。別地点でも発生する場合は駆動輪の異物を確認します。...
  出典：NMシリーズ 保守技術ガイド p.2

---

## Q6: R-104にDRV-42Aを取り付けてよいか？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'case_history', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.218)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.208)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.118)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.094)
  - NMシリーズ 保守技術ガイド p.2 (document_type=maintenance_guide, source=vector, score=0.067)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.068)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- 3. 交換部品と互換条件
表中の『条件付き』は脚注条件をすべて満たす場合のみ使用可能です。外形やコネクターが一致しても、条件を
満たさない部品は使用できません。
脚注
• DRV-42Bは、FW 3.2.0以降へ更新した後に基板学習を実行す...
  出典：NMシリーズ 保守技術ガイド p.3
- | 機種 | 用途 | 標準LiDAR | 駆動制御基板 | FW系列 |
|---|---|---|---|---|
| NM-100 | 一般搬送 | LDS-10X | DRV-42A / DRV-42B | 3.x |
| NM-1...
  出典：NMシリーズ 保守技術ガイド p.1

---

## Q7: NM-100Sの適合部品は何か？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=filter, score=0.500)
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.5 (document_type=maintenance_guide, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.221)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.170)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.152)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.138)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.126)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- | 項目 | 条件 |
|---|---|
| 機種 | NM-100S |
| 製造ロット | L2406〜L2410 |
| FW | 3.1.0〜3.1.6 |
| 症状 | E-204が異物・積載異常なしで再発 |...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- | 対象 | 基板固定ねじ | 側面パネル | 無負荷電流 | 停止位置ずれ |
|---|---|---|---|---|
| NM-100 | 1.8 N·m | 2.4 N·m | 左右各2.5 A以下 | ±20 mm以内 |
|...
  出典：NMシリーズ 保守技術ガイド p.5

---

## Q8: CASE-017と同じ対応をR-104に行ってよいか？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'case_history', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.168)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.048)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.039)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.029)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.024)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.289)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- | 機体ID | 予定 |  | 期限 | 理由 |  |
|---|---|---|---|---|---|
| R-104 | FW 3.2.1更新 |  | 2026-04-10 | SB-2026-014対象候補 |  |
| M-...
  出典：NMシリーズ 運用記録・サービス速報 p.1
- | 顧客 | 拠点 | 機体ID | 機種 | ロット | FW | 主要交換部品 |
|---|---|---|---|---|---|---|
| 東都物流 | 有明DC | R-104 | NM-100S | L2408 | 3.1....
  出典：NMシリーズ 運用記録・サービス速報 p.1

---

## Q9: NM-100Sの基板交換後の無負荷電流基準は？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'maintenance_guide', 'service_bulletin']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=filter, score=0.500)
  - NMシリーズ 運用記録・サービス速報 p.3 (document_type=service_bulletin, source=vector, score=0.123)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=filter, score=0.500)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.178)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.139)
  - NMシリーズ 保守技術ガイド p.5 (document_type=maintenance_guide, source=vector, score=0.125)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.110)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.104)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- | 項目 | 条件 |
|---|---|
| 機種 | NM-100S |
| 製造ロット | L2406〜L2410 |
| FW | 3.1.0〜3.1.6 |
| 症状 | E-204が異物・積載異常なしで再発 |...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- サービス速報 SB-2026-014
NM-100S E-204再発防止措置
1. 対象
2. 事象
対象機ではFWの駆動電流補正が不適切となり、DRV-42Aへの交換後もE-204が再発することがあります。
3. 必須対応
• DRV-4...
  出典：NMシリーズ 運用記録・サービス速報 p.3
- 3. 交換部品と互換条件
表中の『条件付き』は脚注条件をすべて満たす場合のみ使用可能です。外形やコネクターが一致しても、条件を
満たさない部品は使用できません。
脚注
• DRV-42Bは、FW 3.2.0以降へ更新した後に基板学習を実行す...
  出典：NMシリーズ 保守技術ガイド p.3

---

## Q10: R-104のバッテリー交換履歴は？

- 検索精度チェック: OK
- 取得チャンクのdocument_type: ['asset_ledger', 'case_history', 'maintenance_guide']
- 取得チャンク出典:
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.094)
  - NMシリーズ 運用記録・サービス速報 p.1 (document_type=asset_ledger, source=vector, score=0.054)
  - NMシリーズ 保守技術ガイド p.1 (document_type=maintenance_guide, source=vector, score=0.037)
  - NMシリーズ 保守技術ガイド p.3 (document_type=maintenance_guide, source=vector, score=0.024)
  - NMシリーズ 保守技術ガイド p.4 (document_type=maintenance_guide, source=vector, score=0.023)
  - NMシリーズ 運用記録・サービス速報 p.2 (document_type=case_history, source=vector, score=0.063)

**回答:**

[ローカルスタブLLMによる仮の回答: 実際の生成にはOPENAI_API_KEYの設定が必要です]

- | 機体ID | 予定 |  | 期限 | 理由 |  |
|---|---|---|---|---|---|
| R-104 | FW 3.2.1更新 |  | 2026-04-10 | SB-2026-014対象候補 |  |
| M-...
  出典：NMシリーズ 運用記録・サービス速報 p.1
- | 顧客 | 拠点 | 機体ID | 機種 | ロット | FW | 主要交換部品 |
|---|---|---|---|---|---|---|
| 東都物流 | 有明DC | R-104 | NM-100S | L2408 | 3.1....
  出典：NMシリーズ 運用記録・サービス速報 p.1
- 1. 製品と情報の読み方
NMシリーズは倉庫内の定点間搬送を行う自律走行ロボットです。標準機をNM-100、センサー強化機をNM-100S
、重量物対応機をNM-200と記載します。現場ではNM-100Sを『100エス』『センサー強化型』と...
  出典：NMシリーズ 保守技術ガイド p.1

---
