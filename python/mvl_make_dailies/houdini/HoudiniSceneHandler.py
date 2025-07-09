import os
import sys
import hou

from mvl_make_dailies.common_utils import logger
class HoudiniSceneHandler:
    def __init__(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Houdini file not found: {file_path}")
        self.file_path = file_path


    def get_scene_frame_range(self):
        start, end = hou.playbar.frameRange()
        return range(start, end)

    def load_scene(self):
        """
        Load the .hip file into the Houdini session.
        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            hou.hipFile.load(self.file_path, suppress_save_prompt=True)
            return True
        except Exception as e:
            logger.error(f"Failed to load Houdini file '{self.file_path}': {e}")
            return False
        
    def save(self, file_name=None):
        """
        Save the current Houdini scene.
        If file_name is provided, save to that path; otherwise, save to the original file path.
        """
        if file_name is None:
            file_name = self.file_path

        try:
            hou.hipFile.save(file_name, save_to_recent_files=True)
            logger.info(f"Scene saved successfully to {file_name}")
        except Exception as e:
            logger.error(f"Failed to save Houdini file '{file_name}': {e}")

    def list_cameras(self):
        """Return all camera node paths in the scene."""
        return self.list_nodes_by_type("cam")

    def list_object_nodes(self):
        return self.list_nodes_by_type("obj")

    def list_rop_nodes(self):
        return self.list_nodes_by_type("out")

    def list_nodes_by_type(self, type_names, parent_path="/obj"):
        """
        Return all node paths in the scene matching the specified type(s).
        
        Args:
            type_names (str or list of str): Node type(s) to search for (e.g., "cam", ["geo", "cam"]).
            parent_path (str): Root path to search under, default is "/obj".
        
        Returns:
            List[str]: Full Houdini paths to matching nodes.
        """
        if isinstance(type_names, str):
            type_names = [type_names]

        found_nodes = []
        parent_node = hou.node(parent_path)

        if not parent_node:
            raise ValueError(f"Invalid parent path: {parent_path}")

        for node in parent_node.children():
            if node.type().name() in type_names:
                found_nodes.append(node.path())

        return found_nodes
           
    def get_fps(self):
        """Return the frame rate of the current scene."""
        return hou.fps()

    def get_frame_range(self):
        """Return the start and end frame of the scene."""
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        return start, end

    def get_resolution(self):
        """Return the resolution from camera render settings (first cam found)."""
        for cam_path in self.list_cameras():
            cam = hou.node(cam_path)
            resx = cam.parm("resx").eval()
            resy = cam.parm("resy").eval()
            return resx, resy
        return None, None

    def get_scene_metadata(self):
        """Return all basic info as a dictionary."""
        return {
            "fps": self.get_fps(),
            "frame_range": self.get_frame_range(),
            "cameras": self.list_cameras(),
            "resolution": self.get_resolution(),
        }

    def getCameraPath(self, view=None):
        """
        Return the path of the active camera in the current viewport.
        Returns None if the viewport is in perspective/non-camera mode.
        """
        if hou.isUIAvailable() is False:
            #camera = [n for n in hou.node("/obj").children() if n.type().name().lower() == view.lower()] if view else []
            for camera in hou.node("/obj").children():
                logger.info(f"Checking camera: {camera.name()} of type {camera.type().name()}")
                if camera.type().name() == "cam" and (view is None or camera.name() == view):
                    return camera.path()
            # if camera:
            #     return camera[0].path()
            # else:
            #     print(f"No camera found for view: {view}")
            #     return None 
        else:
            try:
                viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
                if not viewer:
                    print("No Scene Viewer pane found.")
                    return None

                viewport = viewer.curViewport()
                camera = viewport.camera()
                return camera.path() if camera else None
            except Exception as e:
                print(f"Error fetching active camera: {e}")
                return None
