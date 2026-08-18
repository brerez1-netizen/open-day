# -*- coding: utf-8 -*-
"""Printable A4 material for the route.

shilut.html  - entry sign (the only QR), one sign per station, way-finding arrows.
               The stairs sign carries a 1:1 printed ruler so nothing has to be
               left lying around the building.
sargel.html  - the 100-250 cm measuring strip for the eye-height station,
               six pages at 1:1 that tape together.

Station text is read out of the game, so signs cannot drift from it.
"""
import io, re, sys, base64
import segno
sys.stdout.reconfigure(encoding="utf-8")

GAME = r"d:\קלוד קוד my-workspace\open-day\index.html"
LOGO = r"d:\קלוד קוד my-workspace\outputs\לוגו\logo-mark.png"
DIR = r"d:\קלוד קוד my-workspace\open-day"
BASE = "https://brerez1-netizen.github.io/open-day/"

src = io.open(GAME, encoding="utf-8").read()
names = re.findall(r'key: "\w+", name: "([^"]+)"', src)
wheres = re.findall(r'where: "([^"]+)"', src)
tasks = re.findall(r'task: "([^"]+)"', src)
assert len(names) == len(wheres) == len(tasks) == 7, (len(names), len(wheres), len(tasks))
logo_b64 = base64.b64encode(open(LOGO, "rb").read()).decode()

SHARED_CSS = '''
  :root { --teal:#009C9C; --teal-d:#00706F; --yellow:#F5D800;
          --ink:#0F1E1E; --paper:#FFFFFF; --soft:#4A5C5C; }
  * { box-sizing:border-box; }
  html, body { margin:0; padding:0; background:#DCEFEF; color:var(--ink);
    font-family: system-ui, "Segoe UI", "Arial Hebrew", Arial, sans-serif; }
  .hint { max-width:52rem; margin:0 auto; padding:1.6rem 1.2rem 0.4rem; }
  .hint h1 { font-size:1.5rem; margin:0 0 0.5rem; }
  .hint p, .hint li { color:#2C3E3E; line-height:1.6; }
  .hint ol, .hint ul { padding-inline-start:1.2rem; margin:0 0 1rem; }
  .hint button { font:inherit; font-weight:700; cursor:pointer; border:0; border-radius:6px;
    background:var(--teal); color:#fff; padding:0.8rem 1.4rem; }
  .sign { width:210mm; height:297mm; margin:1.2rem auto; background:var(--paper);
    padding:16mm 14mm; display:flex; flex-direction:column;
    box-shadow:0 2px 14px rgba(0,0,0,0.16); position:relative; overflow:hidden; }
  .logo { width:32mm; display:block; }
  .logo.sm { width:24mm; }
  @media print {
    @page { size:A4 portrait; margin:0; }
    html, body { background:#fff; }
    .no-print, .hint { display:none !important; }
    .sign { margin:0; box-shadow:none; break-after:page; page-break-after:always; }
    .sign:last-child { break-after:auto; page-break-after:auto; }
  }
'''


def qr_svg(url):
    q = segno.make(url, error="h")
    buf = io.BytesIO()
    q.save(buf, kind="svg", scale=1, border=2, dark="#0F1E1E", light=None,
           svgclass=None, lineclass=None, xmldecl=False, svgns=True)
    raw = buf.getvalue().decode("utf-8")
    m = re.search(r'width="(\d+(?:\.\d+)?)"\s*height="(\d+(?:\.\d+)?)"', raw)
    return raw.replace(m.group(0),
        'width="100%" height="100%" viewBox="0 0 ' + m.group(1) + ' ' + m.group(2) +
        '" preserveAspectRatio="xMidYMid meet"', 1)


# ================================================================ shilut.html
pages = ['''
<section class="sign entry">
  <img class="logo" src="data:image/png;base64,%s" alt="מכללת הנדסאים תל אביב">
  <div class="kick">מגמת אדריכלות ועיצוב פנים</div>
  <h1>מה הבניין הזה<br>מסתיר</h1>
  <p class="lede">שבע תחנות בתוך הבניין. בערך חצי שעה, לבד או בזוג.<br>
     אין שעת התחלה - מתחילים עכשיו, מפסיקים באמצע, וחוזרים.</p>
  <div class="qrwrap">%s</div>
  <div class="scan">סרקו כאן והתחילו</div>
  <div class="foot">סורקים פעם אחת · כל השאר עובד מהנייד</div>
</section>''' % (logo_b64, qr_svg(BASE))]

for i, nm in enumerate(names, start=1):
    pages.append('''
<section class="sign station">
  <div class="top">
    <img class="logo sm" src="data:image/png;base64,%s" alt="">
    <div class="num">%02d</div>
  </div>
  <h2>%s</h2>
  <div class="tail">ההוראות כבר אצלכם בנייד</div>
</section>''' % (logo_b64, i, nm))

