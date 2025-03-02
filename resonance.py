import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
import math

# Default values
DEFAULT_VALUES = {
    'circuit': 'Series',
    'inductance': 10,  # mH
    'inductance_unit': 'mH',
    'capacitance': 100,  # uF
    'capacitance_unit': 'uF',
    'frequency_min': 1,  # kHz
    'frequency_max': 10,  # kHz
    'frequency_unit': 'kHz',
    'resistance': 10,
    'input_voltage': 10,  # Volts
    'input_frequency': 1,  # kHz
    'x_scale': 'log',
    'y_scale': 'log',
    'inductive_var': True,
    'capacitive_var': True,
    'resonance_var': True,
    'current_var': True,
}

# File path to save the values
SAVE_FILE = "saved_values.json"

def load_values():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as file:
            return json.load(file)
    return DEFAULT_VALUES

def save_values():
    values = {
        'circuit': circuit_type.get(),
        'inductance': float(inductance_entry.get()),
        'inductance_unit': inductance_unit.get(),
        'capacitance': float(capacitance_entry.get()),
        'capacitance_unit': capacitance_unit.get(),
        'frequency_min': float(frequency_min_entry.get()),
        'frequency_max': float(frequency_max_entry.get()),
        'frequency_unit': frequency_unit.get(),
        'resistance': float(resistance_entry.get()),
        'input_voltage': float(input_voltage_entry.get()),
        'input_frequency': float(input_frequency_entry.get()),
        'x_scale': x_scale_var.get(),
        'y_scale': y_scale_var.get(),
        'inductive_var': inductive_var.get(),
        'capacitive_var': capacitive_var.get(),
        'resonance_var': resonance_var.get(),
        'current_var': current_var.get(),
    }
    with open(SAVE_FILE, 'w') as file:
        json.dump(values, file)



def calculate_values():

    L_value = float(inductance_entry.get())
    L_unit = inductance_unit.get()
    C_value = float(capacitance_entry.get())
    C_unit = capacitance_unit.get()
    f_min = float(frequency_min_entry.get())
    f_max = float(frequency_max_entry.get())
    f_unit = frequency_unit.get()
    R_value = float(resistance_entry.get())
    
    unit_multipliers = {'Hz': 1, 'kHz': 1e3, 'MHz': 1e6, 'uH': 1e-6, 'mH': 1e-3, 'H': 1, 'pF': 1e-12, 'nF': 1e-9, 'uF': 1e-6, 'mF': 1e-3, 'F': 1}
    f_min *= unit_multipliers[f_unit]
    f_max *= unit_multipliers[f_unit]
    L = L_value * unit_multipliers[L_unit]
    C = C_value * unit_multipliers[C_unit]
    
    R_value = float(resistance_entry.get())
    V_in = float(input_voltage_entry.get())
    f_in = float(input_frequency_entry.get()) * {'Hz': 1, 'kHz': 1e3, 'MHz': 1e6}[frequency_unit.get()]

    X_L = 2 * np.pi * f_in * L
    X_C = 1 / (2 * np.pi * f_in * C)

    # Create a Treeview inside the frame
    table = ttk.Treeview(frame, columns=("Quantity", "Value"), show="headings", height=4)
    table_1 = ttk.Treeview(frame, columns=("Quantity", "Value"), show="headings", height=4)
    
    table.heading("Quantity", text="Quantity")
    table.heading("Value", text="Value")

    table_1.heading("Quantity", text="Quantity")
    table_1.heading("Value", text="Value")
    
    # Set column width
    table.column("Quantity", width=100, anchor="center")
    table.column("Value", width=100, anchor="center")
    table_1.column("Quantity", width=100, anchor="center")
    table_1.column("Value", width=100, anchor="center")

    if circuit_type.get() == "Series":
        Z = np.sqrt(R_value**2 + (X_L - X_C)**2)
        I = V_in / Z
        V_R = I * R_value
        V_L = I * X_L
        V_C = I * X_C
        P_F = R_value / Z
        L_L = math.acos(P_F)*(180.0 / math.pi)

        # Insert data into the table
        table.insert("", "end", values=("Resistor_v", f"{V_R:.2f} V"))
        table.insert("", "end", values=("Inductor_v", f"{V_L:.2f} V"))
        table.insert("", "end", values=("Capacitor_v", f"{V_C:.2f} V"))
        table.insert("", "end", values=("Current", f"{I:.2f} A"))
        table_1.insert("", "end", values=("Impedance", f"{Z:.2f} ohm"))
        table_1.insert("", "end", values=("Power Factor", f"{P_F:.2f}"))
        if X_L > X_C:
            table_1.insert("", "end", values=("I Lag V", f"{L_L:.2f} deg"))
        elif X_C > X_L:
            table_1.insert("", "end", values=("V Lag I", f"{L_L:.2f} deg"))
        else:
            table_1.insert("", "end", values=("Resonance", "0.00 deg"))  

    else:
        Y = np.sqrt((1/R_value)**2 + (1/X_L - 1/X_C)**2)
        Z = 1 / Y
        I_R = V_in / R_value
        I_L = V_in / X_L
        I_C = V_in / X_C
        I_S = np.sqrt(I_R**2 + (I_L - I_C)**2)
        P_F = Z / R_value
        L_L = math.acos(P_F)*(180.0 / math.pi)
        
        # Insert data into the table
        table.insert("", "end", values=("Resistor_i", f"{I_R:.2f} A"))
        table.insert("", "end", values=("Inductor_i", f"{I_L:.2f} A"))
        table.insert("", "end", values=("Capacitor_i", f"{I_C:.2f} A"))
        table.insert("", "end", values=("Current_total", f"{I_S:.2f} A"))
        table_1.insert("", "end", values=("Impedance", f"{Z:.2f} ohm"))
        table_1.insert("", "end", values=("Power Factor", f"{P_F:.2f}"))
        
        if X_C < X_L:  # Equivalent to B_C > B_L
            table_1.insert("", "end", values=("V Lag I", f"{L_L:.2f} deg"))
        elif X_L < X_C:  # Equivalent to B_L > B_C
            table_1.insert("", "end", values=("I Lag V", f"{L_L:.2f} deg"))
        else:
            table_1.insert("", "end", values=("Resonance", "0.00 deg"))  



    # Place the table in the grid (spanning multiple rows to fit)
    table.grid(row=9, column=5, rowspan=7, columnspan=2,sticky="w", padx=5, pady=5)
    table_1.grid(row=9, column=7, rowspan=7, columnspan=2,sticky="w", padx=5, pady=5)   

