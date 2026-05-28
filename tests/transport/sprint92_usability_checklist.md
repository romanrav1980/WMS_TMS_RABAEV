# Sprint 92 — Usability Checklist: Copy All ST Numbers to Clipboard

## Feature
Button **📋 СТ** in trip detail STs toolbar copies all visible (filtered) ST numbers
to clipboard (one per line). Shows «✓ Скопировано» green feedback for 1.8 s.

---

## Test Cases

### TC-1: Button visible
- [ ] «📋 СТ» button appears in the trip STs toolbar when a trip is selected

### TC-2: Copy all (unfiltered)
- [ ] Click «📋 СТ» with no filter active → all ST numbers copied, one per line
- [ ] Paste in Notepad confirms each ST on a separate line

### TC-3: Copy filtered subset
- [ ] Apply text filter first (e.g. "Лысьва") → only matching STs shown
- [ ] Click «📋 СТ» → only filtered STs copied (not the full list)

### TC-4: Copy with unready-only toggle
- [ ] Enable «⚠ Несобр.» toggle → click «📋 СТ» → only unready STs copied

### TC-5: Feedback animation
- [ ] After click: button turns green and shows «✓ Скопировано»
- [ ] After ~1.8 s: button reverts to «📋 СТ» grey state automatically

### TC-6: Reset on trip switch
- [ ] While button is in «✓ Скопировано» state, select another trip → button resets to default state

### TC-7: Edge case — single ST
- [ ] Trip with one ST: click copies that ST number; paste confirms exactly one line

---

## Expected UX
- Button label: `📋 СТ`
- Copied state label: `✓ Скопировано`
- Tooltip: «Скопировать все номера СТ в буфер обмена»
- Green background in copied state
- No page reload; instant clipboard write