for i, nm in enumerate(names, start=1):
    pages.append('''
<section class="sign way" data-dir="0">
  <div class="aimbar no-print">כיוון החץ:
    <button type="button" data-d="0">&#8593;</button>
    <button type="button" data-d="90">&#8594;</button>
    <button type="button" data-d="180">&#8595;</button>
    <button type="button" data-d="270">&#8592;</button>
  </div>
  <div class="arrow">&#8593;</div>
  <div class="wayto">לתחנה %02d</div>
  <div class="wayname">%s</div>
</section>''' % (i, nm))

SHILUT = '''<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>שילוט להדפסה</title><style>%s
  .entry { align-items:center; text-align:center; }
  .entry .kick { margin-top:8mm; font-weight:800; letter-spacing:0.12em; color:var(--teal); font-size:5.2mm; }
  .entry h1 { font-size:25mm; line-height:1.02; font-weight:800; letter-spacing:-0.03em; margin:5mm 0 0; }
  .entry .lede { font-size:5.2mm; line-height:1.55; color:var(--soft); margin:6mm 0 0; }
  .entry .foot { margin-top:auto; font-size:5mm; font-weight:700; color:var(--teal); }
  .qrwrap { width:86mm; height:86mm; margin:9mm auto 0; padding:4mm; background:#fff;
    border:1.2mm solid var(--ink); border-radius:3mm; }
  .scan { font-weight:800; font-size:5.6mm; margin-top:4mm; background:var(--yellow);
    padding:3mm 6mm; border-radius:2mm; }

  .station .top { display:flex; align-items:center; justify-content:space-between; }
  .station .num { font-size:36mm; line-height:0.85; font-weight:800; color:var(--yellow);
    -webkit-text-stroke:1.1mm var(--ink); letter-spacing:-0.04em; }
  .station h2 { font-size:26mm; line-height:1.02; font-weight:800; letter-spacing:-0.035em;
    margin:auto 0; text-align:center; }
  .station .where { display:inline-block; align-self:flex-start; background:var(--teal); color:#fff;
    font-weight:700; font-size:5mm; padding:2mm 4mm; border-radius:2mm; margin:5mm 0 0; }
  .station .task { font-size:7mm; line-height:1.5; margin:8mm 0 0; font-weight:500; }
  .station .tail { text-align:center; font-weight:800; font-size:5.2mm;
    background:var(--yellow); padding:3mm; border-radius:2mm; }

  .way { align-items:center; justify-content:center; text-align:center; }
  .way .arrow { font-size:105mm; line-height:0.8; color:var(--teal); transition:transform .15s; }
  .way[data-dir="90"] .arrow { transform:rotate(90deg); }
  .way[data-dir="180"] .arrow { transform:rotate(180deg); }
  .way[data-dir="270"] .arrow { transform:rotate(270deg); }
  .way .wayto { margin-top:8mm; font-size:9mm; font-weight:800; background:var(--yellow);
    padding:3mm 8mm; border-radius:2mm; }
  .way .wayname { margin-top:4mm; font-size:11mm; font-weight:800; letter-spacing:-0.02em; }
  .aimbar { position:absolute; top:6mm; inset-inline-start:6mm; font-size:3.6mm;
    display:flex; gap:2mm; align-items:center; color:var(--soft); }
  .aimbar button { font:inherit; font-size:5mm; cursor:pointer; border:1px solid #BCDCDC;
    background:#F3FAFA; border-radius:2mm; width:9mm; height:9mm; }
  .aimbar button:hover { background:var(--yellow); }
</style></head><body>

<div class="hint no-print">
  <h1>שילוט להדפסה</h1>
  <p>%d דפים: שלט פתיחה עם הברקוד, שבעה שלטי תחנות, ושבעה שלטי הכוונה.</p>
  <ul>
    <li>הברקוד מופיע רק בשלט הפתיחה. סורקים פעם אחת, וכל השאר עובד מהנייד.</li>
    <li>בשלטי ההכוונה - לחצו על החץ בכיוון הנכון לפני ההדפסה. הבחירה נשמרת.</li>
    <li>שלטי התחנות נושאים רק מספר וכותרת - ההוראות מגיעות מהנייד.</li>
    <li>בתחנת המדרגות משאירים סרט מדידה בשטח.</li>
    <li>הדפסה: A4 לאורך, ללא שוליים, "הדפס רקעים" מסומן.</li>
  </ul>
  <button type="button" onclick="window.print()">הדפסה</button>
</div>

%s

<script>
(function () {
  var KEY = "cts-signs-dir", saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
  Array.prototype.forEach.call(document.querySelectorAll(".way"), function (w, i) {
    if (saved[i] !== undefined) w.setAttribute("data-dir", saved[i]);
    Array.prototype.forEach.call(w.querySelectorAll(".aimbar button"), function (b) {
      b.onclick = function () {
        w.setAttribute("data-dir", b.getAttribute("data-d"));
        saved[i] = b.getAttribute("data-d");
        try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
      };
    });
  });
})();
</script>
</body></html>
''' % (SHARED_CSS, len(pages), "\n".join(pages))

