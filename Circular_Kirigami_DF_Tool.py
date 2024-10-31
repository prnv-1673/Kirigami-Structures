import turtle
import math
import re

# Function to gather inputs and store them in clear variables
def get_user_inputs():
    outer_diameter = float(input("Enter the Outer Diameter (mm): "))
    inner_diameter = float(input("Enter the Inner Diameter (mm): "))
    thickness = float(input("Enter the Thickness (mm): "))
    num_hinges = int(input("Enter the Number of Hinges: "))
    beam_width = float(input("Enter the Beam Width (mm): "))
    void_width = float(input("Enter the Void Width (mm): "))
    hinge_width = float(input("Enter the Hinge Width (mm): "))
    hinge_offset_angle = float(input("Enter the hinge offset angle (in degrees): "))
    needle_diameter = float(input("Enter the Needle Diameter (mm) (extrusion width): "))
    print_speed = float(input("Enter the print speed (mm/s): "))
    

    return {
        'outer_diameter': outer_diameter,
        'inner_diameter': inner_diameter,
        'thickness': thickness,
        'num_hinges': num_hinges,
        'beam_width': beam_width,
        'void_width': void_width,
        'hinge_width': hinge_width,
        'extrusion_width': needle_diameter,
        'hinge_offset_angle': hinge_offset_angle,
        'print_speed' : print_speed
    }

#Checking he entered parameters whether they satisfy the constraints
def parameter_constraints(OD,ID,wb,wv,wh,t,we,n,hoa):

    ha=360/n
    a=(((OD-ID)/2)+wv)/(wb+wv)
    
    if a!=int(a):
        print("Enter the right value of beam and void width or alter the diameters according to the constraints")
        return False
    if (wb/we)!=int(wb/we):
        print("Enter a beam width value that is a multiple of the extrusion width")
        return False
    if (wh/we)%2 != 0:
        print("Enter a hinge width value that is a even multiple of extrusion width")
        return False
    if wh<1:
        print("Enter a hinge width that is atleast 1 mm")
        return False
    if wh<2*we:
        print("Enter a hinge width that is atleast twice the extrusion width")
        return False
    if n*wh>math.pi*ID/2:
        print("Your hinge width is beyond the limit to show enough flexibility in the structure")
        return False
    if (t/we) != int(t/we):
        print("Enter a value for thickness of the structure that is a multiple of extrusion width")
        return False
    if hoa>ha/2 or hoa<0:
        print("The hinge offset angle should be less than",ha/2,"degrees and hreater than 0 degrees")
        return False
    
    else: 
        print("All parameters satisfy the contraints to get the tool path ready")
        return True

# Function to calculate the hinge angle
def calculate_hinge_angle(num_hinges):
    return 360 / num_hinges

# Function to calculate the hinge width angle based on target radius, hinge width, and extrusion width
def calculate_hinge_width_angle(hinge_width, extrusion_width, target_radius):
    sine_value = (hinge_width - extrusion_width) / (2 * target_radius)
    hinge_width_angle = math.degrees(2 * math.asin(sine_value))
    return hinge_width_angle

# Function to calculate the number of beams (bn)
def calculate_number_of_beams(outer_diameter, inner_diameter, beam_width, void_width):
    return int(((outer_diameter - inner_diameter) - 2 * void_width) / (2 * (beam_width + void_width)))

# Function to write G-code lines with optional speed parameter
def write_gcode(file, command, x, y, i=None, j=None, f=None):
    if command in ["G0", "G1"]:
        gcode_line = f"{command} X{x:.3f} Y{y:.3f} F{f:.0f}"
    elif command in ["G2", "G3"]:
        gcode_line = f"{command} X{x:.3f} Y{y:.3f} I{i:.3f} J{j:.3f} F{f:.0f}"
    
    file.write(gcode_line + "\n")

