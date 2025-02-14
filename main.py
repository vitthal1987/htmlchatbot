from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import requests

class StockApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.stock_input = TextInput(hint_text="Enter Stock Name (e.g., RELIANCE)", size_hint=(1, 0.2))
        self.layout.add_widget(self.stock_input)
        
        self.analyze_button = Button(text="Analyze", size_hint=(1, 0.2))
        self.analyze_button.bind(on_press=self.analyze_stock)
        self.layout.add_widget(self.analyze_button)
        
        self.result_label = Label(text="", size_hint=(1, 0.6))
        self.layout.add_widget(self.result_label)
        
        return self.layout

    def analyze_stock(self, instance):
        stock_name = self.stock_input.text
        if not stock_name:
            self.show_popup("Error", "Please enter a stock name.")
            return
        
        # Call your Flask API or backend logic here
        response = requests.post("http://127.0.0.1:5000/get_stock_analysis", data={"stock": stock_name})
        if response.status_code == 200:
            result = response.json()
            self.result_label.text = f"RSI: {result['rsi']}\nPivot: {result['pivot']}\nSentiment: {result['sentiment']}"
        else:
            self.show_popup("Error", "Failed to fetch stock data.")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message)
        popup_button = Button(text="Close", size_hint=(1, 0.2))
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)
        popup.open()

if __name__ == "__main__":
    StockApp().run()