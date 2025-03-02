# QR Code Generator & Scanner

This is a KivyMD-based mobile application that allows users to generate, customize, and scan QR codes. The app supports various QR code styles, embedded logos, color customization, and scan history tracking.

## Features
- **QR Code Generator**: Create QR codes with customizable foreground/background colors, shapes, and optional logos.
- **Gradient QR Codes**: Apply a radial gradient effect to QR codes.
- **Shape Options**: Choose from square, circle, rounded, and dotted QR code styles.
- **QR Code Scanner**: Scan QR codes using the device camera and save scan history.
- **Share QR Codes**: Share generated QR codes using the Plyer share module.
- **Scan History Management**: View and clear previously scanned QR codes.

## Technologies Used
- Python
- Kivy & KivyMD (UI framework)
- Pillow (Image processing)
- QRCode (QR code generation)
- Plyer (Cross-platform sharing functionality)
- Pyzbar (QR code scanning)

## Installation
1. Install dependencies:
   ```sh
   pip install kivy kivymd pillow qrcode[pil] plyer pyzbar
   ```
2. Run the application:
   ```sh
   python main.py
   ```

## Usage
### QR Code Generator
1. Enter text or URL in the input field.
2. (Optional) Set foreground and background colors.
3. (Optional) Provide a path to an image to use as a logo.
4. (Optional) Check "Use Gradient" for a radial gradient effect.
5. Choose a shape for the QR code (square, circle, rounded, dots).
6. Click "Generate QR Code" to create and save the QR code.
7. Click "Share QR Code" to share the generated QR code.

### QR Code Scanner
1. Switch to the "Scanner" screen.
2. Point the camera at a QR code.
3. Click "Scan Now" to detect QR codes manually.
4. The scanned result will be displayed and stored in the scan history.
5. Click "Clear History" to remove past scan results.

## Notes
- Ensure the camera permission is enabled for QR scanning.
- Sharing functionality may not work on some platforms due to Plyer limitations.

## License
This project is open-source and licensed under the MIT License.

## Author
Developed by Mayur Salokhe
