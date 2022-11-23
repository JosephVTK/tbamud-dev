"""
messages.py

Copyright 2022 Joseph Arnusch
https://github.com/JosephVTK/

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import json
from string import Template

HTML_TEMPLATE = Template("""
<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]>      <html class="no-js"> <!--<![endif]-->
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Messages Report</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">

    </head>
    <body class="bg-dark text-light">
        <div class="container">
        $CONTENT
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
    </body>
</html>""")

HTML_CHUNK_TEMPLATE = Template("""
    <div class="border rounded border-light shadow my-2">
    <h2 class="display-5 text-center bg-light text-dark">$NAME</h2>
    <ul>
    <li>$NUM_MSG</li>
    <li>$MISSING_MSG</li>
    <li>$CONT_COL</li>
    <li>$COL_BLD</li>
    <li>$LONG</li>
    <li>$SHORT</li>
    </ul>
    <div class="p-2 m-3 border rounded border-danger">
    <h6 class="display-6 text-warning">Issues</h6>
    <ul class="bg-warning bg-opacity-50 rounded text-dark">$ERRORS</ul>
    </div>
    </div>
    """)

# These are trivial numbers and simply here to help show the potential benefits of utilizing the JSON file system
# to, in this instance, maintain consistency across combat message length.
RECOMMENDED_MIN_MESSAGE_LENGTH = 20
RECOMMENDED_MAX_MESSAGE_LENGTH = 75

if __name__ == "__main__":
    try:
        with open('../lib/misc/messages.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No messages.json found in your lib/misc folder.")
        exit()

    spells = { }

    for msg_object in data:
        message_name = f"{msg_object['type']}) {msg_object.get('name', 'No Name')}"
        if not spells.get(message_name):
            spells[message_name] = {
                "num_messages" : 0,
                "missing_messages" : False,
                "contains_colour" : False,
                "possible_colour_bleed" : False,
                "long_messages" : False,
                "short_messages" : False,
                "errors" : []
            }

        for message_data in msg_object.get('messages', []):
            spells[message_name]['num_messages'] += 1

            error_messages = []

            for msg_text in message_data.values():
                if not msg_text or msg_text == '#':
                    spells[message_name]['missing_messages'] = True
                else:
                    if len(msg_text) < RECOMMENDED_MIN_MESSAGE_LENGTH:
                        spells[message_name]['short_messages'] = True
                        error_messages.append(f"--too short (min {RECOMMENDED_MIN_MESSAGE_LENGTH}): {msg_text} ({len(msg_text)})")

                if "\t" in msg_text:
                    spells[message_name]['contains_colour'] = True

                    if len(msg_text) > 3 and msg_text[-3] != '\\' and msg_text[-1] != 'n':
                        spells[message_name]['possible_colour_bleed'] = True
                        error_messages.append(f"--colour bleed: {msg_text}")

                if len(msg_text) > RECOMMENDED_MAX_MESSAGE_LENGTH:
                    spells[message_name]['long_messages'] = True
                    error_messages.append(f"--too long (max {RECOMMENDED_MAX_MESSAGE_LENGTH}): {msg_text} ({len(msg_text)})")

            if error_messages:
                print("")
                for error in error_messages:
                    print(f"{msg_object['type']}) {msg_object.get('name', 'No Name')}: {error}")

            spells[message_name]['errors'] += error_messages
            
    with open('message_report.json', 'w') as f:
        json.dump({ "spells" : spells }, f, indent=4)

    html_content = ""
    for spell, info in spells.items():
        errors = ""
        for e in info['errors']:
            errors += f"<li>{e}</li>"
        html_content += HTML_CHUNK_TEMPLATE.substitute(
            NAME=spell,
            NUM_MSG=f"<strong>Number of messages</strong> {info.get('num_messages', '?')}",
            MISSING_MSG=f"<strong>Missing Messages</strong> {info.get('missing_messages', '?')}",
            CONT_COL=f"<strong>Contains Color?</strong> {info.get('contains_colour', '?')}",
            COL_BLD=f"<strong class=\"{'text-danger' if info.get('possible_colour_bleed') else ''}\"> Possible Color Bleed?</strong> {info.get('possible_colour_bleed', '?')}",
            LONG=f"<strong class=\"{'text-danger' if info.get('long_messages') else ''}\"> Long Message?</strong> {info.get('long_messages', '?')}",
            SHORT=f"<strong class=\"{'text-danger' if info.get('short_messages') else ''}\"> Short Message?</strong> {info.get('short_messages', '?')}",
            ERRORS=errors
        )

    with open('message_report.html', 'w') as f:
        f.write(HTML_TEMPLATE.substitute(CONTENT=html_content))