import os
import re
import time
from PIL import Image as PilImage
import qrcode
import qrcode.image.svg
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask  
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer, 
    RoundedModuleDrawer, 
    GappedSquareModuleDrawer
)

from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem

# Attempt to import share from plyer
try:
    from plyer import share
except ImportError:
    share = None

KV = '''
#:import MDTopAppBar kivymd.uix.toolbar.MDTopAppBar
ScreenManager:
    Screen:
        name: "generator"
        BoxLayout:
            orientation: 'vertical'
            
            MDTopAppBar:
                title: "QR Code Generator"
                right_action_items: [["camera", lambda x: app.switch_to_scanner()]]
            
            ScrollView:
                MDBoxLayout:
                    id: generator_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(10)
                    spacing: dp(10)
                    
                    MDTextField:
                        id: input_data
                        hint_text: "Enter text or URL for QR code"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                    
                    MDTextField:
                        id: fg_color
                        hint_text: "Foreground color (e.g. black, #000000)"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                    
                    MDTextField:
                        id: bg_color
                        hint_text: "Background color (e.g. white, #ffffff)"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                    
                    MDTextField:
                        id: logo_path
                        hint_text: "Logo path (optional)"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(10)
                        MDLabel:
                            text: "Use Gradient:"
                            size_hint_x: 0.4
                            halign: "center"
                        MDCheckbox:
                            id: gradient_checkbox
                            size_hint_x: 0.1
                            active: False
                    
                    MDTextField:
                        id: shape
                        hint_text: "Shape (square, circle, rounded, dots)"
                        size_hint_x: 0.9
                        pos_hint: {"center_x": 0.5}
                    
                    MDRaisedButton:
                        text: "Generate QR Code"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.generate_qr_code()
                    
                    Image:
                        id: qr_image
                        source: ""
                        size_hint: (1, None)
                        height: dp(300)
                    
                    MDRaisedButton:
                        text: "Share QR Code"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.share_qr_code()
    
    Screen:
        name: "scanner"
        BoxLayout:
            orientation: "vertical"
            
            MDTopAppBar:
                title: "QR Code Scanner"
                left_action_items: [["arrow-left", lambda x: app.switch_to_generator()]]
            
            Camera:
                id: camera
                resolution: (640, 480)
                play: True
            
            MDLabel:
                id: scan_result_label
                text: "Point camera at QR code..."
                halign: "center"
                size_hint_y: None
                height: dp(40)
            
            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(10)
                padding: dp(10)
                MDRaisedButton:
                    text: "Scan Now"
                    on_release: app.scan_qr_code(manual=True)
                MDRaisedButton:
                    text: "Clear History"
                    on_release: app.clear_scan_history()
            
            ScrollView:
                MDList:
                    id: scan_history_list
'''

def sanitize_filename(text):
    """Sanitize filename by replacing unwanted characters."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text)

def generate_qr(data, filename="qrcode.png", fg_color="black", bg_color="white",
                box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_H,
                logo_path=None, gradient=False, shape="square"):
    """Generate a QR code image with optional styling and embedded logo."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    shape_styles = {
        "square": None,
        "circle": CircleModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "dots": GappedSquareModuleDrawer()
    }
    module_drawer = shape_styles.get(shape.lower(), None)
    
    if gradient:
        if module_drawer:
            img = qr.make_image(image_factory=StyledPilImage,
                                color_mask=RadialGradiantColorMask(),
                                module_drawer=module_drawer)
        else:
            img = qr.make_image(image_factory=StyledPilImage,
                                color_mask=RadialGradiantColorMask())
    else:
        if module_drawer:
            img = qr.make_image(fill_color=fg_color, back_color=bg_color,
                                module_drawer=module_drawer).convert("RGBA")
        else:
            img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGBA")
    
    if logo_path and os.path.exists(logo_path):
        logo = PilImage.open(logo_path)
        logo_size = img.size[0] // 5
        logo = logo.resize((logo_size, logo_size))
        if logo.mode != "RGBA":
            logo = logo.convert("RGBA")
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo)
    
    img.save(filename)
    return filename

class QRApp(MDApp):
    def build(self):
        self.title = "QR Code Generator & Scanner"
        self.scanner_event = None
        self.last_scan_time = 0
        self.scan_interval = 1.0  # seconds between automatic scans
        return Builder.load_string(KV)
    
    def generate_qr_code(self):
        data = self.root.ids.input_data.text.strip()
        if not data:
            self.show_dialog("Error", "Please enter text or URL.")
            return
        
        fg_color = self.root.ids.fg_color.text.strip() or "black"
        bg_color = self.root.ids.bg_color.text.strip() or "white"
        logo_path = self.root.ids.logo_path.text.strip() or None
        gradient = self.root.ids.gradient_checkbox.active
        shape = self.root.ids.shape.text.strip().lower() or "square"
        
        filename = sanitize_filename(data) + "_qr.png"
        try:
            filepath = generate_qr(data, filename=filename, fg_color=fg_color,
                                   bg_color=bg_color, logo_path=logo_path,
                                   gradient=gradient, shape=shape)
            self.root.ids.qr_image.source = filepath
            self.root.ids.qr_image.reload()
            self.show_dialog("Success", f"QR code generated and saved as {filepath}")
        except Exception as e:
            self.show_dialog("Error", str(e))
    
    def share_qr_code(self):
        """Share the generated QR code image using plyer if available."""
        source = self.root.ids.qr_image.source
        if not source or not os.path.exists(source):
            self.show_dialog("Error", "No QR code image to share. Generate one first.")
            return
        
        if share is None:
            self.show_dialog("Error", "Share functionality is not available on this platform.")
            return
        
        try:
            share.share(title="Share QR Code", text="Here is my QR Code!", filepath=source)
        except Exception as e:
            self.show_dialog("Error", f"Sharing failed: {e}")
    
    def scan_qr_code(self, manual=False):
        current_time = time.time()
        if not manual and (current_time - self.last_scan_time) < self.scan_interval:
            return  # Prevent scanning too frequently
        self.last_scan_time = current_time
        
        try:
            camera = self.root.ids.camera
            if not camera.texture:
                self.show_dialog("Error", "No camera feed available.")
                return
            texture = camera.texture
            size = texture.size
            pixels = texture.pixels
            pil_image = PilImage.frombytes(mode='RGBA', size=size, data=pixels)
            pil_image = pil_image.convert('RGB')
            
            from pyzbar.pyzbar import decode
            decoded_objects = decode(pil_image)
            if decoded_objects:
                result_text = "\n".join([obj.data.decode('utf-8') for obj in decoded_objects])
                self.root.ids.scan_result_label.text = result_text
                self.add_to_scan_history(result_text)
            else:
                self.root.ids.scan_result_label.text = "No QR code found."
        except Exception as e:
            self.show_dialog("Error", str(e))
    
    def add_to_scan_history(self, result_text):
        list_item = OneLineListItem(text=result_text)
        self.root.ids.scan_history_list.add_widget(list_item)
    
    def clear_scan_history(self):
        self.root.ids.scan_history_list.clear_widgets()
        self.root.ids.scan_result_label.text = "Scan history cleared."
    
    def switch_to_scanner(self):
        self.root.current = "scanner"
        if not self.scanner_event:
            self.scanner_event = Clock.schedule_interval(lambda dt: self.scan_qr_code(), self.scan_interval)
    
    def switch_to_generator(self):
        self.root.current = "generator"
        if self.scanner_event:
            self.scanner_event.cancel()
            self.scanner_event = None
    
    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, None), height=200)
        dialog.open()

if __name__ == '__main__':
    QRApp().run()