def calculate_q_bw(R_value, L, resonance_frequency):
    #Calculate Q Factor at Resonant frequency
    Q = (2 * np.pi * resonance_frequency * L) / R_value
    #Calculate Bandwidth
    BW = resonance_frequency / Q
    #The upper and lower -3dB frequency points, ƒH and ƒL
    FL = resonance_frequency - 0.5*BW
    FH = resonance_frequency + 0.5*BW
    return Q, FL, FH

def plot_graph():
    global canvas  # Use a global variable to track the canvas

    # Clear previous plot if it exists
    if 'canvas' in globals() and canvas is not None:
        canvas.get_tk_widget().destroy()
            
    # Get current window size
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    
    # Example: set the figure width to 80% of the window width
    fig_width = window_width * 0.95
    fig_height = window_height * 0.6  # Adjust height proportionally or set a fixed ratio
    
    # Adjust figure size based on window size
    fig, ax1 = plt.subplots(figsize=(fig_width / 100, fig_height / 100), facecolor='lightgrey')  # Convert pixels to inches
    
    L_value = float(inductance_entry.get())
    L_unit = inductance_unit.get()
    C_value = float(capacitance_entry.get())
    C_unit = capacitance_unit.get()
    f_min = float(frequency_min_entry.get())
    f_max = float(frequency_max_entry.get())
    f_unit = frequency_unit.get()
    R_value = float(resistance_entry.get())
    
    unit_multipliers = {'Hz': 1, 'kHz': 1e3, 'MHz': 1e6, 'uH': 1e-6, 'mH': 1e-3, 'H': 1, 'pF': 1e-12, 'nF': 1e-9, 'uF': 1e-6, 'mF': 1e-3, 'F': 1}
    f_min *= unit_multipliers[f_unit]
    f_max *= unit_multipliers[f_unit]
    L = L_value * unit_multipliers[L_unit]
    C = C_value * unit_multipliers[C_unit]
    frequencies = np.linspace(f_min, f_max, 1000)
    f_in = float(input_frequency_entry.get()) * {'Hz': 1, 'kHz': 1e3, 'MHz': 1e6}[frequency_unit.get()]

    V_in = float(input_voltage_entry.get())
    inductive_reactance = 2 * np.pi * frequencies * L
    capacitive_reactance = 1 / (2 * np.pi * frequencies * C)

    #Z = np.sqrt(R_value**2 + (inductive_reactance - capacitive_reactance)**2)
    if circuit_type.get() == "Series":
        Z = np.sqrt(R_value**2 + (inductive_reactance - capacitive_reactance)**2)
    else:  # Parallel Resonant Circuit
        Y = np.sqrt((1/R_value)**2 + (1/inductive_reactance - 1/capacitive_reactance)**2)
        Z = 1 / Y
        
        
    current = V_in / Z
    
    if inductive_var.get():      
        ax1.plot(frequencies, inductive_reactance, label=f'Inductive Reactance\n(L={L_value} {L_unit})', color='b')
    
    if capacitive_var.get():
        ax1.plot(frequencies, capacitive_reactance, label=f'Capacitive Reactance\n(C={C_value} {C_unit})', color='y')
    
    if resonance_var.get():
        resonance_frequency = 1 / (2 * np.pi * np.sqrt(L * C))

        ax1.axvline(resonance_frequency, color='g', linestyle='--', label = f'Resonance Frequency\n{resonance_frequency / 1000.0:.2f} kHz')
        ax1.plot(frequencies, Z, label=f'Impedance Z', color='purple')
            
        #Calculate Q Factor at Resonant frequency
        if circuit_type.get() == "Series":
            Q, FL, FH = calculate_q_bw(R_value, L, resonance_frequency)
            
            ax1.axvline(x=FL, color='honeydew', linestyle='--', label=f'FL: {FL/1000.0:.2f} kHz')
            ax1.axvline(x=FH, color='honeydew', linestyle='--', label=f'FH: {FH/1000.0:.2f} kHz')  
            ax1.annotate(f'Q: {Q:.2f}',
                         xy=(resonance_frequency, max(Z)/2),
                         xytext=(resonance_frequency * 1.1, max(Z)/2),
                         arrowprops=dict(facecolor='black', shrink=0.05))


        # Calculate reactance at input_frequency
        X_L = 2 * np.pi * f_in * L
        X_C = 1 / (2 * np.pi * f_in * C)
        Z_f_in = np.sqrt(R_value**2 + (X_L - X_C)**2)
        
        # Plot the single point on the total impedance curve
        ax1.scatter(f_in, Z_f_in, color='black', marker='o', s=50)

        ax1.annotate(text=f'{f_in / 1000:.2f} kHz', # Annotation text
                     xy=(f_in, Z_f_in), # Arrow tip (data point)
                     xytext=(f_in * 0.95, Z_f_in * 0.7), # Offset text position
                     arrowprops=dict(facecolor='red', arrowstyle='->'))
        
    if current_var.get():
        #R_value = float(resistance_entry.get())
        #current = 1 / np.sqrt(R_value**2 + (2 * np.pi * frequencies * L - 1 / (2 * np.pi * frequencies * C))**2)
        
        # Create a second y-axis on the right side for current
        ax2 = ax1.twinx()  # Create another y-axis sharing the same x-axis
        ax2.plot(frequencies, current, label='Current (I)', color='crimson', linestyle='--')
        ax2.set_ylabel('Current (A)', color='crimson')  # Label for right axis
        ax2.tick_params(axis='y', labelcolor='crimson')  # Set tick color for right axis
        ax2.legend(loc='upper left', bbox_to_anchor=(0.83, 1.15), ncol=3)

    
    ax1.set_facecolor("lightgrey")
    plt.figure(facecolor='yellow')
    
    ax1.set_xscale(x_scale_var.get())
    ax1.set_yscale(y_scale_var.get())
    ax1.set_xlabel(f'Frequency ({f_unit})')
    ax1.set_ylabel('Reactance (Ohms)')  # Label for left axis
    ax1.tick_params(axis='y')  # Set tick color for left axis
    #ax1.set_title('Reactance and Current vs Frequency')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    
    
    # Create a legend for both axes and place it on top of the chart
    ax1.legend(loc='upper right', bbox_to_anchor=(0.83, 1.15), ncol=3)
    
    # Create a canvas to draw the figure
    canvas = FigureCanvasTkAgg(fig, master=root)  # Placing the chart outside the frame
    canvas.draw()
    
    # Add canvas to the window
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


