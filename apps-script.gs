/**
 * קליטת פרטי מתעניינים ממסלול יום הפתוח אל גיליון Google של המכללה.
 *
 * התקנה (פעם אחת, כ-5 דקות):
 *   1. צרו גיליון Google חדש בחשבון של המכללה, למשל "מתעניינים — יום פתוח".
 *   2. בגיליון: תפריט Extensions ← Apps Script.
 *   3. מחקו את מה שיש שם, הדביקו את כל הקובץ הזה, ושמרו.
 *   4. עדכנו את NOTIFY_EMAIL למטה, או השאירו ריק כדי לא לקבל התראות.
 *   5. הריצו פעם אחת את הפונקציה setup (בחרו אותה בתפריט ולחצו Run) ואשרו הרשאות.
 *   6. Deploy ← New deployment ← Web app.
 *        Execute as:        Me
 *        Who has access:    Anyone
 *      העתיקו את כתובת ה-Web app שמתקבלת.
 *   7. שלחו את הכתובת לארז. היא נכנסת למשתנה ENDPOINT בראש index.html.
 *
 * הערה: הכתובת אינה סודית, אבל היא גם לא מפורסמת. אין בקוד הדף שום מפתח.
 */

var NOTIFY_EMAIL = '';   // למשל 'aya@cts.org.il'. ריק = בלי התראות.
var SHEET_NAME = 'מתעניינים';

var HEADERS = [
  'תאריך ושעה',
  'שם',
  'טלפון',
  'אימייל',
  'אישור יצירת קשר',
  'נוסח ההסכמה',
  'תחנות שהושלמו',
  'תשובות במסלול',
  'צילום מתחנת הפשרות',
  'מקור'
];

/** שומר את הצילום מתחנת הפשרות בתיקייה בדרייב ומחזיר קישור. */
function savePhoto(dataUrl, who) {
  if (!dataUrl || dataUrl.indexOf('base64,') < 0) return '';
  try {
    var folders = DriveApp.getFoldersByName('צילומים — יום פתוח');
    var folder = folders.hasNext() ? folders.next()
                                   : DriveApp.createFolder('צילומים — יום פתוח');
    var bytes = Utilities.base64Decode(dataUrl.split('base64,')[1]);
    var blob = Utilities.newBlob(bytes, 'image/jpeg',
      (who || 'ללא שם') + ' ' + Utilities.formatDate(new Date(), 'Asia/Jerusalem', 'yyyy-MM-dd HH-mm-ss') + '.jpg');
    return folder.createFile(blob).getUrl();
  } catch (err) {
    console.error(err);
    return '';
  }
}

/** מריצים פעם אחת אחרי ההדבקה: יוצר את הגיליון ואת שורת הכותרות. */
function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sh.setFrozenRows(1);
    sh.setRightToLeft(true);
  }
  return 'מוכן';
}

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);

    // בלי אישור מפורש לא נרשם דבר — דרישת חוק התקשורת (בזק ושידורים)
    if (!d.consent) {
      return ContentService.createTextOutput('no consent');
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) { setup(); }

    var answers = '';
    if (d.answers) {
      answers = Object.keys(d.answers)
        .map(function (k) { return k + ': ' + d.answers[k]; })
        .join(' | ');
    }

    sh.appendRow([
      new Date(),
      d.name || '',
      d.phone || '',
      d.email || '',
      'כן',
      d.consentText || '',
      d.stationsDone || 0,
      answers,
      savePhoto(d.photo, d.name),
      d.source || ''
    ]);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: 'מתעניין חדש ביום הפתוח — ' + (d.name || ''),
        body: [
          'שם: ' + (d.name || ''),
          'טלפון: ' + (d.phone || ''),
          'אימייל: ' + (d.email || '—'),
          'תחנות שהושלמו: ' + (d.stationsDone || 0),
          '',
          answers,
          '',
          'הרשומה נוספה לגיליון: ' + ss.getUrl()
        ].join('\n')
      });
    }

    return ContentService.createTextOutput('ok');
  } catch (err) {
    // לא מפילים את הבקשה — המבקר לא אמור לראות שגיאה
    console.error(err);
    return ContentService.createTextOutput('error');
  }
}

/** בדיקה מהירה שהכל עובד, בלי לפתוח את המשחק. */
function testAppend() {
  doPost({ postData: { contents: JSON.stringify({
    name: 'בדיקה', phone: '050-0000000', email: '', consent: true,
    consentText: 'בדיקה', stationsDone: 3,
    answers: { 'גובה העיניים': 162 }, source: 'בדיקה ידנית'
  }) } });
}
