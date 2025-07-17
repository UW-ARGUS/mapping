import trimesh

# Path to your GLB file
glb_path = 'glbtest.glb'  # Change this to your file name

# Load the GLB file
mesh = trimesh.load(glb_path)

# Display it in a window (pyglet viewer)
mesh.show()