root = tk.Tk()
root.title("Reactance Plotter")

frame = ttk.Frame(root)
frame.pack(side=tk.TOP, padx=10, pady=10)

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size (half width, full height) and position (left side)
root.geometry(f"{screen_width//2}x{screen_height-80}+0+0")

frame.grid_columnconfigure(0, weight=1, minsize=100)
frame.grid_columnconfigure(1, weight=1, minsize=100)
frame.grid_columnconfigure(2, weight=1, minsize=100)

# Load saved values or defaults
saved_values = load_values()

# Widgets and their values

### Series / Parallel
ttk.Label(frame, text="Circuit type:").grid(row=7, column=3, sticky="w", padx=5, pady=5)
input_frequency_entry = ttk.Entry(frame)
circuit_type = ttk.Combobox(frame, values=["Series", "Parallel"], state="readonly", width=8)
circuit_type.grid(row=7, column=4)
circuit_type.set(saved_values['circuit'])


### Inductance
ttk.Label(frame, text="Inductance:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
inductance_entry = ttk.Entry(frame, width = 10)
inductance_entry.grid(row=0, column=1, padx=5, pady=5)
inductance_entry.insert(0, saved_values['inductance'])  # Set saved value
inductance_unit = ttk.Combobox(frame, values=["uH", "mH", "H"], state="readonly", width=5)
inductance_unit.grid(row=0, column=2, padx=5, pady=5)
inductance_unit.set(saved_values['inductance_unit'])

### Voltage
ttk.Label(frame, text="Input Voltage (V):").grid(row=0, column=3, sticky="w", padx=5, pady=5)
input_voltage_entry = ttk.Entry(frame, width = 10)
input_voltage_entry.grid(row=0, column=4)
input_voltage_entry.insert(0, saved_values['input_voltage'])

### Capacitance
capacitive_var = tk.BooleanVar(value=saved_values['capacitive_var'])
inductive_var = tk.BooleanVar(value=saved_values['inductive_var'])
resonance_var = tk.BooleanVar(value=saved_values['resonance_var'])
current_var = tk.BooleanVar(value=saved_values['current_var'])

ttk.Label(frame, text="Capacitance:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
capacitance_entry = ttk.Entry(frame, width = 10)
capacitance_entry.grid(row=5, column=1, padx=5, pady=5)
capacitance_entry.insert(0, saved_values['capacitance'])  # Set saved value
capacitance_unit = ttk.Combobox(frame, values=["pF", "nF", "uF", "mF", "F"], state="readonly", width=5)
capacitance_unit.grid(row=5, column=2, padx=5, pady=5)
capacitance_unit.set(saved_values['capacitance_unit'])

### Resistance
ttk.Label(frame, text="Resistance (Ohms):").grid(row=5, column=3, sticky="w", padx=5, pady=5)
resistance_entry = ttk.Entry(frame, width = 10)
resistance_entry.grid(row=5, column=4, padx=5, pady=5)
resistance_entry.insert(0, saved_values['resistance'])

### Frequency
ttk.Label(frame, text="Frequency Min:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
frequency_min_entry = ttk.Entry(frame, width = 10)
frequency_min_entry.grid(row=6, column=1, padx=5, pady=5)
frequency_min_entry.insert(0, saved_values['frequency_min'])

ttk.Label(frame, text="Frequency Max:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
frequency_max_entry = ttk.Entry(frame, width = 10)
frequency_max_entry.grid(row=7, column=1, padx=5, pady=5)
frequency_max_entry.insert(0, saved_values['frequency_max'])

frequency_unit = ttk.Combobox(frame, values=["Hz", "kHz", "MHz"], state="readonly", width=5)
frequency_unit.grid(row=6, column=2, padx=5, pady=5)
frequency_unit.set(saved_values['frequency_unit'])

ttk.Label(frame, text="Input Frequency:").grid(row=6, column=3, sticky="w", padx=5, pady=5)
input_frequency_entry = ttk.Entry(frame, width = 10)
input_frequency_entry.grid(row=6, column=4)
input_frequency_entry.insert(0, saved_values['input_frequency'])

### Scale
ttk.Label(frame, text="X-Axis Scale:").grid(row=0, column=7, sticky="w", padx=5, pady=5)
x_scale_var = ttk.Combobox(frame, values=["linear", "log"], state="readonly", width=5)
x_scale_var.grid(row=0, column=8, padx=5, pady=5)
x_scale_var.set(saved_values['x_scale'])

ttk.Label(frame, text="Y-Axis Scale:").grid(row=5, column=7, sticky="w", padx=5, pady=5)
y_scale_var = ttk.Combobox(frame, values=["linear", "log"], state="readonly", width=5)
y_scale_var.grid(row=5, column=8, padx=5, pady=5)
y_scale_var.set(saved_values['y_scale'])

# Buttons
plot_button = ttk.Button(frame, text="Plot Graph", command=plot_graph)
plot_button.grid(row=8, column=2)

### Check Boxes
ttk.Checkbutton(frame, text="Plot Inductive Reactance", variable=inductive_var).grid(row=0, column=6, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame, text="Plot Capacitive Reactance", variable=capacitive_var).grid(row=5, column=6, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame, text="Show Resonance Frequency", variable=resonance_var).grid(row=6, column=6, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame, text="Plot Current", variable=current_var).grid(row=7, column=6, sticky="w", padx=5, pady=5)

# Save the values when the plot button is clicked
plot_button['command'] = lambda: [save_values(), plot_graph(), calculate_values()]

root.mainloop()
