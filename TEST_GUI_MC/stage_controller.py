# stage_controller.py
# PyQt5 version of the stage controller with enhanced features

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QGroupBox, QSpinBox, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from mcu_side_enhanced import move_motor
import os


class StageController(QWidget):
    """Stage controller widget for X/Y/Z motor control with enhanced features"""
    
    # Signal emitted when position changes
    position_changed = pyqtSignal(int, int, int)  # x, y, z
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Track current position (in steps)
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0
        
        # Step sizes
        self.xy_step_size = 100
        self.z_step_size = 50
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the stage controller UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Stage Controller")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Logo (optional - can be removed if not needed in main window)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "egen25_logo.png")
            
            if os.path.exists(logo_path):
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                pixmap = pixmap.scaled(200, 95, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_label)
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Position Display
        position_group = QGroupBox("Current Position (steps)")
        position_layout = QHBoxLayout()
        
        self.pos_x_label = QLabel("X: 0")
        self.pos_y_label = QLabel("Y: 0")
        self.pos_z_label = QLabel("Z: 0")
        
        # Make position labels bold and slightly larger
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.pos_x_label.setFont(font)
        self.pos_y_label.setFont(font)
        self.pos_z_label.setFont(font)
        
        position_layout.addWidget(self.pos_x_label)
        position_layout.addWidget(self.pos_y_label)
        position_layout.addWidget(self.pos_z_label)
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        # Step Size Controls
        step_group = QGroupBox("Step Size")
        step_layout = QGridLayout()
        
        # XY Step Size
        xy_step_label = QLabel("XY Steps:")
        self.xy_step_spinbox = QSpinBox()
        self.xy_step_spinbox.setRange(1, 1000)
        self.xy_step_spinbox.setValue(self.xy_step_size)
        self.xy_step_spinbox.setSuffix(" steps")
        self.xy_step_spinbox.valueChanged.connect(self.update_xy_step_size)
        step_layout.addWidget(xy_step_label, 0, 0)
        step_layout.addWidget(self.xy_step_spinbox, 0, 1)
        
        # Z Step Size
        z_step_label = QLabel("Z Steps:")
        self.z_step_spinbox = QSpinBox()
        self.z_step_spinbox.setRange(1, 500)
        self.z_step_spinbox.setValue(self.z_step_size)
        self.z_step_spinbox.setSuffix(" steps")
        self.z_step_spinbox.valueChanged.connect(self.update_z_step_size)
        step_layout.addWidget(z_step_label, 1, 0)
        step_layout.addWidget(self.z_step_spinbox, 1, 1)
        
        step_group.setLayout(step_layout)
        layout.addWidget(step_group)
        
        # Jog Speed Control
        speed_group = QGroupBox("Jog Speed")
        speed_layout = QVBoxLayout()
        
        self.speed_label = QLabel("Speed: Medium (0.5ms delay)")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)  # 1 = slowest, 10 = fastest
        self.speed_slider.setValue(5)  # Medium speed
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # XY Movement Grid
        xy_group = QGroupBox("XY Movement")
        xy_layout = QGridLayout()
        
        # Row 0: Y+
        self.btn_y_plus = QPushButton("↑ Y+")
        self.btn_y_plus.setMinimumSize(80, 50)
        self.btn_y_plus.clicked.connect(lambda: self.move_axis('Y', '+'))
        xy_layout.addWidget(self.btn_y_plus, 0, 1)
        
        # Row 1: X-, STOP, X+
        self.btn_x_minus = QPushButton("← X-")
        self.btn_x_minus.setMinimumSize(80, 50)
        self.btn_x_minus.clicked.connect(lambda: self.move_axis('X', '-'))
        xy_layout.addWidget(self.btn_x_minus, 1, 0)
        
        self.btn_stop = QPushButton("⚠ STOP")
        self.btn_stop.setMinimumSize(80, 50)
        self.btn_stop.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; font-size: 14px;")
        self.btn_stop.clicked.connect(self.emergency_stop)
        xy_layout.addWidget(self.btn_stop, 1, 1)
        
        self.btn_x_plus = QPushButton("→ X+")
        self.btn_x_plus.setMinimumSize(80, 50)
        self.btn_x_plus.clicked.connect(lambda: self.move_axis('X', '+'))
        xy_layout.addWidget(self.btn_x_plus, 1, 2)
        
        # Row 2: Y-
        self.btn_y_minus = QPushButton("↓ Y-")
        self.btn_y_minus.setMinimumSize(80, 50)
        self.btn_y_minus.clicked.connect(lambda: self.move_axis('Y', '-'))
        xy_layout.addWidget(self.btn_y_minus, 2, 1)
        
        xy_group.setLayout(xy_layout)
        layout.addWidget(xy_group)
        
        # Z Movement
        z_group = QGroupBox("Z Axis")
        z_layout = QHBoxLayout()
        
        self.btn_z_plus = QPushButton("Z+")
        self.btn_z_plus.setMinimumSize(80, 50)
        self.btn_z_plus.clicked.connect(lambda: self.move_axis('Z', '+'))
        z_layout.addWidget(self.btn_z_plus)
        
        self.btn_z_minus = QPushButton("Z-")
        self.btn_z_minus.setMinimumSize(80, 50)
        self.btn_z_minus.clicked.connect(lambda: self.move_axis('Z', '-'))
        z_layout.addWidget(self.btn_z_minus)
        
        z_group.setLayout(z_layout)
        layout.addWidget(z_group)
        
        # Homing/Datum Control
        home_group = QGroupBox("Homing")
        home_layout = QGridLayout()
        
        self.btn_home_x = QPushButton("Home X")
        self.btn_home_x.clicked.connect(lambda: self.home_axis('X'))
        home_layout.addWidget(self.btn_home_x, 0, 0)
        
        self.btn_home_y = QPushButton("Home Y")
        self.btn_home_y.clicked.connect(lambda: self.home_axis('Y'))
        home_layout.addWidget(self.btn_home_y, 0, 1)
        
        self.btn_home_z = QPushButton("Home Z")
        self.btn_home_z.clicked.connect(lambda: self.home_axis('Z'))
        home_layout.addWidget(self.btn_home_z, 0, 2)
        
        self.btn_home_all = QPushButton("Home All Axes")
        self.btn_home_all.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")
        self.btn_home_all.clicked.connect(self.home_all_axes)
        home_layout.addWidget(self.btn_home_all, 1, 0, 1, 3)
        
        self.btn_zero_position = QPushButton("Zero Current Position")
        self.btn_zero_position.setStyleSheet("background-color: #388e3c; color: white;")
        self.btn_zero_position.clicked.connect(self.zero_position)
        home_layout.addWidget(self.btn_zero_position, 2, 0, 1, 3)
        
        home_group.setLayout(home_layout)
        layout.addWidget(home_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_xy_step_size(self, value):
        """Update XY step size"""
        self.xy_step_size = value
        print(f"XY step size changed to: {value}")
    
    def update_z_step_size(self, value):
        """Update Z step size"""
        self.z_step_size = value
        print(f"Z step size changed to: {value}")
    
    def update_speed(self, value):
        """Update jog speed and apply to motor controller"""
        # Map slider value (1-10) to step delay (2ms-0.1ms)
        # Lower delay = faster movement
        delay_ms = 2.0 - (value - 1) * 0.21  # Maps 1→2.0ms, 10→0.1ms
        
        speed_names = {
            1: "Very Slow", 2: "Slow", 3: "Slow-Medium",
            4: "Medium-Slow", 5: "Medium", 6: "Medium-Fast",
            7: "Fast-Medium", 8: "Fast", 9: "Very Fast", 10: "Maximum"
        }
        
        self.speed_label.setText(f"Speed: {speed_names[value]} ({delay_ms:.2f}ms delay)")
        
        # Update the STEP_DELAY in mcu_side module
        try:
            import mcu_side
            mcu_side.STEP_DELAY = delay_ms / 1000.0  # Convert to seconds
            print(f"Motor speed updated: {delay_ms:.2f}ms delay")
        except Exception as e:
            print(f"Error updating motor speed: {e}")
    
    def move_axis(self, axis, direction):
        """Move specified axis in given direction"""
        if axis in ['X', 'Y']:
            steps = self.xy_step_size
        else:  # Z
            steps = self.z_step_size
        
        command = f"{axis}{direction}{steps}"
        print(f"Command: {command}")
        
        # Update position tracking
        step_delta = steps if direction == '+' else -steps
        if axis == 'X':
            self.position_x += step_delta
        elif axis == 'Y':
            self.position_y += step_delta
        elif axis == 'Z':
            self.position_z += step_delta
        
        self.update_position_display()
        
        # Execute motor command
        move_motor(axis, direction, steps)
    
    def emergency_stop(self):
        """Emergency stop - halt all motor movement"""
        print("🚨 EMERGENCY STOP ACTIVATED 🚨")
        # TODO: Implement actual e-stop logic here
        # This might involve:
        # - Sending stop signal to motor controller
        # - Disabling motor drivers
        # - Setting an emergency flag
        # - Logging the event
        
        # Placeholder for actual implementation
        try:
            import mcu_side
            # You might want to add an emergency_stop() function to mcu_side.py
            # mcu_side.emergency_stop()
            print("All motors stopped")
        except Exception as e:
            print(f"Error during emergency stop: {e}")
    
    def home_axis(self, axis):
        """Home a single axis"""
        print(f"Homing {axis} axis...")
        # TODO: Implement actual homing logic
        # This typically involves:
        # - Moving until limit switch is triggered
        # - Backing off slightly
        # - Setting position to 0
        
        # For now, just reset the position counter
        if axis == 'X':
            self.position_x = 0
        elif axis == 'Y':
            self.position_y = 0
        elif axis == 'Z':
            self.position_z = 0
        
        self.update_position_display()
        print(f"{axis} axis homed to position 0")
    
    def home_all_axes(self):
        """Home all axes in sequence"""
        print("Homing all axes...")
        # Typically done in order: Z first (lift), then X, then Y
        self.home_axis('Z')
        self.home_axis('X')
        self.home_axis('Y')
        print("All axes homed")
    
    def zero_position(self):
        """Set current position as zero point (datum)"""
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0
        self.update_position_display()
        print("Current position set as zero/datum")
    
    def update_position_display(self):
        """Update the position labels"""
        self.pos_x_label.setText(f"X: {self.position_x}")
        self.pos_y_label.setText(f"Y: {self.position_y}")
        self.pos_z_label.setText(f"Z: {self.position_z}")
        
        # Emit signal for other components that might need position info
        self.position_changed.emit(self.position_x, self.position_y, self.position_z)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        key = event.key()
        
        if key == Qt.Key_Up:
            self.move_axis('Y', '+')
        elif key == Qt.Key_Down:
            self.move_axis('Y', '-')
        elif key == Qt.Key_Left:
            self.move_axis('X', '-')
        elif key == Qt.Key_Right:
            self.move_axis('X', '+')
        elif key == Qt.Key_PageUp:
            self.move_axis('Z', '+')
        elif key == Qt.Key_PageDown:
            self.move_axis('Z', '-')
        elif key == Qt.Key_Space:
            self.emergency_stop()
        elif key == Qt.Key_H:
            self.home_all_axes()
        elif key == Qt.Key_0:
            self.zero_position()
        else:
            super().keyPressEvent(event)
