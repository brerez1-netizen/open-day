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

/**
 * לאן נשלחת התראה על כל נרשם. אפשר כמה כתובות מופרדות בפסיק, למשל:
 *   'aya@cts.org.il, morang@cts.org.il'
 * ריק = בלי מיילים, רק שורה בגיליון.
 *
 * הערה: המייל יוצא מהחשבון שפרס את הסקריפט. המגבלה היומית היא 100 מיילים
 * בחשבון פרטי ו-1500 בחשבון ארגוני — הרבה מעבר למה שיום פתוח מייצר.
 *
 * הגיליון נשאר גם אם שולחים מייל, והוא רשת הביטחון: מייל אחד שנמחק בטעות
 * או נופל לספאם הוא ליד שאבד, ושורה בגיליון לא הולכת לשום מקום.
 */
var NOTIFY_EMAIL = 'daniel@cts.org.il';
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
      var msg = {
        to: NOTIFY_EMAIL.split(',').map(function (s) { return s.trim(); }).join(','),
        subject: 'מתעניין חדש ביום הפתוח: ' + (d.name || 'ללא שם'),
        htmlBody:
          '<div dir="rtl" style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6">' +
          '<h2 style="margin:0 0 12px">' + (d.name || 'ללא שם') + '</h2>' +
          '<p style="margin:0 0 4px"><b>טלפון:</b> <a href="tel:' + (d.phone || '') + '">' + (d.phone || '') + '</a></p>' +
          (d.email ? '<p style="margin:0 0 4px"><b>אימייל:</b> ' + d.email + '</p>' : '') +
          '<p style="margin:0 0 4px"><b>תחנות שהושלמו:</b> ' + (d.stationsDone || 0) + ' מתוך 7</p>' +
          (answers ? '<p style="margin:12px 0 4px"><b>מה ענה במסלול:</b><br>' + answers + '</p>' : '') +
          '<p style="margin:16px 0 0;color:#666;font-size:13px">אישר יצירת קשר. ' +
          'הרשומה נשמרה גם <a href="' + ss.getUrl() + '">בגיליון</a>.</p></div>'
      };
      // the photo travels with the mail, so it is readable even without Drive access
      if (d.photo && d.photo.indexOf('base64,') > 0) {
        try {
          msg.attachments = [Utilities.newBlob(
            Utilities.base64Decode(d.photo.split('base64,')[1]), 'image/jpeg',
            'הפשרה שצילם.jpg')];
        } catch (e) { console.error(e); }
      }
      MailApp.sendEmail(msg);
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
