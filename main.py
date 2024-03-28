'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
import cv2
import pandas as pd
from openpyxl import load_workbook
from kivy.properties import StringProperty
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
    Button:
        text: 'Export to Excel'
        size_hint_y: None
        height: '48dp'
        on_press: root.export_to_excel()
    Label:
        id: label1
        text: root.data
        height: '48dp'
''')


class CameraClick(BoxLayout):
    data = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inventory = []

    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date, and scan for QR codes.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        detect = cv2.QRCodeDetector()
        img = cv2.imread("IMG_{}.png".format(timestr))
        data, bbox, _ = detect.detectAndDecode(img)
        if data:
            item_data = data.split(',')
            if len(item_data) == 4: # Expected 4 data points
                self.inventory.append(item_data)
                self.data = f"Captured: {data}"
            else:
                self.data = "Invalid QR code format"
        else:
            self.data = "QR code not detected"
        print(self.data)

    def export_to_excel(self):
        '''
        Exports the inventory data to an Excel file.
        '''
        if self.inventory:
            df = pd.DataFrame(self.inventory, columns=['Item ID', 'Name', 'Description', 'Item Cost'])
            # This needs to be changed based on local Excel file name
            file_path = 'QuickInventory.xlsx'
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, startrow=0, index=False)
            self.data = 'Exported to {file_path}'
        else:
            self.data = 'No inventory to export' 

class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()
