
from abc import ABC, abstractmethod
import hou
import os

from mvl_make_dailies.common_utils import logger
class BaseRenderStrategy(ABC):
    @abstractmethod
    def render(self, **kwargs):
        """Render the scene."""
        pass


class FlipbookRenderStrategy(BaseRenderStrategy):
    def __init__(self, scene_handler):
        self.scene = scene_handler
        self.viewer = self._get_viewer()

    def _get_viewer(self):
        for pane in hou.ui.paneTabs():
            if isinstance(pane, hou.SceneViewer):
                return pane
        raise RuntimeError("No Scene Viewer available.")

    def render(self, camera_path=None, output_path=None, start_frame=None, end_frame=None, res_x=1920, res_y=1080):
        if camera_path is None:
            cameras = self.scene.list_cameras()
            if not cameras:
                raise RuntimeError("No cameras found.")
            camera_path = cameras[0]

        cam = hou.node(camera_path)
        if cam is None:
            raise ValueError(f"Camera not found: {camera_path}")

        if start_frame is None or end_frame is None:
            start_frame, end_frame = self.scene.get_frame_range()

        flipbook_dir = os.path.join(os.path.dirname(output_path), "flipbook_temp")
        os.makedirs(flipbook_dir, exist_ok=True)
        flip_path = os.path.join(flipbook_dir, "frame.$F4.exr")

        opts = self.viewer.flipbookSettings()
        #opts.camera(cam)
        opts.frameRange((start_frame, end_frame))
        opts.resolution((res_x, res_y))
        opts.output(flip_path)

        print("Flipbooking...")
        self.viewer.flipbook(self.viewer.curViewport(), opts)
        print("Flipbook complete.")
        return flip_path

class RopRenderStrategy(BaseRenderStrategy):
    def __init__(self, scene_handler):
        self.scene = scene_handler

    def list_available_rops(self):
        """List all ROP nodes under the given ROP network."""
        return self.scene.list_rop_nodes()

    def get_or_create_default_rop(self, rop_root="/out", rop_type="ifd", rop_name="auto_render"):
        """
        Returns an existing ROP or creates a new one if none are found.

        Args:
            rop_root (str): Path to the ROP network (usually '/out').
            rop_type (str): Node type to create if needed ('ifd' for Mantra, 'karma', etc.)
            rop_name (str): Name of the node to create if needed.

        Returns:
            hou.Node: A valid ROP node ready to render.
        """
        rops = self.list_available_rops()
        if rops:
           logger.info(f"rop nodes {rops}")

        ropnet = hou.node(rop_root)
        if not ropnet:
            ropnet = hou.node("/").createNode("ropnet", "out")

        new_rop = ropnet.createNode(rop_type, node_name=rop_name)
        new_rop.moveToGoodPosition()
        return new_rop

    def setup_stage_for_karma(self):
        """
        Sets up /stage for Karma rendering:
        - Imports all geo nodes from /obj
        - Imports the first camera from /obj
        - Adds a dome light
        - Merges all into a single USD graph
        """
        stage = hou.node("/stage")
        if not stage:
            raise RuntimeError("No /stage context found.")

        # Import all geo nodes
        geo_nodes = [n for n in hou.node("/obj").children() if n.type().name().lower() == "geo"]
        sop_import_nodes = []
        for geo in geo_nodes:
            node_name = f"import_{geo.name()}"
            sop_import = stage.node(node_name) or stage.createNode("sopimport", node_name)
            sop_import.parm("soppath").set(geo.path())
            sop_import_nodes.append(sop_import)

        # Import first camera
        cam_nodes = [n for n in hou.node("/obj").children() if n.type().name().lower() == "cam"]
        cam_import = None
        if cam_nodes:
            cam_import = stage.node("import_cam") or stage.createNode("camimport", "import_cam")
            cam_import.parm("camerapath").set(cam_nodes[0].path())

        # Dome light
        dome_light = stage.node("dome_light") or stage.createNode("domelight", "dome_light")

        # Merge all
        merge = stage.node("merge_all") or stage.createNode("merge", "merge_all")
        idx = 0
        for sop_import in sop_import_nodes:
            merge.setInput(idx, sop_import)
            idx += 1
        if cam_import:
            merge.setInput(idx, cam_import)
            idx += 1
        merge.setInput(idx, dome_light)

        merge.setDisplayFlag(True)
        merge.setRenderFlag(True)
        logger.info("Stage setup for Karma: geometry, camera, and dome light merged.")

    def mantra_render_settings(self, rop, camera_path, start_frame, end_frame, output_path, res_x, res_y):
        rop.parm("trange").set(1)
        rop.parm("camera").set(camera_path)
        rop.parm("f1").set(start_frame)
        rop.parm("f2").set(end_frame)
        if output_path:
            output_path = os.path.join(output_path, "render")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            output_path = os.path.join(output_path, "image.$F4.exr")
            rop.parm("vm_picture").set(output_path)
        #rop.parm("resolutionx").set(res_x)
        #rop.parm("resolutiony").set(res_y)

    def karma_render_settings(self, rop, start_frame, end_frame, output_path, res_x, res_y):
        self.setup_stage_for_karma()
        rop.parm("trange").set(1)
        rop.parm("camera").set("/stage/import_cam")
        rop.parm("rendersettings").set("/stage/merge_all")
        rop.parm("f1").set(start_frame)
        rop.parm("f2").set(end_frame)
        if output_path:
            output_path = os.path.join(output_path, "render")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            output_path = os.path.join(output_path, "image.$F4.exr")
            rop.parm("picture").set(output_path)
        rop.parm("resolutionx").set(res_x)
        rop.parm("resolutiony").set(res_y)

    def render(self, camera_path=None, rop_type=None, start_frame=None, end_frame=None, output_path=None, res_x=None, res_y=None):
        rop = self.get_or_create_default_rop(
            rop_type=rop_type,
            rop_name="mvl_mantra" if rop_type == "ifd" else "mvl_karma"
        )

        if start_frame is None or end_frame is None:
            start_frame, end_frame = self.scene.get_frame_range()

        if rop_type == "ifd":
            self.mantra_render_settings(rop, camera_path, start_frame, end_frame, output_path, res_x, res_y)
        elif rop_type == "karma":
            self.karma_render_settings(rop, start_frame, end_frame, output_path, res_x, res_y)
        else:
            raise ValueError(f"Unsupported ROP type: {rop_type}")

        logger.info(f"Rendering via ROP: {rop.path()} outpath")
        rop.render(frame_range=(start_frame, end_frame))
        logger.info("ROP render complete.")