"""
messages.py

Copyright 2022 Joseph Arnusch
https://github.com/JosephVTK/jsIOn

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

RECOMMENDED_MIN_MESSAGE_LENGTH = 20
RECOMMENDED_MAX_MESSAGE_LENGTH = 75

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
                    error_messages.append(f"  --too short: {msg_text}")

            if "@" in msg_text:
                spells[message_name]['contains_colour'] = True

                if len(msg_text) > 2 and msg_text[-2] != '@' and msg_text[-1] != 'n':
                    spells[message_name]['possible_colour_bleed'] = True
                    error_messages.append(f"  --colour bleed: {msg_text}")

            if len(msg_text) > RECOMMENDED_MAX_MESSAGE_LENGTH:
                spells[message_name]['long_messages'] = True
                error_messages.append(f"  --too long: {msg_text}")

        if error_messages:
            print(f"\nIssues on {msg_object['type']}) {msg_object.get('name', 'No Name')}:")
            for error in error_messages:
                print(error)

            


with open('message_report.txt', 'w') as f:
    json.dump({ "spells" : spells }, f, indent=4)