# Function to draw concentric circles and hinges with hinge offset
def draw_circles_and_hinges(file, outer_diameter, inner_diameter, extrusion_width, beam_width, void_width, num_hinges, hinge_width, hinge_offset_angle, print_speed):
    bn = calculate_number_of_beams(outer_diameter, inner_diameter, beam_width, void_width)
    outer_radius = outer_diameter / 2
    target_radius = outer_radius - (extrusion_width / 2)

    # Calculated speed values
    rapid_value = 1800
    f_value = 60 * print_speed
    f_double = 2 * f_value

    for beam in range(bn):
        be = beam_width / extrusion_width
        num_complete_circles = int(be - 1)
        hinge_angle = calculate_hinge_angle(num_hinges)
        hinge_width_angle = calculate_hinge_width_angle(hinge_width, extrusion_width, target_radius)

        for i in range(num_complete_circles):
            if i == 0 and beam == 0:
                t.penup()
                t.goto(0, -target_radius)
                t.setheading(0)
                t.circle(target_radius, hinge_width_angle / 2)
                t.pendown()
                global First_pos
                First_pos=[]
                first_pos = t.pos()
                First_pos.append(round(first_pos[0],3))
                First_pos.append(round(first_pos[1],3))
                start_pos= t.pos()
                t.circle(target_radius)
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value) #add the speed user gave here (print speed)
                target_radius -= extrusion_width
            elif i == 0 and beam > 0:
                start_pos = t.pos()
                t.circle(target_radius)
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value)  #add print speed here
                target_radius -= extrusion_width
            elif i > 0 and beam >= 0:
                t.left(90)
                t.forward(extrusion_width)
                pos = t.pos()
                write_gcode(file, "G1", pos[0], pos[1], f=f_value)
                t.right(90)
                start_pos = t.pos()
                t.circle(target_radius)
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value)
                target_radius -= extrusion_width

        hinge_width_angle = calculate_hinge_width_angle(hinge_width, extrusion_width, target_radius)
        
        t.left(90)
        t.forward(extrusion_width)
        t.right(90)
        start_pos = t.pos()
        write_gcode(file, "G1", start_pos[0], start_pos[1], f=f_value)
        if beam>0:
            t.circle(target_radius, -hinge_offset_angle)
            end_pos=t.pos()
            write_gcode(file, "G2", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_double) #add 2 times the print speed here
            start_pos=t.pos()
            t.circle(target_radius, hinge_offset_angle) 
            end_pos=t.pos()
            write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_double) #add 2 times the print speed here
        
        # Now adding the hinges
        for hinge_num in range(num_hinges):

            arc_angle = hinge_angle - hinge_width_angle
            start_pos = t.pos()
            if hinge_num == 0 and beam>0:
                t.circle(target_radius, (arc_angle - hinge_offset_angle))
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value) #add print speed here
            else:
                t.circle(target_radius, arc_angle)
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value) #add print speed here

            # Draw void for hinge
            t.left(90)
            t.forward(void_width + (extrusion_width/2))
            pos = t.pos()
            write_gcode(file, "G1", pos[0], pos[1], f=f_value)

            t.right(90)
            start_pos = t.pos()
            t.circle(target_radius - (void_width + (extrusion_width/2)), hinge_width_angle)
            end_pos = t.pos()
            write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value)

            if hinge_num < num_hinges - 1:
                t.right(90)
                t.forward(void_width + (extrusion_width/2))
                pos = t.pos()
                write_gcode(file, "G1", pos[0], pos[1], f=f_value) #add print speed here
                t.left(90)
            elif hinge_num == num_hinges - 1:
                t.right(90)
                t.forward(void_width + (extrusion_width/2))
                pos = t.pos()
                write_gcode(file, "G1", pos[0], pos[1], f=f_double) #add 2 times the print speed here
                t.backward(void_width + extrusion_width)
                pos = t.pos()
                write_gcode(file, "G1", pos[0], pos[1], f=f_double) #add 2 times the print speed here
                t.left(90)

        target_radius -= (void_width + extrusion_width)

        if beam == bn - 1:
            for i in range(num_complete_circles + 1):
                start_pos = t.pos()
                t.circle(target_radius)
                end_pos = t.pos()
                write_gcode(file, "G3", end_pos[0], end_pos[1], -start_pos[0], -start_pos[1], f=f_value) #add print speed here
                if i < num_complete_circles:
                    t.left(90)
                    t.forward(extrusion_width)
                    pos = t.pos()
                    write_gcode(file, "G1", pos[0], pos[1], f=f_value)
                    t.right(90)
                    target_radius -= extrusion_width

