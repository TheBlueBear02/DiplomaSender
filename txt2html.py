import re


def txt_to_html(txt, name, bullet_symbols=None):
    if bullet_symbols is None:
        bullet_symbols = ["💫"]  # Default bullet symbols
    
    html_template = """<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8">
</head>
<body style="direction: rtl; text-align: right; font-family: Arial, sans-serif; color: #333333; margin: 20px;">
    {}
</body>
</html>"""
    # Regex to detect URLs
    url_pattern = re.compile(r"(http[s]?://[^\s]+)")

    # Replace {{name}} with the actual name
    txt = txt.replace("{{name}}", f'<span style="color: #ff6600;">{name}</span>')

    # Split text into lines
    lines = txt.strip().split("\n")

    html_body = ""
    for line in lines:
        if line.strip() == "":  # Skip empty lines
            continue
        elif any(line.startswith(symbol) for symbol in bullet_symbols):  # Handle general bullet symbols
            html_body += f'<p style="line-height: 1.5; margin-left: 10px;">{line}</p>\n'
        elif line.startswith("-"):  # List item
            html_body += f'<li style="margin-bottom: 10px;">{line[1:].strip()}</li>\n'
        else:  # Regular paragraph
            line = url_pattern.sub(r'<a href="\1" target="_blank" style="color: #0066cc; text-decoration: none;">\1</a>', line)
            html_body += f'<p style="line-height: 1.5;">{line}</p>\n'

    # Wrap in <ul> if it contains list items
    if "<li" in html_body:
        html_body = html_body.replace('<li', '<ul style="list-style-type: none; padding: 0;"><li', 1).replace('</li>\n', '</li></ul>\n', 1)

    return html_template.format(html_body)





# Testing the function
def main():
    # Sample input text
    txt = """שלום {{name}},

שמחנו מאוד שבחרת להשתתף בקורס "כלים יצירתיים להנחיית ילדים ובני נוער להתמודדות עם חרדה, פחדים וטראומה"

שמחות להעניק לך תעודת השתתפות בקורס 😊

התעודה מצורפת ב2 פורמטים:

- בפורמט PDF להדפסה - לתלות במשרד או בקליניקה.
- וקובץ תמונה JPG - להציג בפייסבוק, באינסטגרם, ובוואטספ.

מאחלות לך בהצלחה בדרכך המקצועית והאישית
אלה גבאי ומירי יפרח.

כמו כן אנו מזמינות אותך להמשיך ולהעמיק בלימודי ה-NLP CREATIVE איתנו:

💫 קורס 'כלים יצירתיים להנחיית ילדים ובני נוער | נפתח  ב-16.2.25

נפגש ל-6 מפגשים ב-Zoom

למטפלים, למאמנים, ולאנשי חינוך וייעוץ
לקורס יישומי, מקצועי וממוקד הנותן כלים פרקטיים ויישומיים להנחיית ילדים ובני נוער.
הקורס כולל תהליכים מקוריים שיוסיפו כלים חדשים לעבודה בקליניקה ובהנחיית קבוצות.
כל הפרטים כאן: https://kenesklafim.ravpage.co.il/kidsteen0225
"""

    # Convert text to HTML
    html_output = txt_to_html(txt, "אלה גבאי")

    # Save to an HTML file
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("HTML file generated: output.html")

if __name__ == "__main__":
    main()
