import sys
import time
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt
# TODO: Get your own API key and paste it here
API_KEY = "PASTE_YOUR_OWN_OPENWEATHER_API_KEY_HERE"

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.unit = "C"
        self.recent_cities = []

        self._setup_window()
        self._create_widgets()
        self._apply_layout()
        self._apply_styles(day=True)
        self._connect_signals()

    #----------------------------------------SETUP--------------------------------------
    def _setup_window(self):
        self.setWindowTitle("Weather App")
        self.resize(430, 600)

    def _create_widgets(self):
        self.city_label = QLabel("🌍 Weather App")
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_label.setObjectName("title")
        self.unit_button = QPushButton("°C")
        self.unit_button.setFixedWidth(50)
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.city_input.setAlignment(Qt.AlignCenter)
        self.search_button = QPushButton("Get Weather")
        self.recent_box = QComboBox()
        self.recent_box.addItem("Recently searched cities")
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.emoji_label = QLabel("🌤️")
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.temp_label = QLabel("-- °C")
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.feels_label = QLabel("")
        self.feels_label.setAlignment(Qt.AlignCenter)

        self.desc_label = QLabel(
            "Welcome 👋\nEnter a city to see the current weather"
        )
        self.desc_label.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

    def _apply_layout(self):
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addWidget(self.unit_button)
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.addWidget(self.city_label)
        layout.addLayout(top_row)
        layout.addWidget(self.city_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.recent_box)
        layout.addWidget(self.time_label)
        layout.addWidget(self.emoji_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.feels_label)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    #-----------------------------------------------STYLES----------------------------------------
    def _apply_styles(self, day=True):
        if day:
            bg = "#f6c453"
            text = "#2c2c2c"
            input_bg = "#fff3e0"
        else:
            bg = "#0f172a"
            text = "#f8fafc"
            input_bg = "#1e293b"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {text};
                font-family: Calibri;
            }}

            QLabel#title {{
                font-size: 38px;
                font-weight: bold;
            }}

            QLineEdit {{
                font-size: 26px;
                padding: 12px;
                border-radius: 12px;
                background-color: {input_bg};
                color: {text};
                border: none;
            }}

            QPushButton {{
                font-size: 18px;
                padding: 10px 16px;
                border-radius: 18px;
                background-color: #1c2833;
                color: white;
                border: none;
            }}

            QPushButton:hover {{
                background-color: #2c3e50;
            }}

            QComboBox {{
                font-size: 18px;
                padding: 8px;
                border-radius: 12px;
                background-color: {input_bg};
                color: {text};
            }}

            QLabel {{
                font-size: 20px;
            }}
        """)

        self.temp_label.setStyleSheet("font-size: 72px; font-weight: bold;")
        self.emoji_label.setStyleSheet("font-size: 90px;")
        self.desc_label.setStyleSheet("font-size: 24px;")
        self.feels_label.setStyleSheet("font-size: 22px;")
        self.status_label.setStyleSheet("font-size: 18px; opacity: 0.8;")

    def _connect_signals(self):
        self.search_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)
        self.unit_button.clicked.connect(self.toggle_unit)
        self.recent_box.activated[str].connect(self.select_recent)

    #  WEATHER
    def get_weather(self):
        city = self.city_input.text().strip()
        if not city:
            self.status_label.setText("⚠️ Please enter a city name")
            return

        self.status_label.setText("⏳ Fetching weather...")
        # TODO: Replace with the actual Weather Map API URL
        url = f"PUT_API_URL_HERE/weather?q={city}&appid={API_KEY}"

        try:
            response = requests.get(url)
            data = response.json()

            if str(data.get("cod")) != "200":
                self.status_label.setText("❌ City not found")
                return

            self.display_weather(data)
            self.add_recent(city)

        except Exception:
            self.status_label.setText("❌ Network error")

    def display_weather(self, data):
        temp_k = data["main"]["temp"]
        feels_k = data["main"]["feels_like"]

        if self.unit == "C":
            temp = temp_k - 273.15
            feels = feels_k - 273.15
            unit = "°C"
        else:
            temp = (temp_k * 9/5) - 459.67
            feels = (feels_k * 9/5) - 459.67
            unit = "°F"

        self.unit_button.setText(unit)

        weather_id = data["weather"][0]["id"]
        description = data["weather"][0]["description"].capitalize()
        city_name = data["name"]
        country = data["sys"]["country"]

        current_time = data["dt"]
        sunrise = data["sys"]["sunrise"]
        sunset = data["sys"]["sunset"]

        is_day = sunrise <= current_time <= sunset
        self._apply_styles(day=is_day)

        local_time = time.strftime(
            "%I:%M %p",
            time.gmtime(current_time + data["timezone"])
        )

        self.time_label.setText(f"🕒 Local time: {local_time}")
        self.temp_label.setText(f"{temp:.1f}{unit}")
        self.feels_label.setText(f"It feels like {feels:.1f}{unit}")
        self.desc_label.setText(f"📍 {city_name}, {country}\n{description} today")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.status_label.setText("✔️ Weather updated")

    #----------------------------------------EXTRA FEATURES--------------------------------------
    def toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.get_weather()

    def add_recent(self, city):
        if city not in self.recent_cities:
            self.recent_cities.insert(0, city)
            self.recent_cities = self.recent_cities[:5]
            self.recent_box.clear()
            self.recent_box.addItem("Recently searched cities")
            self.recent_box.addItems(self.recent_cities)

    def select_recent(self, city):
        if city != "Recently searched cities":
            self.city_input.setText(city)
            self.get_weather()

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return "🌈"


def main():
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



