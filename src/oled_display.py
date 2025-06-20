from luma.core.interface.serial import spi
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

class OLEDDisplay:
    def __init__(self, spi_port, spi_device, gpio_dc, gpio_rst):
        serial = spi(port=spi_port, device=spi_device, gpio_DC=gpio_dc, gpio_RST=gpio_rst)
        self.device = ssd1306(serial)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 16)
        except:
            self.font = ImageFont.load_default()

    def show_status(self, username, status):
        image = Image.new('1', (self.device.width, self.device.height), "BLACK")
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), f"User: {username}", font=self.font, fill=255)
        draw.text((0, 24), f"Status: {status}", font=self.font, fill=255)
        self.device.display(image)