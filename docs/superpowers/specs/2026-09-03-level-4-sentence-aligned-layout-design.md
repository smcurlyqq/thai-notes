# Thai Notes Level 4 逐句對齊排版設計

日期：2026-09-03（Asia/Taipei）

## 問題

目前含多行內容的文法、註解與練習，把全部泰文放在一起、全部羅馬讀音放在下一大段，最後只提供一段摘要翻譯。使用者無法立即判斷每一句泰文對應哪一行讀音與哪一段譯文；手機上尤其難以閱讀。

## 已確認呈現方式

Level 4 Lessons 1–8 的所有學習內容統一採用逐句直向排列。每個最小可翻譯單位依序顯示：

1. 一句泰文原文。
2. 緊接該句的帶聲調羅馬讀音。
3. 緊接該句、預設可見的繁體中文譯文。
4. 同一列內、由既有按鈕共同展開的英文、日文與韓文譯文。

標題、說明句、例句、練習指令、題目、提示與答案都遵守相同規則。單字及既有單句主課文沿用同一結構，不增加不必要的視覺層級。

## 資料與來源完整性

- 443 個 `data-source-unit`、課次、分類、頁碼與來源順序保持不變。
- `thaiBody` 與 `romanizationBody` 保留來源文字；逐行 `zh-Hant`、`en`、`ja`、`ko` 存在 `level-4/line-translations/lesson-*.json`，三者行數與順序必須一致。
- 來源標題也作為獨立對齊列，不再讓一段摘要翻譯同時代表標題與所有內文。
- 原始 Thai heading 與 Thai body 依原順序串接後必須和現有凍結 manifest 相同；本次純排版與翻譯結構調整不得重新凍結或改寫來源原文。
- 空白行不建立內容列；來源內有意義的小節標題、編號、題目與提示不得丟棄或合併。

## HTML 結構

每個外層 `article[data-source-unit]` 繼續代表一個來源項目並顯示一次頁碼。來源項目內包含一或多個 `.sentence-row[data-content-unit]`；每個 Thai 列恰好含一個 Thai unit、羅馬讀音及四種翻譯。原始教材中少數本來就是 English 的練習提示保留成 `data-source-text`，不偽造 Thai 或重複一份假 romanization，但仍有四語翻譯。

```html
<article data-source-unit data-source-page="13–14">
  <span class="source-page">pp. 13–14</span>
  <div class="sentence-row" data-content-unit>
    <div data-thai-unit>
      <div data-thai lang="th">1) ทุกคนกินข้าวอิ่ม</div>
      <div data-romanization lang="th-Latn">1) túk-kon gin-kâao ìm</div>
    </div>
    <div data-translation="zh-Hant" lang="zh-Hant">大家都吃飽了。</div>
    <div data-translation="en" lang="en" data-extra-language>Everyone ate until full.</div>
    <div data-translation="ja" lang="ja" data-extra-language>みんなお腹いっぱい食べました。</div>
    <div data-translation="ko" lang="ko" data-extra-language>모두 배불리 먹었어요.</div>
  </div>
</article>
```

JavaScript 失效時仍顯示所有語言；JavaScript 啟動後預設只顯示繁中，既有按鈕同時控制 EN／JP／KR。羅馬讀音永遠可見。

## 視覺規則

- 使用單欄直向排列，不使用桌機左右對照表，避免手機需要橫向捲動。
- Thai、romanization、繁中之間使用較小間距；句與句之間使用分隔線與較大間距。
- 頁碼只固定在來源卡片右上方，不在每句重複。
- 文法中的用法轉折或小標可使用淡色分隔列，但小標本身仍要有羅馬讀音與逐語翻譯。
- 沿用現有 Level 4 色彩、字體與語言按鈕，不改導覽與 URL。

## 產生器與稽核

- 產生器從結構化 `bodyLines` 產生逐句 HTML，不再輸出多行 `.thai-source-body`、多行 `.romanization-source-body` 與整段摘要譯文。
- Repository 稽核逐一檢查每個來源單位的行數、行序、Thai、romanization 與四語欄位；任一缺漏、錯位或多出一行都失敗。
- Shared Thai Notes auditor 新增規則：任何含多句 Thai 的內容列、含多行 romanization 的內容列，或一個譯文對應多個句子的舊結構都視為錯誤。
- 現有來源 count／order／page／hash 驗證繼續執行，確保排版重構不造成內容遺漏或換序。

## 驗收標準

- Level 4 四個 lesson pages 不再出現「整段 Thai → 整段 romanization → 一段摘要翻譯」的結構。
- 每一句 Thai 都能在同一視覺列立即找到讀音與繁中譯文；展開後能立即找到同一句的 EN／JP／KR。
- 443 個來源單位、頁碼、分類與課本穿插順序完全不變。
- 所有來源驗證、全站 auditor、單元測試與 `git diff --check` 通過。
- 使用 MBQQ 瀏覽器逐頁驗收桌機與手機：沒有重疊或橫向捲動，預設繁中、切換後四語對齊，romanization 始終可見。
