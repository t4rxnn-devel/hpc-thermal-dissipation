import FreeCAD
import Part
import Draft

def create_microchannel_cold_plate():
    # Initialize a new active document
    doc = FreeCAD.newDocument("ColdPlateModel")

    # 1. Create the main OFHC Copper Base Plate (100mm x 100mm x 10mm)
    base_length = 100.0
    base_width = 100.0
    base_thickness = 10.0
    
    block = doc.addObject("Part::Box", "BasePlate")
    block.Length = base_length
    block.Width = base_width
    block.Height = base_thickness

    # 2. Define and carve parallel micro-channels on the top surface
    # Simulating a series of channel cuts for liquid coolant flow
    num_channels = 10
    channel_width = 2.0
    channel_depth = 5.0
    channel_pitch = 8.0
    
    cut_tools = []
    start_offset = 10.0

    for i in range(num_channels):
        x_pos = start_offset + (i * channel_pitch)
        
        # Create cutting tool shape for each micro-channel groove
        channel = doc.addObject("Part::Box", f"Channel_{i}")
        channel.Length = channel_width
        channel.Width = 80.0  # span across the plate length
        channel.Height = channel_depth
        
        # Position the channel cut tool into the top face of the base plate
        channel.Placement = FreeCAD.Placement(
            FreeCAD.Vector(x_pos, 10.0, base_thickness - channel_depth), 
            FreeCAD.Rotation(0, 0, 0)
        )
        cut_tools.append(channel)

    # 3. Perform Boolean Cut operation using FreeCAD Part MultiFuse / Cut architecture
    # Grouping channels to cut out of the primary copper block
    if cut_tools:
        fusion = doc.addObject("Part::MultiFuse", "ChannelFusion")
        fusion.Shapes = cut_tools
        
        cut_operation = doc.addObject("Part::Cut", "ColdPlateWithChannels")
        cut_operation.Base = block
        cut_operation.Tool = fusion

    doc.recompute()

    # 4. Export the resulting geometry directly as a .STEP file into the geometry directory
    output_path = "geometry/cold_plate.STEP"
    shapes_to_export = [cut_operation if cut_tools else block]
    Part.export(shapes_to_export, output_path)
    
    print(f"Successfully exported open-source parametric CAD file to: {output_path}")

if __name__ == "__main__":
    create_microchannel_cold_plate()