# Gather inputs from the user
user_inputs = get_user_inputs()

C = parameter_constraints(user_inputs['outer_diameter'], user_inputs['inner_diameter'],user_inputs['beam_width'],user_inputs['void_width'],user_inputs['hinge_width'],user_inputs['thickness'],user_inputs['extrusion_width'],user_inputs['num_hinges'],user_inputs['hinge_offset_angle'])
parameter_constraints(user_inputs['outer_diameter'], user_inputs['inner_diameter'],user_inputs['beam_width'],user_inputs['void_width'],user_inputs['hinge_width'],user_inputs['thickness'],user_inputs['extrusion_width'],user_inputs['num_hinges'],user_inputs['hinge_offset_angle'])

if C is True:
    # Initialize turtle
    t = turtle.Turtle()
    t.speed(5)

    # Open G-code file for writing
    with open("Oddlayer.gcode", "w") as gcode_file:
        # Draw the concentric circles and add hinges
        draw_circles_and_hinges(
            gcode_file,
            user_inputs['outer_diameter'],
            user_inputs['inner_diameter'],
            user_inputs['extrusion_width'],
            user_inputs['beam_width'],
            user_inputs['void_width'],
            user_inputs['num_hinges'],
            user_inputs['hinge_width'],
            user_inputs['hinge_offset_angle'],
            user_inputs['print_speed']
        )

    # Keep the window open
    turtle.done()

#REVERSING THE GCODE TO OBTIAN THE EVEN LAYER TOOL PATH
# Parse the G-code line to extract the command, coordinates, and I, J values if present
def parse_gcode_line(line):
    match = re.match(r"(G[0231])(?: X([-+]?\d*\.\d+|\d+))?(?: Y([-+]?\d*\.\d+|\d+))?(?: I([-+]?\d*\.\d+|\d+))?(?: J([-+]?\d*\.\d+|\d+))?(?: F(\d+))?", line)
    if match:
        command = match.group(1)
        x = float(match.group(2)) if match.group(2) else None
        y = float(match.group(3)) if match.group(3) else None
        i = float(match.group(4)) if match.group(4) else None
        j = float(match.group(5)) if match.group(5) else None
        f = float(match.group(6)) if match.group(6) else None
        return command, x, y, i, j, f
    return None, None, None, None, None, None

# Format a G-code line for writing
def format_gcode_line(command, x, y, i=None, j=None, f=None):
    line = f"{command}"
    if x is not None:
        line += f" X{x:.3f}"
    if y is not None:
        line += f" Y{y:.3f}"
    if i is not None:
        line += f" I{i:.3f}"
    if j is not None:
        line += f" J{j:.3f}"
    if f is not None:
        line += f" F{f:.0f}"
    return line

