import json
import http.client
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

# Устанавливаем размер окна для тестирования
Window.size = (400, 600)

class TranslatorApp(App):
    def __init__(self):
        super().__init__()
        self.translation_result = ""
        self.translation_error = ""
        
    def build(self):
        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        
        # Заголовок
        title = Label(
            text='🌍 Переводчик',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(title)
        
        # Контейнер для выбора языков
        lang_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        
        # Исходный язык
        source_label = Label(text='Из:', size_hint_x=None, width=dp(30), font_size=dp(12))
        self.source_spinner = Spinner(
            text='Авто',
            values=['Авто', 'Русский', 'English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português', '中文', '日本語', '한국어', 'العربية', 'हिन्दी', 'Türkçe'],
            size_hint_x=0.4,
            font_size=dp(11)
        )
        
        # Кнопка смены языков
        swap_btn = Button(
            text='⇄',
            size_hint_x=None,
            width=dp(40),
            font_size=dp(16)
        )
        swap_btn.bind(on_press=self.swap_languages)
        
        # Целевой язык
        target_label = Label(text='В:', size_hint_x=None, width=dp(20), font_size=dp(12))
        self.target_spinner = Spinner(
            text='Русский',
            values=['Русский', 'English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português', '中文', '日本語', '한국어', 'العربية', 'हिन्दी', 'Türkçe'],
            size_hint_x=0.4,
            font_size=dp(11)
        )
        
        lang_layout.add_widget(source_label)
        lang_layout.add_widget(self.source_spinner)
        lang_layout.add_widget(swap_btn)
        lang_layout.add_widget(target_label)
        lang_layout.add_widget(self.target_spinner)
        
        main_layout.add_widget(lang_layout)
        
        # Поле ввода
        input_label = Label(text='Введите текст:', size_hint_y=None, height=dp(25), font_size=dp(12), halign='left')
        input_label.bind(size=input_label.setter('text_size'))
        main_layout.add_widget(input_label)
        
        self.input_text = TextInput(
            multiline=True,
            hint_text='Введите текст для перевода...',
            size_hint_y=None,
            height=dp(120),
            font_size=dp(14)
        )
        main_layout.add_widget(self.input_text)
        
        # Кнопки
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        self.translate_btn = Button(
            text='Перевести',
            font_size=dp(14),
            background_color=(0.29, 0.56, 0.89, 1)
        )
        self.translate_btn.bind(on_press=self.translate_text)
        
        clear_btn = Button(
            text='Очистить',
            font_size=dp(14),
            background_color=(0.8, 0.8, 0.8, 1)
        )
        clear_btn.bind(on_press=self.clear_text)
        
        button_layout.add_widget(self.translate_btn)
        button_layout.add_widget(clear_btn)
        main_layout.add_widget(button_layout)
        
        # Поле результата
        output_label = Label(text='Перевод:', size_hint_y=None, height=dp(25), font_size=dp(12), halign='left')
        output_label.bind(size=output_label.setter('text_size'))
        main_layout.add_widget(output_label)
        
        self.output_text = TextInput(
            multiline=True,
            readonly=True,
            hint_text='Здесь появится перевод...',
            size_hint_y=None,
            height=dp(120),
            font_size=dp(14),
            background_color=(0.95, 0.95, 0.95, 1)
        )
        main_layout.add_widget(self.output_text)
        
        # Статус
        self.status_label = Label(
            text='Готов к переводу',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(10),
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def get_lang_code(self, lang_name):
        """Получение кода языка по названию"""
        lang_map = {
            'Авто': 'auto',
            'Русский': 'ru',
            'English': 'en',
            'Español': 'es',
            'Français': 'fr',
            'Deutsch': 'de',
            'Italiano': 'it',
            'Português': 'pt',
            '中文': 'zh',
            '日本語': 'ja',
            '한국어': 'ko',
            'العربية': 'ar',
            'हिन्दी': 'hi',
            'Türkçe': 'tr'
        }
        return lang_map.get(lang_name, 'auto')
    
    def swap_languages(self, instance):
        """Смена языков местами"""
        if self.source_spinner.text == 'Авто':
            self.show_popup('Ошибка', 'Нельзя поменять местами с авто-определением')
            return
        
        source_text = self.source_spinner.text
        target_text = self.target_spinner.text
        
        # Меняем языки
        if source_text in self.target_spinner.values:
            self.target_spinner.text = source_text
        if target_text in self.source_spinner.values:
            self.source_spinner.text = target_text
        
        # Меняем тексты
        input_text = self.input_text.text
        output_text = self.output_text.text
        
        if output_text and output_text.strip():
            self.input_text.text = output_text
            self.output_text.text = input_text
    
    def translate_text(self, instance):
        """Запуск перевода"""
        text = self.input_text.text.strip()
        if not text:
            self.show_popup('Ошибка', 'Введите текст для перевода')
            return
        
        source_lang = self.get_lang_code(self.source_spinner.text)
        target_lang = self.get_lang_code(self.target_spinner.text)
        
        if source_lang == target_lang and source_lang != 'auto':
            self.show_popup('Ошибка', 'Исходный и целевой языки должны отличаться')
            return
        
        # Блокируем кнопку
        self.translate_btn.text = 'Переводим...'
        self.translate_btn.disabled = True
        self.status_label.text = 'Выполняется перевод...'
        
        # Запускаем перевод в отдельном потоке
        thread = Thread(target=self.do_translation, args=(text, source_lang, target_lang))
        thread.daemon = True
        thread.start()
        
        # Проверяем результат каждые 0.1 секунды
        Clock.schedule_interval(self.check_translation_result, 0.1)
    
    def do_translation(self, text, source_lang, target_lang):
        """Выполнение перевода в отдельном потоке"""
        try:
            conn = http.client.HTTPSConnection("deep-translate1.p.rapidapi.com")
            payload = json.dumps({
                "q": text,
                "source": source_lang,
                "target": target_lang
            })
            headers = {
                'x-rapidapi-key': "db66b9db65msh1e925d637b4e831p18d7f5jsn790bb6ed72b2",
                'x-rapidapi-host': "deep-translate1.p.rapidapi.com",
                'Content-Type': "application/json"
            }
            
            conn.request("POST", "/language/translate/v2", payload, headers)
            res = conn.getresponse()
            data = res.read()
            
            response = json.loads(data.decode("utf-8"))
            
            if 'data' in response and 'translations' in response['data']:
                translations = response['data']['translations']
                
                if 'translatedText' in translations:
                    translated_text = translations['translatedText']
                    if isinstance(translated_text, list) and len(translated_text) > 0:
                        translated_text = translated_text[0]
                    elif not isinstance(translated_text, str):
                        translated_text = str(translated_text)
                    
                    self.translation_result = translated_text
                else:
                    self.translation_error = "Поле 'translatedText' не найдено в ответе"
            else:
                self.translation_error = f"Неожиданная структура ответа: {response}"
                
        except Exception as e:
            self.translation_error = f"Ошибка перевода: {str(e)}"
    
    def check_translation_result(self, dt):
        """Проверка результата перевода"""
        if self.translation_result:
            self.output_text.text = self.translation_result
            self.status_label.text = 'Перевод выполнен'
            self.translation_result = ""
            self.restore_translate_button()
            return False
        
        if self.translation_error:
            self.show_popup('Ошибка', self.translation_error)
            self.translation_error = ""
            self.restore_translate_button()
            return False
        
        return True
    
    def restore_translate_button(self):
        """Восстановление кнопки перевода"""
        self.translate_btn.text = 'Перевести'
        self.translate_btn.disabled = False
    
    def clear_text(self, instance):
        """Очистка полей"""
        self.input_text.text = ''
        self.output_text.text = ''
        self.status_label.text = 'Поля очищены'
    
    def show_popup(self, title, message):
        """Показ всплывающего окна"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()

if __name__ == '__main__':
    TranslatorApp().run()
