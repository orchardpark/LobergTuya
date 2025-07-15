import kivy
kivy.require('2.3.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, Ellipse
import random
from collections import deque
from control import KesserHeater

class HeaterIcon(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 60)
        with self.canvas:
            # Base color
            Color(0.8, 0.8, 0.8, 1)
            # Heater body (rectangle)
            Rectangle(pos=(10, 10), size=(40, 35))
            # Heater elements (horizontal lines)
            Color(1, 0.4, 0.2, 1)  # Orange/red for heating elements
            Line(points=[15, 35, 45, 35], width=2)
            Line(points=[15, 30, 45, 30], width=2)
            Line(points=[15, 25, 45, 25], width=2)
            Line(points=[15, 20, 45, 20], width=2)
            # Control knob
            Color(0.5, 0.5, 0.5, 1)
            Ellipse(pos=(35, 40), size=(10, 10))


class TemperatureGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 120
        self.temp_history = deque(maxlen=50)  # Store last 50 temperature readings
        self.set_temp_history = deque(maxlen=50)
        self.bind(size=self.update_graph, pos=self.update_graph)
    
    def add_temperature(self, current_temp, set_temp):
        self.temp_history.append(current_temp)
        self.set_temp_history.append(set_temp)
        self.update_graph()
    
    def update_graph(self, *args):
        self.canvas.clear()
        if len(self.temp_history) < 2:
            return
        
        with self.canvas:
            # Background
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Grid lines
            Color(0.3, 0.3, 0.3, 1)
            for i in range(1, 4):
                y = self.y + (self.height / 4) * i
                Line(points=[self.x, y, self.x + self.width, y], width=1)
            
            # Temperature range for scaling (10°C to 35°C)
            temp_min, temp_max = 10, 35
            temp_range = temp_max - temp_min
            
            # Draw set temperature line (dashed effect)
            if len(self.set_temp_history) >= 2:
                Color(0.8, 0.8, 0.2, 1)  # Yellow for set temperature
                points = []
                for i, temp in enumerate(self.set_temp_history):
                    x = self.x + (i / (len(self.set_temp_history) - 1)) * self.width
                    y = self.y + ((temp - temp_min) / temp_range) * self.height
                    points.extend([x, y])
                Line(points=points, width=2)
            
            # Draw current temperature line
            if len(self.temp_history) >= 2:
                Color(1, 0.4, 0.2, 1)  # Orange for current temperature
                points = []
                for i, temp in enumerate(self.temp_history):
                    x = self.x + (i / (len(self.temp_history) - 1)) * self.width
                    y = self.y + ((temp - temp_min) / temp_range) * self.height
                    points.extend([x, y])
                Line(points=points, width=2)
            
            # Labels
            Color(0.7, 0.7, 0.7, 1)
            # We'll add temperature labels in the main widget


class HeaterControl(BoxLayout):
    def __init__(self, heater_name, kesser_heater: KesserHeater, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20
        
        self.heater_name = heater_name
        status = kesser_heater.get_status()
        self.current_temp = status.current_temp
        self.set_temp = status.set_temp
        self.power = status.power
        
        # Header with title and icon
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        # Heater icon
        icon = HeaterIcon()
        header_layout.add_widget(icon)
        
        # Title
        title = Label(
            text=f'{heater_name}\nHeater',
            font_size='18sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header_layout.add_widget(title)
        
        self.add_widget(header_layout)
        
        # Current temperature display
        self.current_temp_label = Label(
            text=f'Current: {self.current_temp:.1f}°C',
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.current_temp_label)
        
        # Set temperature display
        self.set_temp_label = Label(
            text=f'Set: {self.set_temp:.1f}°C',
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.set_temp_label)
        
        # Control buttons
        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        
        decrease_btn = Button(
            text='−',
            font_size='24sp',
            on_press=self.decrease_temp
        )
        button_layout.add_widget(decrease_btn)
        
        increase_btn = Button(
            text='+',
            font_size='24sp',
            on_press=self.increase_temp
        )
        button_layout.add_widget(increase_btn)
        
        self.add_widget(button_layout)
        
        # Temperature graph
        graph_label = Label(
            text='Temperature History',
            font_size='14sp',
            size_hint_y=None,
            height=25
        )
        self.add_widget(graph_label)
        
        self.graph = TemperatureGraph()
        self.add_widget(self.graph)
        
        # Legend
        legend_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=20, spacing=20)
        
        current_legend = Label(
            text='● Current',
            font_size='12sp',
            color=(1, 0.4, 0.2, 1),
            size_hint_x=None,
            width=60
        )
        legend_layout.add_widget(current_legend)
        
        set_legend = Label(
            text='● Set',
            font_size='12sp',
            color=(0.8, 0.8, 0.2, 1),
            size_hint_x=None,
            width=40
        )
        legend_layout.add_widget(set_legend)
        
        # Add spacer
        legend_layout.add_widget(Label())
        
        self.add_widget(legend_layout)
        
        # Add initial data point
        self.graph.add_temperature(self.current_temp, self.set_temp)
    
    def increase_temp(self, instance):
        if self.set_temp < 30.0:  # Maximum temperature limit
            self.set_temp += 0.5
            self.update_display()
    
    def decrease_temp(self, instance):
        if self.set_temp > 10.0:  # Minimum temperature limit
            self.set_temp -= 0.5
            self.update_display()
    
    def update_current_temp(self, current_temp):
        # Sets the new current temperature, from the heater reading 
        if abs(temp_diff) > 0.1:
            # Move current temp towards set temp with some randomness
            change = temp_diff * 0.1 + random.uniform(-0.2, 0.2)
            self.current_temp += change
            self.current_temp = max(5.0, min(35.0, self.current_temp))  # Bounds
            self.update_display()
            
        # Add to graph every update
        self.graph.add_temperature(self.current_temp, self.set_temp)
    
    def update_display(self):
        self.current_temp_label.text = f'Current: {self.current_temp:.1f}°C'
        self.set_temp_label.text = f'Set: {self.set_temp:.1f}°C'


class LobergTuya(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='horizontal', spacing=20, padding=20)
        
        # Living room heater control
        living_room_control = HeaterControl('Living Room')
        main_layout.add_widget(living_room_control)
        
        # Separator line
        separator = Label(text='|', size_hint_x=None, width=2)
        main_layout.add_widget(separator)
        
        # Bathroom heater control
        bathroom_control = HeaterControl('Bathroom')
        main_layout.add_widget(bathroom_control)
        
        return main_layout


if __name__ == '__main__':
    LobergTuya().run()