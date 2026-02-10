from flask import Flask, request, jsonify
import urllib.parse
import datetime
import re

app = Flask(__name__)

# ==========================================
# ⚙️ DUKAN SETTINGS
# ==========================================
SHOP_UPI = "7046769047@ibl"
SHOP_NAME = "Xerox Center"
RATE_SINGLE = 1.5
RATE_DOUBLE = 2
RATE_COLOR = 10.0
# Extras
PRICE_LAMINATION = 20
PRICE_FILE = 10
PRICE_PEN = 5
PRICE_STAMP = 50
PRICE_BINDING = 30

def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: return "Good Morning"
    elif 12 <= hour < 17: return "Good Afternoon"
    elif 17 <= hour < 22: return "Good Evening"
    else: return "Hello"

def get_extras_menu():
    return (
        "\n━━━━━━━━━━━━━━━━\n"
        "🛍️ *Add-ons:*\n"
        f"🛡️ Lamination: ₹{PRICE_LAMINATION}\n"
        f"📂 Plastic File: ₹{PRICE_FILE}\n"
        f"📘 Spiral Binding: ₹{PRICE_BINDING}\n"
        f"🖊️ Pen: ₹{PRICE_PEN} | 🏷️ Stamp: ₹{PRICE_STAMP}"
    )

def generate_upi_link(amount):
    safe_name = urllib.parse.quote(SHOP_NAME)
    return f"upi://pay?pa={SHOP_UPI}&pn={safe_name}&am={amount}&cu=INR"

@app.route('/whatsapp', methods=['GET', 'POST'])
def bot():
    # 1. Check karo ki request kaise aayi hai (JSON ya URL Parameters)
    incoming_msg = ""
    wants_plain_text = False # Default hum JSON bhejenge

    # Agar URL mein '?format=text' likha hai, to hum plain text bhejenge (MacroDroid ke liye)
    if request.values.get('format') == 'text':
        wants_plain_text = True

    # Message nikalna
    if request.is_json:
        data = request.get_json(silent=True)
        if data and 'message' in data:
            incoming_msg = data.get('message', '').lower().strip()
    
    if not incoming_msg:
        # MacroDroid aksar 'msg' parameter bhejta hai
        incoming_msg = request.values.get('msg', '').lower().strip()

    # --- LOGIC START ---
    special_files = ['photo', 'image', 'video', 'document', 'pdf', 'doc']
    reply_text = ""

    # File detection logic
    if incoming_msg in special_files or incoming_msg == "":
        reply_text = (
            "📂 *File Received!* ✅\n"
            "Total Pages kitne hain? (Number likhein)\n"
            "(Example: *10* ya *50*)"
        )
    else:
        greet = get_greeting()
        
        if incoming_msg in ['hi', 'hello', 'rate', 'menu', 'start']:
            reply_text = (
                f"🖨️ *{SHOP_NAME}*\n"
                f"{greet}! File bhejein, main bill bana dunga.\n\n"
                "👇 *Rates:*\n"
                f"📄 Single Side: ₹{RATE_SINGLE}\n"
                f"📄 Back-to-Back: ₹{RATE_DOUBLE}\n"
                f"🌈 Color Print: ₹{RATE_COLOR}\n"
                f"{get_extras_menu()}"
            )
        
        elif 'color' in incoming_msg:
            try:
                numbers = re.findall(r'\d+', incoming_msg)
                if numbers:
                    pages = int(numbers[0])
                    if pages > 0:
                        amount = pages * RATE_COLOR
                        pay_link = generate_upi_link(amount)
                        reply_text = (
                            f"🌈 *Color Bill Generated*\n"
                            f"Pages: {pages} | Total: *₹{int(amount)}*\n"
                            f"👇 *Tap to Pay:*\n{pay_link}"
                            f"{get_extras_menu()}"
                        )
            except: pass

        elif any(char.isdigit() for char in incoming_msg) and 'binding' not in incoming_msg:
            try:
                numbers = re.findall(r'\d+', incoming_msg)
                if numbers:
                    pages = int(numbers[0])
                    if pages > 0:
                        cost_single = int(pages * RATE_SINGLE)
                        cost_double = int(pages * RATE_DOUBLE)
                        link_single = generate_upi_link(cost_single)
                        link_double = generate_upi_link(cost_double)
                        reply_text = (
                            f"🧾 *Print Estimate (Pages: {pages})*\n"
                            "━━━━━━━━━━━━━━━━\n"
                            f"1️⃣ *Single Side:* ₹{cost_single}\n"
                            f"👉 Pay: {link_single}\n\n"
                            f"2️⃣ *Back-to-Back:* ₹{cost_double}\n"
                            f"👉 Pay: {link_double}"
                            f"{get_extras_menu()}"
                        )
            except: pass

        elif 'binding' in incoming_msg:
            reply_text = f"📘 *Binding Charge:* ₹{PRICE_BINDING} per book."

    # --- FINAL RETURN ---
    if not reply_text:
        return "" if wants_plain_text else jsonify({"reply": ""})

    # Yahan Magic Hai: MacroDroid ko Text, Baaki ko JSON
    if wants_plain_text:
        return reply_text
    else:
        return jsonify({"reply": reply_text})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
