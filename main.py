from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import platform
from plyer import filechooser
import yt_dlp
import threading
import os

# მომრგვალებული და ფერადი ღილაკის კლასი (ნაგულისხმევი ფერი: ბორდოსფერი)
class ModernButton(Button):
    def __init__(self, bg_color=(0.41, 0.0, 0.0, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MMApp(App):
    def build(self):
        # მთავარი ფონი (აბსოლუტური შავი: #000000)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        with self.layout.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_rect = RoundedRectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.update_bg, size=self.update_bg)

        # ლოგო 
        self.logo = Image(source='', size_hint=(1, 0.3), allow_stretch=True)
        self.layout.add_widget(self.logo)

        # ლოგოს შეცვლის ღილაკი (ბორდოსფერი)
        self.change_logo_btn = ModernButton(text='ლოგოს შეცვლა', size_hint=(1, 0.1))
        self.change_logo_btn.bind(on_press=self.choose_image)
        self.layout.add_widget(self.change_logo_btn)

        # საძიებო ველი (ძალიან მუქი ნაცრისფერი ფონი, რომ შავში არ ჩაიკარგოს. კურსორი - ბორდოსფერი)
        self.search_input = TextInput(
            hint_text='მოძებნე მუსიკა YouTube-ზე...', 
            size_hint=(1, 0.1), 
            background_color=(0.05, 0.05, 0.05, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.41, 0.0, 0.0, 1),
            multiline=False
        )
        self.layout.add_widget(self.search_input)

        # სტატუსის ტექსტი
        self.status = Label(text='მზადაა', size_hint=(1, 0.1), color=(0.8, 0.8, 0.8, 1))
        self.layout.add_widget(self.status)

        # ღილაკების პანელი (ძებნა/დაკვრა და გადმოწერა)
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        
        # მოსმენის ღილაკი (ბორდოსფერი)
        self.play_btn = ModernButton(text='▶ მოსმენა')
        self.play_btn.bind(on_press=lambda x: self.process_audio(download=False))
        btn_layout.add_widget(self.play_btn)

        # გადმოწერის ღილაკი (ოდნავ უფრო მუქი ბორდოსფერი ვიზუალური კონტრასტისთვის)
        self.download_btn = ModernButton(text='⬇ გადმოწერა', bg_color=(0.3, 0.0, 0.0, 1))
        self.download_btn.bind(on_press=lambda x: self.process_audio(download=True))
        btn_layout.add_widget(self.download_btn)

        self.layout.add_widget(btn_layout)
        self.sound = None
        self.audio_url = None
        return self.layout

    def update_bg(self, *args):
        self.bg_rect.pos = self.layout.pos
        self.bg_rect.size = self.layout.size

    def choose_image(self, instance):
        # ხსნის ტელეფონის ფაილების/გალერეის მენიუს ლოგოს ასარჩევად
        filechooser.open_file(on_selection=self.update_logo)

    def update_logo(self, selection):
        if selection:
            self.logo.source = selection[0]

    def process_audio(self, download=False):
        query = self.search_input.text
        if not query: return
        self.status.text = 'იძებნება და მუშავდება...'
        threading.Thread(target=self.fetch_yt, args=(query, download)).start()

    def fetch_yt(self, query, download):
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1'
        }
        
        if download:
            # iOS-ის Documents ფოლდერში შენახვა
            save_dir = App.get_running_app().user_data_dir
            ydl_opts['outtmpl'] = os.path.join(save_dir, '%(title)s.%(ext)s')

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if download:
                    ydl.download([query])
                    self.status.text = 'გადმოწერილია Files აპლიკაციაში!'
                else:
                    info = ydl.extract_info(query, download=False)
                    video = info['entries'][0] if 'entries' in info else info
                    self.audio_url = video['url']
                    self.status.text = f"იკვრება: {video['title']}"
                    self.play_audio(self.audio_url)
        except Exception as e:
            self.status.text = 'შეცდომა ან ვიდეო მიუწვდომელია'

    def play_audio(self, url):
        if self.sound:
            self.sound.stop()
        self.sound = SoundLoader.load(url)
        if self.sound:
            self.sound.play()

if __name__ == '__main__':
    MMApp().run()
    
