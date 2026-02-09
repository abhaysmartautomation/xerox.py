from flask import Flask, request
import urllib.parse # URL ko safe banane ke liye
import datetime
import re # Number nikalne ke liye

app = Flask(__name__)

# ==========================================
# ⚙️ DUKANDAAR KI SETTINGS (Yahan Edit Karein)
# ==========================================
SHOP_UPI = "7046769047@ibl"   # 👈 Yahan apni UPI ID dalein (IMPORTANT)
SHOP_NAME = "abhay_automation"    # Dukandaar ka naam (Space mat dena)

RATE_BW = 2.0      # Black & White Rate per page
RATE_COLOR = 10.0  # Color Rate per page
RATE_BINDING = 25.0 # Spiral Binding Rate

# ==========================================
# 🕒 TIME BASED GREETING
# ==========================================
def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: return "Good Morning ☀️"
    elif 12 <= hour < 17: return "Good Afternoon 🌤️"
    elif 17 <= hour < 22: return "Good Evening 🌆"
    else: return "Hello 👋"

@app.route('/whatsapp', methods=['GET', 'POST'])
def bot():
    # WhatsAuto se message 'msg' mein aata hai
    incoming_msg = request.values.get('msg', '').lower().strip()
    
    # 1. Safety Check: Agar message khali hai
    if not incoming_msg:
        return "Bot is Running! ✅"

    greet = get_greeting()
    reply = ""

    # --- 🖨️ MAIN LOGIC START ---

    # 1. MENU (Hi/Hello)
    if incoming_msg in ['hi','hii', 'hello', 'rate', 'menu', 'start']:
        reply = (
            f"{greet}! *Welcome to {SHOP_NAME}* 🖨️\n"
            "━━━━━━━━━━━━━━━━\n"
            "Bill aur Payment QR ke liye message karein:\n\n"
            "📄 *'50 page'* (Black & White Bill)\n"
            "🌈 *'5 color'* (Color Bill)\n"
            "📘 *'Binding'* (Binding Rate)\n"
            "💰 *'Pay 50'* (Direct Payment Link)"
        )

    # 2. COLOR PRINT CALCULATION (Isse pehle check karna zaruri hai)
    elif 'color' in incoming_msg:
        try:
            # Message se number nikalo
            numbers = re.findall(r'\d+', incoming_msg)
            if numbers:
                pages = int(numbers[0])
                amount = pages * RATE_COLOR
                
                # Payment Link & QR Generator
                upi_raw = f"upi://pay?pa={SHOP_UPI}&pn={SHOP_NAME}&am={amount}&cu=INR"
                upi_safe = urllib.parse.quote(upi_raw)
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_safe}"
                
                reply = (
                    f"🌈 *Color Bill Generated:*\n"
                    f"{pages} Pages x ₹{RATE_COLOR} = *₹{int(amount)}*\n\n"
                    f"👇 *Scan to Pay (Auto-Fill):*\n"
                    f"{qr_url}"
                )
            else:
                reply = "❌ Pages ki sankhya likhein. Jaise: *5 color*"
        except Exception as e:
            reply = "❌ Error: Sahi se likhein (e.g., 5 color)"

    # 3. BLACK & WHITE CALCULATION (Agar 'color' nahi likha hai)
    elif 'page' in incoming_msg or any(char.isdigit() for char in incoming_msg):
        # Agar message mein 'binding' hai to use ignore karein yahan
        if 'binding' in incoming_msg:
            pass 
        else:
            try:
                numbers = re.findall(r'\d+', incoming_msg)
                if numbers:
                    pages = int(numbers[0])
                    amount = pages * RATE_BW
                    
                    upi_raw = f"upi://pay?pa={SHOP_UPI}&pn={SHOP_NAME}&am={amount}&cu=INR"
                    upi_safe = urllib.parse.quote(upi_raw)
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_safe}"
                    
                    reply = (
                        f"📄 *B&W Bill Generated:*\n"
                        f"{pages} Pages x ₹{RATE_BW} = *₹{int(amount)}*\n\n"
                        f"👇 *Scan to Pay (Auto-Fill):*\n"
                        f"{qr_url}"
                    )
            except:
                pass

    # 4. BINDING INFO
    if 'binding' in incoming_msg:
        # Binding ko alag se handle kiya taaki mix na ho
        reply = f"📘 *Spiral Binding Rate:*\n₹{int(RATE_BINDING)} per book (Cover included)."

    # 5. DIRECT PAYMENT (Agar koi seedha amount pay karna chahe)
    elif 'pay' in incoming_msg:
        try:
            numbers = re.findall(r'\d+', incoming_msg)
            if numbers:
                amount = int(numbers[0])
                upi_raw = f"upi://pay?pa={SHOP_UPI}&pn={SHOP_NAME}&am={amount}&cu=INR"
                upi_safe = urllib.parse.quote(upi_raw)
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_safe}"
                reply = f"💰 *Payment Link for ₹{amount}:*\n{qr_url}"
        except:
            pass

    # Agar kuch samajh na aaye aur reply khali ho
    if not reply:
        return "✨sorry i cant understand ✨
 to see prices type:'start, hi, menu, " # Chup raho

    return reply

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
