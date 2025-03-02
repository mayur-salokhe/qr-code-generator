import qrcode
import qrcode.image.svg
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, RoundedModuleDrawer, GappedSquareModuleDrawer
from PIL import Image
import csv
import os
import re
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from tkinter import Tk, filedialog, simpledialog, colorchooser

KV = '''
def sanitize_filename(text):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text)  # Replace invalid characters with '_'

def generate_qr(data, filename="qrcode.png", fg_color="black", bg_color="white", box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_H, logo_path=None, gradient=False, shape="square"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    shape_styles = {
        "square": StyledPilImage,
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "dots": GappedSquareModuleDrawer()
    }
    
    module_drawer = shape_styles.get(shape, StyledPilImage)
    
    if gradient:
        img = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask(), module_drawer=module_drawer)
    else:
        img = qr.make_image(fill_color=fg_color, back_color=bg_color, module_drawer=module_drawer).convert("RGBA")
    
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        
        # Resize logo to fit within the QR code
        logo_size = img.size[0] // 5  # 20% of QR code size
        logo = logo.resize((logo_size, logo_size))

        # Ensure logo has an alpha (transparent) channel
        if logo.mode != "RGBA":
            logo = logo.convert("RGBA")

        # Get the position for centering the logo
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

        # Paste the logo onto the QR code
        img.paste(logo, pos, mask=logo)
    
    img.save(filename)
    print(f"QR code saved as {filename}")

def generate_vcard_qr():
    full_name = input("Enter full name: ")
    organization = input("Enter organization: ")
    phone = input("Enter phone number: ")
    email = input("Enter email: ")

    vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:{full_name}
ORG:{organization}
TEL:{phone}
EMAIL:{email}
END:VCARD"""

    filename = f"{sanitize_filename(full_name)}_vcard.png"
    generate_qr(vcard_data, filename)
    print("vCard QR Code generated successfully!")

def generate_wifi_qr():
    ssid = input("Enter WiFi SSID (network name): ")
    security = input("Enter security type (WPA/WEP/None): ").upper()
    password = input("Enter WiFi password (leave empty for open network): ")

    if security not in ["WPA", "WEP", ""]:
        print("Invalid security type. Using 'WPA' as default.")
        security = "WPA"

    wifi_data = f"WIFI:S:{ssid};T:{security};P:{password};;"
    
    filename = f"{sanitize_filename(ssid)}_wifi.png"
    generate_qr(wifi_data, filename)
    print("WiFi QR Code generated successfully!")

def bulk_generate_qr_csv():
    csv_file = input("Enter CSV file path: ")
    if not os.path.exists(csv_file):
        print("File not found!")
        return
    
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if row:
                data = row[0]
                filename = f"QR_{i+1}.png"
                generate_qr(data, filename)

def bulk_generate_qr_manual():
    num_qrs = int(input("How many QR codes do you want to generate? "))
    for i in range(num_qrs):
        data = input(f"Enter data for QR code {i+1}: ")
        filename = f"QR_{i+1}.png"
        generate_qr(data, filename)

def scan_qr(image_path):
    img = cv2.imread(image_path)
    detected_barcodes = decode(img)
    for barcode in detected_barcodes:
        print("QR Code Data:", barcode.data.decode('utf-8'))
    if not detected_barcodes:
        print("No QR code detected")

def gui_generate_qr():
    root = Tk()
    root.withdraw()
    data = simpledialog.askstring("Input", "Enter text or URL to generate QR code:")
    if not data:
        return
    fg_color = colorchooser.askcolor(title="Choose Foreground Color")[1]
    bg_color = colorchooser.askcolor(title="Choose Background Color")[1]
    logo_path = filedialog.askopenfilename(title="Select Logo (Optional)")
    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("SVG files", "*.svg")])
    gradient = simpledialog.askstring("Gradient", "Use gradient color? (yes/no)").strip().lower() == "yes"
    shape = simpledialog.askstring("QR Shape", "Choose shape (square, circle, rounded, dots): ").strip().lower()
    if save_path:
        generate_qr(data, filename=save_path, fg_color=fg_color, bg_color=bg_color, logo_path=logo_path if logo_path else None, gradient=gradient, shape=shape)

if __name__ == "__main__":
    choice = input("Choose an option: \n1. Generate QR Code\n2. Generate vCard QR Code\n3. Generate WiFi QR Code\n4. Bulk Generate QR Codes (CSV)\n5. Bulk Generate QR Codes (Manual Input)\n6. Scan QR Code\n7. GUI Mode\nEnter choice: ")
    if choice == "1":
        data = input("Enter text or URL: ")
        use_gradient = input("Use gradient color? (yes/no): ").strip().lower() == "yes"
        shape = input("Choose shape (square, circle, rounded, dots): ").strip().lower()
        generate_qr(data, gradient=use_gradient, shape=shape)
    elif choice == "2":
        generate_vcard_qr()
    elif choice == "3":
        generate_wifi_qr()
    elif choice == "4":
        bulk_generate_qr_csv()
    elif choice == "5":
        bulk_generate_qr_manual()
    elif choice == "6":
        image_path = input("Enter QR code image path: ")
        scan_qr(image_path)
    elif choice == "7":
        gui_generate_qr()
    else:
        print("Invalid choice.")
'''
class MainApp(MDApp):
    def __init__(self):
        super().__init__()
        self.kvs = Builder.load_string(KV)

    def build(self):
        screen = Screen()
        screen.add_widget(self.kvs)
        return screen

ma = MainApp()
ma.run()