io.open(DIR + r"\shilut.html", "w", encoding="utf-8").write(SHILUT)

# ================================================================ sargel.html
SEG, LO, HI = 25, 100, 250
strips = []
for lo in range(LO, HI, SEG):
    hi = lo + SEG
    ticks = []
    for mm in range(0, SEG * 10 + 1, 10):       # one tick per centimetre
        cm = lo + mm // 10
        y = SEG * 10 - mm                       # the scale grows upward
        if cm % 10 == 0:
            ticks.append('<i class="t10" style="top:%.1fmm"></i>' % y)
            ticks.append('<b style="top:%.1fmm">%d</b>' % (y, cm))
        elif cm % 5 == 0:
            ticks.append('<i class="t5" style="top:%.1fmm"></i>' % y)
            ticks.append('<s style="top:%.1fmm">%d</s>' % (y, cm))
        else:
            ticks.append('<i class="t1" style="top:%.1fmm"></i>' % y)
    strips.append('''
<section class="sign strip">
  <div class="hd"><img class="logo sm" src="data:image/png;base64,%s" alt="">
    <div class="rng">%d-%d ס״מ</div></div>
  <div class="cut top">גזרו כאן · מעל מתחבר הדף שמתחיל ב-%d</div>
  <div class="scale">%s</div>
  <div class="cut bot">גזרו כאן · מתחת מתחבר הדף שמסתיים ב-%d</div>
  <div class="calib"><span class="bar"></span><span class="lab">הפס הזה הוא 10 ס״מ - בדקו עם סרגל לפני שתולים</span></div>
</section>''' % (logo_b64, lo, hi, hi, "".join(ticks), lo))

SARGEL = '''<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>סרגל מדידה - גובה העיניים</title><style>%s
  .strip { padding:10mm 14mm; }
  .hd { display:flex; align-items:center; justify-content:space-between; }
  .rng { font-size:8mm; font-weight:800; color:var(--teal); }
  .scale { position:relative; height:250mm; width:46mm; margin:6mm 0 0 auto;
    border-inline-end:0.8mm solid var(--ink); }
  .scale i { position:absolute; inset-inline-end:0; height:0.4mm; background:var(--ink); display:block; }
  .scale i.t1 { width:5mm; }
  .scale i.t5 { width:10mm; }
  .scale i.t10 { width:20mm; height:0.8mm; background:var(--teal); }
  .scale s { position:absolute; inset-inline-end:13mm; transform:translateY(-50%%);
    text-decoration:none; font-size:4.4mm; font-weight:600; color:#7B8E8E; }
  .scale b { position:absolute; inset-inline-end:22mm; transform:translateY(-50%%);
    font-size:6mm; font-weight:800; background:var(--yellow); padding:0.5mm 2mm; border-radius:1mm; }
  .cut { position:absolute; inset-inline:8mm; font-size:3.4mm; font-weight:700; color:var(--soft);
    border-top:0.4mm dashed var(--teal); padding-top:1mm; }
  .cut.top { top:24mm; }
  .cut.bot { top:277mm; }
  .calib { position:absolute; inset-inline-start:14mm; bottom:8mm; display:flex;
    flex-direction:column; gap:1.5mm; }
  .calib .bar { display:block; width:100mm; height:3mm; background:var(--teal); }
  .calib .lab { font-size:3.4mm; font-weight:700; color:var(--soft); }
</style></head><body>

<div class="hint no-print">
  <h1>סרגל מדידה לתחנת גובה העיניים</h1>
  <p>שישה דפים שמתחברים לסרגל אחד מ-100 ועד 250 ס״מ, בגודל אמיתי, בצבעי המכללה.</p>
  <ol>
    <li>הדפיסו ב-<b>100%%</b>. חשוב לבטל "התאם לעמוד" / Fit to page, אחרת המידות לא נכונות.</li>
    <li>בכל דף יש פס טורקיז באורך 10 ס״מ בתחתית. מדדו אותו עם סרגל - אם הוא לא בדיוק 10, ההדפסה לא ב-100%%.</li>
    <li>גזרו על הקווים המקווקווים והדביקו את הדפים זה מעל זה לפי המספרים.</li>
    <li>תלו כך שהקו של <b>100</b> יהיה בדיוק מטר מהרצפה. את זה מודדים פעם אחת עם מטר.</li>
  </ol>
  <button type="button" onclick="window.print()">הדפסה</button>
</div>

%s
</body></html>
''' % (SHARED_CSS, "\n".join(strips))

io.open(DIR + r"\sargel.html", "w", encoding="utf-8").write(SARGEL)

print("shilut.html : %d pages (1 entry + %d stations + %d arrows)" % (len(pages), len(names), len(names)))
print("sargel.html : %d pages, %d-%d cm" % (len(strips), LO, HI))