# Process G-code lines according to the algorithm
def reverse_gcode_with_algorithm(gcode_lines):
    # Reverse the lines initially
    reversed_sequence = gcode_lines[::-1]
    reversed_gcode = []
    
    i = 0
    while i < len(reversed_sequence) - 1:
        current_line = reversed_sequence[i]
        next_line = reversed_sequence[i + 1]
        
        # Parse current and next line
        current_cmd, x, y, i_val, j_val, f_value = parse_gcode_line(current_line)
        next_cmd, next_x, next_y, next_i, next_j, next_f = parse_gcode_line(next_line)
        
        if current_cmd in ["G2", "G3"]:
            # Rule 3: Check if I and J are negative of X, Y
            if i_val == -x and j_val == -y:
                # Convert G2 <-> G3
                new_cmd = "G3" if current_cmd == "G2" else "G2"
                reversed_gcode.append(format_gcode_line(new_cmd, x, y, i_val, j_val, f_value))
            
            # Rule 4: Adjust I, J values and swap X, Y with next line
            else:
                new_cmd = "G3" if current_cmd == "G2" else "G2"
                new_i = -x if i_val is not None and x is not None else i_val
                new_j = -y if j_val is not None and y is not None else j_val
                reversed_gcode.append(format_gcode_line(new_cmd, next_x, next_y, new_i, new_j, f_value))
        
        elif current_cmd in ["G1", "G0"]:
            # Rule 5: Swap X, Y with next line and keep I, J if present in next line
            reversed_gcode.append(format_gcode_line(current_cmd, next_x, next_y, None, None, f_value))
        i += 1
    
    # Handle last line if needed
    if i == len(reversed_sequence) - 1:
        reversed_gcode.append(reversed_sequence[i])
    
    return reversed_gcode

# Main function to read from and write to files
def reverse_gcode_file(input_file, output_file):
    with open(input_file, 'r') as file:
        gcode_lines = file.readlines()
    
    # Apply algorithm to reverse G-code
    reversed_gcode = reverse_gcode_with_algorithm([line.strip() for line in gcode_lines])
    
    # Write to output file
    with open(output_file, 'w') as file:
        for line in reversed_gcode:
            file.write(line + '\n')

input_file = 'Oddlayer.gcode'
output_file = 'Evenlayer.gcode'
reverse_gcode_file(input_file, output_file)

#Creating the final tool path file
def generate_gcode_with_layers(first_pos, layer_height, total_layers, odd_layer_file, even_layer_file, output_file):
    # Read odd and even layer G-code from files
    with open(odd_layer_file, 'r') as file:
        odd_layer_code = file.readlines()

    with open(even_layer_file, 'r') as file:
        even_layer_code = file.readlines()

    with open(output_file, 'w') as file:
        # Write the header
        file.write("G21\n")  # Set units to mm
        file.write("G90\n")  # Absolute positioning
        file.write("G28\n")  # Home all axes
        file.write("G0 Z20 F600\n")  # Raise to a safe height
        file.write(f"G0 X{first_pos[0]} Y{first_pos[1]} F1800\n")  # Move to starting position
        file.write(f"G0 Z{layer_height} F600\n")  # Move to the first layer height
        file.write("M7\n")  # Turn on mist coolant (or another command)

        # Write layers
        for layer in range(total_layers):
            z_position = layer_height * (layer + 1)  # Calculate current layer height
            if layer % 2 == 0:  # Odd layer (0, 2, 4...)
                if layer>0:
                    file.write(f"G0 Z{z_position} F600\n")  # Move to the odd layer height
                file.writelines(odd_layer_code)  # Append odd layer code
            else:  # Even layer (1, 3, 5...)
                file.write(f"G0 Z{z_position} F600\n")  # Move to the even layer height
                file.writelines(even_layer_code)  # Append even layer code

        # Write the footer
        file.write("M9\n")  # Turn off coolant
        file.write("G0 Z20 F300\n")  # Move to safe height
        file.write("G0 X0 Y0 F1800\n")  # Return to home position
        file.write("M30\n")  # End of program

# Example usage
layer_height = user_inputs['extrusion_width']  # Height of each layer (extrusion width)
total_layers = int(user_inputs['thickness']/user_inputs['extrusion_width'])  # Total number of layers to create
odd_layer_file = 'Oddlayer.gcode'  # Input file for odd layers
even_layer_file = 'Evenlayer.gcode'  # Input file for even layers
output_file = 'Your_path.gcode'  # Output G-code file name

generate_gcode_with_layers(First_pos, layer_height, total_layers, odd_layer_file, even_layer_file, output_file)
