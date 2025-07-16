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
from kivy.core.text import Label as CoreLabel
from collections import deque
from control import KesserHeater, parse_devices


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
    def __init__(self, kesser_heater: KesserHeater, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20
        
        self.heater_name = kesser_heater.name
        self.kesser_heater = kesser_heater
        self.update_status(True)
                
        # Title
        title = Label(
            text=f'{self.heater_name} Heater',
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
        
        Clock.schedule_interval(lambda _: self.update_status(), 60*5)
    
    def update_status(self, first_run=False):
        status = self.kesser_heater.get_status()
        self.current_temp = status.current_temp 
        self.set_temp = status.set_temp
        self.is_on = status.power
        self.is_online = status.online
        self.display_on = status.display
        if not first_run:
            self.update_display()
            self.graph.add_temperature(self.current_temp, self.set_temp)
    
    def increase_temp(self, instance):
        if self.is_online:  
            self.kesser_heater.set_temperature(self.set_temp+1)
            self.update_status()
    
    def decrease_temp(self, instance):
        if self.is_online: 
            self.kesser_heater.set_temperature(self.set_temp-1)
            self.update_status()
    
    def toggle_power(self, instance):
        if self.is_online:
            if self.is_on:
                self.kesser_heater.turn_off()
            else:
                self.kesser_heater.turn_on()
            self.update_status()
    
    def toggle_display(self, instance):
        if self.is_online:
            if self.display_on:
                self.kesser_heater.turn_display_off()
            else:
                self.kesser_heater.turn_display_on()
            self.update_status()
    
    def update_display(self):
        self.current_temp_label.text = f'Current: {self.current_temp:.1f}°C'
        self.set_temp_label.text = f'Set: {self.set_temp:.1f}°C'
        self.current_temp_label.color = (1, 1, 1, 1)  # White
        self.set_temp_label.color = (1, 1, 1, 1)  # White

        if self.is_online:
            self.online_status.text = '● Online'
            self.online_status.color = (0.2, 0.8, 0.2, 1)  # Green
        else:
            self.online_status.text = '● Offline'
            self.online_status.color = (0.8, 0.2, 0.2, 1)  # Red
        
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
        
        devices = parse_devices()
        
        living_room_heater = next((d for d in devices if d.name=='Heater 1'), None)
        bath_room_heater = next((d for d in devices if d.name=='Heater 2'), None)
        
        if not (living_room_heater and bath_room_heater):
            return

        # Main layout
        main_layout = BoxLayout(orientation='horizontal', spacing=20, padding=20)
        
        # Living room heater control
        living_room_control = HeaterControl(living_room_heater)
        main_layout.add_widget(living_room_control)
        
        # Separator line
        separator = Label(text='|', size_hint_x=None, width=2)
        main_layout.add_widget(separator)
        
        # Bathroom heater control
        bathroom_control = HeaterControl(living_room_heater)
        main_layout.add_widget(bathroom_control)
        
        return main_layout


if __name__ == '__main__':
    LobergTuya().run()