

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy import platform

if platform == "android":
    is_android = True
# I plan to use this for camera orientation. It seems like on android -90 degrees rotation of camera is good, but on
# my desktop I need -180 degrees. It is also needed for file IO, desktop will have a different filepath for storage.


# Going to need to add camera logic here and image IO
class One(Screen):
    pass


# Probably retrieve image here and do qr decoding
class Two(Screen):
    pass


# This is probably where we need the Excel Exporting IO
class Three(Screen):
    pass


class Quickventory(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(One(name='One'))
        sm.add_widget(Two(name='Two'))
        sm.add_widget(Three(name='Three'))
        return sm


# When debugging the Camera Widget takes about 10 min to load, replace camera widget with an image maybe in order to
# speed it up. Also could take out the builder string and make it a file later.
Builder.load_string("""
<One>:
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1,1
        Camera:
            id: 'camera'
            play: True
            keep_ratio: False
            allow_stretch: True
            canvas.before:
                PushMatrix
                Rotate:
                    angle: -90
                    origin: self.center
            canvas.after:
                PopMatrix
    BoxLayout: 
        orientation: 'horizontal'
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'bottom'
            padding: [0,0,0,50]
            Button:
                id: '1'
                canvas.before:
                    Color:
                        rgba: .3,0,1,.2
                    Rectangle:
                        pos: self.pos
                        size: self.size
                size: 100,100
                size_hint: None, None
                on_press: root.manager.current = "Two"
                background_color: [.4,.4,.4,.3]
                background_normal: ''
        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            padding: [0,0,75,0]
            Button:
                id: '2'
                size: 100,50
                size_hint: None, None
                on_press: root.manager.current = "Three"
                background_color: [.4,.4,.4,.3]
                background_normal: ''
        
    
<Two>:
    BoxLayout:
        spacing: 10
        padding: [50,50,50,50]
        orientation: 'vertical'
        Image:
            source: 'city-skyline-silhouette.jpg'
            size: self.texture_size
            
        TextInput:
            text: "QR Code Data"
            size_hint: .75, .5
            height: 150
            width: 300
            pos_hint: {'center_x':.5, 'center_y':.5}
        BoxLayout:
            size_hint: 1, .3
            orientation: 'horizontal'
            AnchorLayout:
                anchor_x: 'left'
                anchor_y: 'bottom'
                padding: [0,0,75,0]
                Button:
                    text: 'Back'
                    on_press: root.manager.current = "One" 
                    size: 150,50
                    size_hint: None, None
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'bottom'
                Button:
                    text: 'Save to Session'
                    on_press: root.manager.current = "Three"            
                    size: 150,50
                    size_hint: None, None
                
<Three>:
    BoxLayout:
        orientation: 'vertical'
        padding: [50,50,50,50]
        TextInput:
            text: "Session Data"
            size_hint: .8, .9
            height: 600
            width: 300
            pos_hint: {'center_x':.5, 'center_y':.5}
        BoxLayout:
            size_hint: 1, .3
            orientation: 'horizontal'
            AnchorLayout:
                anchor_x: 'left'
                anchor_y: 'bottom'
                padding: [50,50,75,50]
                Button:
                    text: 'Back'
                    on_press: root.manager.current = "One" 
                    size: 150,50
                    size_hint: None, None
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'bottom'
                padding: [50,50,50,50]
                Button:
                    text: 'Save to Excel'
                    on_press: root.manager.current = "One"            
                    size: 150,50
                    size_hint: None, None
""")


if __name__ == "__main__":
    Quickventory().run()
