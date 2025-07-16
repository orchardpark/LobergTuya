import kivy
kivy.require('2.3.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.core.text import Label as CoreLabel
import random
from collections import deque
from kivy.config import Config


class TemperatureGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 300
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
            
            # Grid lines and temperature labels
            Color(0.3, 0.3, 0.3, 1)
            temp_min, temp_max = 10, 35
            temp_range = temp_max - temp_min
            
            # Draw horizontal grid lines at temperature intervals
            for i in range(5):  # 5 horizontal lines (including top and bottom)
                y = self.y + (self.height / 4) * i
                if i > 0 and i < 4:  # Don't draw lines at very top and bottom
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
            
            # Draw temperature scale labels
            Color(0.7, 0.7, 0.7, 1)
            for i in range(5):  # 5 labels from 10°C to 35°C
                temp_value = temp_min + (temp_range / 4) * i
                y = self.y + (self.height / 4) * i
                
                # Create text label
                label = CoreLabel(text=f'{temp_value:.0f}°C', font_size=10)
                label.refresh()
                texture = label.texture
                
                # Position label to the left of the graph
                label_x = self.x - 35
                label_y = y - texture.height / 2
                
                # Draw the label
                Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
            
            # Draw current temperature line
            if len(self.temp_history) >= 2:
                Color(1, 0.4, 0.2, 1)  # Orange for current temperature
                points = []
                for i, temp in enumerate(self.temp_history):
                    x = self.x + (i / (len(self.temp_history) - 1)) * self.width
                    y = self.y + ((temp - temp_min) / temp_range) * self.height
                    points.extend([x, y])
                Line(points=points, width=2)


class HeaterControl(BoxLayout):
    def __init__(self, heater_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20
        
        self.heater_name = heater_name
        self.current_temp = 20.0  # Starting current temperature
        self.set_temp = 22.0      # Starting set temperature
        self.is_on = True         # Heater power state
        self.is_online = True     # Device connectivity state
        self.display_on = True    # Display state
        
        # Title
        title = Label(
            text=f'{heater_name} Heater',
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True
        )
        self.add_widget(title)
        
        # Status indicators
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=20)
        
        # Online/Offline status
        self.online_status = Label(
            text='● Online',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),  # Green
            size_hint_x=None,
            width=80
        )
        status_layout.add_widget(self.online_status)
        
        # On/Off status
        self.power_status = Label(
            text='● On',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),  # Green
            size_hint_x=None,
            width=60
        )
        status_layout.add_widget(self.power_status)
        
        # Display status
        self.display_status = Label(
            text='● Display On',
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1),  # Green
            size_hint_x=None,
            width=90
        )
        status_layout.add_widget(self.display_status)
        
        # Add spacer
        status_layout.add_widget(Label())
        
        self.add_widget(status_layout)
        
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
        button_layout = GridLayout(cols=4, spacing=10, size_hint_y=None, height=50)
        
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
        
        # Power toggle button
        self.power_btn = Button(
            text='Turn Off',
            font_size='14sp',
            background_color=(0.8, 0.2, 0.2, 1),  # Red
            on_press=self.toggle_power
        )
        button_layout.add_widget(self.power_btn)
        
        # Display toggle button
        self.display_btn = Button(
            text='Display Off',
            font_size='14sp',
            background_color=(0.8, 0.2, 0.2, 1),  # Red
            on_press=self.toggle_display
        )
        button_layout.add_widget(self.display_btn)
        
        self.add_widget(button_layout)
        
        # Online toggle button (simulate connectivity)
        self.online_btn = Button(
            text='Simulate Offline',
            font_size='12sp',
            size_hint_y=None,
            height=35,
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.toggle_online
        )
        self.add_widget(self.online_btn)
        
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
        
        # Schedule current temperature updates to simulate real heater behavior
        Clock.schedule_interval(self.update_current_temp, 2.0)
        
        # Add initial data point
        self.graph.add_temperature(self.current_temp, self.set_temp)
        
        # Update display
        self.update_display()
    
    def increase_temp(self, instance):
        if self.is_online and self.set_temp < 30.0:  # Maximum temperature limit
            self.set_temp += 0.5
            self.update_display()
    
    def decrease_temp(self, instance):
        if self.is_online and self.set_temp > 10.0:  # Minimum temperature limit
            self.set_temp -= 0.5
            self.update_display()
    
    def toggle_power(self, instance):
        if self.is_online:
            self.is_on = not self.is_on
            self.update_display()
    
    def toggle_display(self, instance):
        if self.is_online:
            self.display_on = not self.display_on
            self.update_display()
    
    def toggle_online(self, instance):
        self.is_online = not self.is_online
        self.update_display()
    
    def update_current_temp(self, dt):
        if not self.is_online:
            # When offline, don't update temperature
            return
        
        if self.is_on:
            # Heater is on - temperature moves toward set temperature
            temp_diff = self.set_temp - self.current_temp
            if abs(temp_diff) > 0.1:
                # Move current temp towards set temp with some randomness
                change = temp_diff * 0.1 + random.uniform(-0.2, 0.2)
                self.current_temp += change
                self.current_temp = max(5.0, min(35.0, self.current_temp))  # Bounds
        else:
            # Heater is off - temperature gradually decreases toward ambient (18°C)
            ambient_temp = 18.0
            temp_diff = ambient_temp - self.current_temp
            if abs(temp_diff) > 0.1:
                change = temp_diff * 0.05 + random.uniform(-0.1, 0.1)
                self.current_temp += change
                self.current_temp = max(5.0, min(35.0, self.current_temp))  # Bounds
        
        self.update_display()
        
        # Add to graph every update
        self.graph.add_temperature(self.current_temp, self.set_temp)
    
    def update_display(self):
        # Update temperature displays based on display state
        if self.display_on:
            self.current_temp_label.text = f'Current: {self.current_temp:.1f}°C'
            self.set_temp_label.text = f'Set: {self.set_temp:.1f}°C'
            self.current_temp_label.color = (1, 1, 1, 1)  # White
            self.set_temp_label.color = (1, 1, 1, 1)  # White
        else:
            self.current_temp_label.text = 'Current: ---'
            self.set_temp_label.text = 'Set: ---'
            self.current_temp_label.color = (0.3, 0.3, 0.3, 1)  # Dark gray
            self.set_temp_label.color = (0.3, 0.3, 0.3, 1)  # Dark gray
        
        # Update online status
        if self.is_online:
            self.online_status.text = '● Online'
            self.online_status.color = (0.2, 0.8, 0.2, 1)  # Green
            self.online_btn.text = 'Simulate Offline'
        else:
            self.online_status.text = '● Offline'
            self.online_status.color = (0.8, 0.2, 0.2, 1)  # Red
            self.online_btn.text = 'Simulate Online'
        
        # Update power status and button
        if self.is_on:
            self.power_status.text = '● On'
            self.power_status.color = (0.2, 0.8, 0.2, 1)  # Green
            self.power_btn.text = 'Turn Off'
            self.power_btn.background_color = (0.8, 0.2, 0.2, 1)  # Red
        else:
            self.power_status.text = '● Off'
            self.power_status.color = (0.8, 0.2, 0.2, 1)  # Red
            self.power_btn.text = 'Turn On'
            self.power_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
        
        # Update display status and button
        if self.display_on:
            self.display_status.text = '● Display On'
            self.display_status.color = (0.2, 0.8, 0.2, 1)  # Green
            self.display_btn.text = 'Display Off'
            self.display_btn.background_color = (0.8, 0.2, 0.2, 1)  # Red
        else:
            self.display_status.text = '● Display Off'
            self.display_status.color = (0.8, 0.2, 0.2, 1)  # Red
            self.display_btn.text = 'Display On'
            self.display_btn.background_color = (0.2, 0.8, 0.2, 1)  # Green
        
        # Disable controls when offline
        if not self.is_online:
            self.power_btn.disabled = True
            self.power_btn.background_color = (0.5, 0.5, 0.5, 1)  # Gray
            self.display_btn.disabled = True
            self.display_btn.background_color = (0.5, 0.5, 0.5, 1)  # Gray
        else:
            self.power_btn.disabled = False
            self.display_btn.disabled = False


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