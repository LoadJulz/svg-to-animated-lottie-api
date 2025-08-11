#!/usr/bin/env python3
"""
SVG to Animated Lottie Converter

This module provides functions to convert base64-encoded SVG images to animated Lottie files
using the python-lottie library.
"""

import base64
import tempfile
import os
import json
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

try:
    from lottie import objects
    from lottie.importers.svg import import_svg
    from lottie.exporters.core import export_lottie
    from lottie import Point, Color
    from lottie.utils import animation as anim_utils
    from lottie.utils.animation import shake, rot_shake
except ImportError as e:
    raise ImportError(
        "Required lottie package not found. Please install with: pip install lottie[all]"
    ) from e


def decode_base64_svg(base64_svg: str) -> str:
    """
    Decode a base64-encoded SVG string.
    
    Args:
        base64_svg (str): Base64-encoded SVG string
        
    Returns:
        str: Decoded SVG content
        
    Raises:
        ValueError: If the base64 string is invalid
    """
    try:
        # Remove data URL prefix if present
        if base64_svg.startswith('data:image/svg+xml;base64,'):
            base64_svg = base64_svg.replace('data:image/svg+xml;base64,', '')
        
        # Decode base64
        svg_bytes = base64.b64decode(base64_svg)
        return svg_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decode base64 SVG: {str(e)}")


def create_basic_animation(lottie_animation: objects.Animation, animation_type: str = "fade_in") -> objects.Animation:
    """
    Add basic animation effects to a Lottie animation using predefined animations.
    
    Args:
        lottie_animation: The base Lottie animation object
        animation_type: Type of animation to apply ("fade_in", "scale_up", "rotate", "bounce", "shake")
        
    Returns:
        objects.Animation: The animated Lottie object
    """
    if not lottie_animation.layers:
        return lottie_animation
    
    # Set animation duration (in frames, 30fps default)
    duration = 60  # 2 seconds at 30fps
    lottie_animation.out_point = duration
    
    # Apply animation to all layers
    for layer in lottie_animation.layers:
        if hasattr(layer, 'transform'):
            transform = layer.transform
            
            if animation_type == "fade_in":
                # Fade in animation - manual implementation since fade_in might not be available
                transform.opacity.add_keyframe(0, 0)
                transform.opacity.add_keyframe(30, 100)
                
            elif animation_type == "scale_up":
                # Scale up animation - manual implementation
                transform.scale.add_keyframe(0, Point(10, 10))
                transform.scale.add_keyframe(30, Point(100, 100))
                
            elif animation_type == "rotate":
                # Continuous rotation animation - manual implementation for smooth 360° rotation
                transform.rotation.add_keyframe(0, 0)
                transform.rotation.add_keyframe(duration, 360)
                
            elif animation_type == "bounce":
                # Bounce animation using scale with manual keyframes
                transform.scale.add_keyframe(0, Point(100, 100))
                transform.scale.add_keyframe(15, Point(120, 120))
                transform.scale.add_keyframe(30, Point(100, 100))
                transform.scale.add_keyframe(45, Point(110, 110))
                transform.scale.add_keyframe(60, Point(100, 100))
    return lottie_animation


def create_complex_animation(lottie_animation: objects.Animation, 
                           effects: Dict[str, Any] = None) -> objects.Animation:
    """
    Create more complex animations with multiple effects using predefined animations.
    
    Args:
        lottie_animation: The base Lottie animation object
        effects: Dictionary of animation effects and their parameters
        
    Returns:
        objects.Animation: The animated Lottie object
    """
    if effects is None:
        effects = {
            "duration": 90,  # 3 seconds at 30fps
            "fade_in": {"start": 0, "end": 30},
            "scale_pulse": {"start": 30, "end": 60},
            "rotation": {"start": 60, "end": 90, "degrees": 360}
        }
    
    duration = effects.get("duration", 90)
    lottie_animation.out_point = duration
    
    for layer in lottie_animation.layers:
        if hasattr(layer, 'transform'):
            transform = layer.transform
            
            # Fade in effect - manual implementation
            if "fade_in" in effects:
                fade = effects["fade_in"]
                transform.opacity.add_keyframe(fade["start"], 0)
                transform.opacity.add_keyframe(fade["end"], 100)
            
            # Scale pulse effect - manual implementation
            if "scale_pulse" in effects:
                pulse = effects["scale_pulse"]
                mid_point = (pulse["start"] + pulse["end"]) // 2
                transform.scale.add_keyframe(pulse["start"], Point(100, 100))
                transform.scale.add_keyframe(mid_point, Point(130, 130))
                transform.scale.add_keyframe(pulse["end"], Point(100, 100))
            
            # Rotation effect using manual keyframes for continuous rotation
            if "rotation" in effects:
                rot = effects["rotation"]
                degrees = rot.get("degrees", 360)
                # Use manual keyframes for smooth continuous rotation
                transform.rotation.add_keyframe(rot["start"], 0)
                transform.rotation.add_keyframe(rot["end"], degrees)
            
            # Shake effect if specified
            if "shake" in effects:
                shake_params = effects["shake"]
                # shake(property, amplitude, frequency, start, end, loops)
                shake(transform.position, 
                      shake_params.get("amplitude", 10), 
                      shake_params.get("frequency", 2), 
                      shake_params["start"], 
                      shake_params["end"], 
                      5)
    
    return lottie_animation


def svg_to_animated_lottie(base64_svg: str, 
                          output_path: str,
                          animation_type: str = "fade_in",
                          custom_effects: Optional[Dict[str, Any]] = None,
                          fps: int = 30,
                          size: Optional[Tuple[int, int]] = None) -> str:
    """
    Convert a base64-encoded SVG to an animated Lottie file.
    
    Args:
        base64_svg (str): Base64-encoded SVG string
        output_path (str): Path where the Lottie file should be saved
        animation_type (str): Type of basic animation ("fade_in", "scale_up", "rotate", "bounce", "complex")
        custom_effects (Dict[str, Any], optional): Custom animation effects for complex animations
        fps (int): Frames per second for the animation (default: 30)
        size (Tuple[int, int], optional): Width and height for the animation (default: derived from SVG)
        
    Returns:
        str: Path to the created Lottie file
        
    Raises:
        ValueError: If SVG decoding fails
        IOError: If file operations fail
    """
    
    # Decode the base64 SVG
    svg_content = decode_base64_svg(base64_svg)
    
    # Create temporary SVG file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
        temp_svg.write(svg_content)
        temp_svg_path = temp_svg.name
    
    try:
        # Import SVG to Lottie
        lottie_animation = import_svg(temp_svg_path)
        
        # Set basic properties
        lottie_animation.frame_rate = fps
        
        # Set standard dimensions for consistent filling behavior
        target_width = size[0] if size else 512
        target_height = size[1] if size else 512
        
        lottie_animation.width = target_width
        lottie_animation.height = target_height
        
        # Calculate the bounds of all layers to determine scaling needed
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
        
        # First pass: find the content bounds
        for layer in lottie_animation.layers:
            if hasattr(layer, 'shapes') and layer.shapes:
                # Estimate content bounds (simplified approach)
                min_x = min(min_x, 0)
                min_y = min(min_y, 0)
                max_x = max(max_x, 100)  # Assume typical SVG viewBox
                max_y = max(max_y, 100)
        
        # If no bounds found, use default
        if min_x == float('inf'):
            min_x, min_y, max_x, max_y = 0, 0, 100, 100
            
        content_width = max_x - min_x
        content_height = max_y - min_y
        
        # Calculate scale to fill the canvas (with some padding)
        scale_x = (target_width * 0.9) / content_width if content_width > 0 else 1
        scale_y = (target_height * 0.9) / content_height if content_height > 0 else 1
        fill_scale = min(scale_x, scale_y) * 100  # Convert to percentage
        
        # Second pass: position and scale all layers to fill the view
        for layer in lottie_animation.layers:
            if hasattr(layer, 'transform'):
                # Center the layer
                layer.transform.position.value = [target_width // 2, target_height // 2]
                
                # Apply scaling to ensure content fills the view
                if hasattr(layer.transform, 'scale'):
                    layer.transform.scale.value = [fill_scale, fill_scale]
                
                # Ensure anchor point is at center for proper rotation/scaling
                if hasattr(layer.transform, 'anchor_point'):
                    layer.transform.anchor_point.value = [50, 50]  # Center anchor point
        
        # Apply animations
        if animation_type == "complex":
            lottie_animation = create_complex_animation(lottie_animation, custom_effects)
        else:
            lottie_animation = create_basic_animation(lottie_animation, animation_type)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create directory if there is one
            os.makedirs(output_dir, exist_ok=True)
        
        # Export to Lottie JSON with viewport filling configuration
        lottie_dict = lottie_animation.to_dict()
        
        # Ensure proper viewport and scaling metadata
        lottie_dict.update({
            "w": target_width,
            "h": target_height,
            "ip": 0,  # in point
            "op": lottie_animation.out_point,  # out point
            "fr": fps,  # frame rate
            # Add metadata for better rendering behavior
            "meta": {
                "g": "SVG to Lottie Converter",
                "a": "",
                "k": "",
                "d": "",
                "tc": ""
            }
        })
        
        # Ensure all layers have proper bounds and transforms
        if "layers" in lottie_dict:
            for layer_dict in lottie_dict["layers"]:
                if "ks" in layer_dict and "p" in layer_dict["ks"]:
                    # Ensure position is centered
                    if "k" in layer_dict["ks"]["p"]:
                        layer_dict["ks"]["p"]["k"] = [target_width // 2, target_height // 2]
                
                # Ensure layer has proper bounds
                layer_dict["w"] = target_width
                layer_dict["h"] = target_height
        
        with open(output_path, 'w') as output_file:
            json.dump(lottie_dict, output_file, indent=2)
        
        return output_path
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_svg_path):
            os.unlink(temp_svg_path)


def create_sample_animated_lottie():
    """
    Create a sample animated Lottie from a simple SVG for demonstration.
    """
    
    # Encode to base64
    svg_base64 = 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE4LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPg0KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4NCjxzdmcgdmVyc2lvbj0iMS4xIiBpZD0iQ2FwYV8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCINCgkgdmlld0JveD0iMCAwIDYwIDYwIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCA2MCA2MDsiIHhtbDpzcGFjZT0icHJlc2VydmUiPg0KPHBhdGggZD0iTTU5Ljk4OSwyMWMtMC4wOTktMS43MTEtMi4xMzQtMy4wNDgtNi4yMDQtNC4wNjhjMC4xMzctMC4zLDAuMjE0LTAuNjEyLDAuMjE1LTAuOTM2VjloLTAuMDE3QzUzLjYyNSwzLjE3MiwyOS43NDMsMywyNywzDQoJUzAuMzc1LDMuMTcyLDAuMDE3LDlIMHYwLjEzdjB2MGwwLDYuODY5YzAuMDA1LDEuOSwyLjQ1NywzLjM4Nyw2LjEwNSw0LjQ5NGMtMC4wNSwwLjE2Ni0wLjA4LDAuMzM1LTAuMDksMC41MDdINnYwLjEzdjB2MGwwLDYuODU3DQoJQzIuMDcsMjguOTk5LDAuMTA3LDMwLjMxNywwLjAxLDMySDB2MC4xM3YwdjBsMCw2Ljg2OWMwLjAwMywxLjMyMywxLjE5NiwyLjQ0NSwzLjE0OCwzLjM4Yy0wLjA3NCwwLjIwMy0wLjEyLDAuNDEtMC4xMzMsMC42MjJIMw0KCXYwLjEzdjB2MGwwLDYuODY5YzAuMDA4LDMuMzI2LDcuNDk3LDUuMzkxLDE1LjgxOCw2LjM1NWMwLjA2MSwwLjAxMiwwLjExNywwLjAzNywwLjE4MiwwLjAzN2MwLjAxOSwwLDAuMDM1LTAuMDEsMC4wNTQtMC4wMTENCgljMS42MDQsMC4xODEsMy4yMzQsMC4zMjIsNC44NDcsMC40MjNjMC4wMzQsMC4wMDQsMC4wNjQsMC4wMiwwLjA5OSwwLjAyYzAuMDE5LDAsMC4wMzQtMC4wMSwwLjA1Mi0wLjAxMQ0KCUMyNi4xLDU2LjkzNywyOC4xMTUsNTcsMzAsNTdjMS44ODUsMCwzLjktMC4wNjMsNS45NDgtMC4xODhjMC4wMTgsMC4wMDEsMC4wMzQsMC4wMTEsMC4wNTIsMC4wMTFjMC4wMzUsMCwwLjA2NS0wLjAxNywwLjA5OS0wLjAyDQoJYzEuNjEzLTAuMTAxLDMuMjQzLTAuMjQxLDQuODQ3LTAuNDIzQzQwLjk2NSw1Ni4zOCw0MC45ODEsNTYuMzksNDEsNTYuMzljMC4wNjUsMCwwLjEyMS0wLjAyNSwwLjE4Mi0wLjAzNw0KCWM4LjMyMS0wLjk2NCwxNS44MDktMy4wMywxNS44MTgtNi4zNTdWNDNoLTAuMDE2Yy0wLjA3LTEuMjI2LTEuMTE1LTIuMjQ5LTMuMTc5LTMuMTA0YzAuMTI2LTAuMjg5LDAuMTk1LTAuNTg5LDAuMTk1LTAuOVYzMi40Ng0KCWMzLjU5LTEuMTA0LDUuOTk1LTIuNTgxLDYtNC40NjRWMjFINTkuOTg5eiBNNTEuODkyLDM5LjMyMWwtMC4zNDEsMC4yOTlDNTEuMDI2LDQwLjA4Myw1MC4xNTEsNDAuNTUsNDksNDF2LTQuNzY4DQoJYzEuMTg5LTAuNDE0LDIuMjAxLTAuODczLDMtMS4zNzZ2NC4xMzhDNTIsMzkuMDk3LDUxLjk2MiwzOS4yMDcsNTEuODkyLDM5LjMyMXogTTI5LjUyNiw0My45NjgNCgljLTAuMTQ2LDAuMDA0LTAuMjkzLDAuMDA2LTAuNDQsMC4wMDljLTAuMzU3LDAuMDA3LTAuNzIzLDAuMDA5LTEuMDg1LDAuMDEydi00Ljk5NWMwLjI3NS0wLjAwMywwLjU1LTAuMDA3LDAuODI1LTAuMDEyDQoJYzAuMDUzLTAuMDAxLDAuMTA2LTAuMDAyLDAuMTU5LTAuMDAzYzEuMDA3LTAuMDE5LDIuMDE0LTAuMDUsMy4wMTYtMC4wOTZ2NC45OTNjLTAuMjE0LDAuMDExLTAuNDI5LDAuMDIxLTAuNjQ2LDAuMDMNCglDMzAuNzUzLDQzLjkzMywzMC4xNDUsNDMuOTUzLDI5LjUyNiw0My45Njh6IE0yNS4xNTksNDMuOTgyYy0wLjQ1OC0wLjAwOC0wLjkxNC0wLjAxOS0xLjM2Ny0wLjAzMw0KCWMtMC4wNTYtMC4wMDItMC4xMTItMC4wMDQtMC4xNjgtMC4wMDZjLTAuNTQ1LTAuMDE4LTEuMDg2LTAuMDQxLTEuNjIzLTAuMDY3di00Ljk5MmMxLjAwMiwwLjA0NywyLjAwOSwwLjA3OCwzLjAxNiwwLjA5Ng0KCWMwLjA1MywwLjAwMSwwLjEwNiwwLjAwMiwwLjE1OCwwLjAwM2MwLjI3NSwwLjAwNSwwLjU1LDAuMDA5LDAuODI1LDAuMDEydjQuOTk4Yy0wLjE5NC0wLjAwMi0wLjM4OC0wLjAwMi0wLjU4MS0wLjAwNQ0KCUMyNS4zMzEsNDMuOTg2LDI1LjI0Niw0My45ODMsMjUuMTU5LDQzLjk4MnogTTcuMDk3LDQxLjcwMkM3LjA2NCw0MS42OTIsNy4wMzMsNDEuNjgzLDcsNDEuNjc0di00LjgzMQ0KCWMwLjkzNCwwLjI1MiwxLjkzOCwwLjQ4MiwzLDAuNjkxdjQuODgxYy0wLjkxOC0wLjE5NS0xLjc2NS0wLjQtMi41MzYtMC42MUM3LjM0Miw0MS43Nyw3LjIxNiw0MS43MzcsNy4wOTcsNDEuNzAyeiBNMjguMTc1LDQ5Ljk4Mw0KCWMwLjI3NSwwLjAwNSwwLjU1LDAuMDA5LDAuODI1LDAuMDEydjQuOTk5Yy0xLjM4Mi0wLjAxMy0yLjcxNi0wLjA1My00LTAuMTE2di00Ljk5M2MxLjAwMiwwLjA0NywyLjAwOSwwLjA3OCwzLjAxNiwwLjA5Ng0KCUMyOC4wNjksNDkuOTgxLDI4LjEyMiw0OS45ODIsMjguMTc1LDQ5Ljk4M3ogTTMxLjk4NCw0OS45OGMxLjAwNy0wLjAxOSwyLjAxNC0wLjA1LDMuMDE2LTAuMDk2djQuOTkzDQoJYy0xLjI4NCwwLjA2My0yLjYxOCwwLjEwMy00LDAuMTE2di00Ljk5OWMwLjI3NS0wLjAwMywwLjU1LTAuMDA3LDAuODI1LTAuMDEyQzMxLjg3OCw0OS45ODIsMzEuOTMxLDQ5Ljk4MSwzMS45ODQsNDkuOTh6DQoJIE00MCw0OS41Mjh2NC45NjZjLTAuOTYxLDAuMTAxLTEuOTYxLDAuMTktMywwLjI2M3YtNC45ODdDMzguMDE0LDQ5LjcwNCwzOS4wMTYsNDkuNjIzLDQwLDQ5LjUyOHogTTQyLDQ5LjMxMg0KCWMxLjAzMS0wLjEyNCwyLjAzMi0wLjI2NSwzLTAuNDIydjQuOTFjLTAuOTQyLDAuMTY2LTEuOTQzLDAuMzE5LTMsMC40NThWNDkuMzEyeiBNNDcsNDguNTMzYzEuMDYyLTAuMjA5LDIuMDY2LTAuNDM5LDMtMC42OTF2NC44MzENCgljLTAuODkxLDAuMjU3LTEuODk0LDAuNTA2LTMsMC43NDFWNDguNTMzeiBNMTMsNDguNTMzdjQuODgxYy0xLjEwNi0wLjIzNS0yLjEwOS0wLjQ4NC0zLTAuNzQxdi00LjgzMQ0KCUMxMC45MzQsNDguMDk0LDExLjkzOCw0OC4zMjUsMTMsNDguNTMzeiBNMTUsNDguODkxYzAuOTY4LDAuMTU3LDEuOTY5LDAuMjk4LDMsMC40MjJ2NC45NDZjLTEuMDU3LTAuMTM5LTIuMDU4LTAuMjkyLTMtMC40NTgNCglWNDguODkxeiBNMjAsNDkuNTI4YzAuOTg0LDAuMDk1LDEuOTg2LDAuMTc2LDMsMC4yNDN2NC45ODdjLTEuMDM5LTAuMDczLTIuMDM5LTAuMTYyLTMtMC4yNjNWNDkuNTI4eiBNMTcuNTE5LDQzLjU0OA0KCWMtMC4xMDItMC4wMS0wLjIwMy0wLjAyMS0wLjMwNC0wLjAzMWMtMC4wNzItMC4wMDctMC4xNDMtMC4wMTYtMC4yMTUtMC4wMjN2LTQuOTY1YzAuOTg0LDAuMDk1LDEuOTg2LDAuMTc2LDMsMC4yNDN2NC45ODMNCglDMTkuMTYsNDMuNjk1LDE4LjMzLDQzLjYyNywxNy41MTksNDMuNTQ4eiBNMTUsMzguMzEydjQuOTQ2Yy0xLjA1Ny0wLjEzOS0yLjA1OC0wLjI5Mi0zLTAuNDU4di00LjkxDQoJQzEyLjk2OCwzOC4wNDcsMTMuOTY5LDM4LjE4OSwxNSwzOC4zMTJ6IE0zNC42NjYsNDMuNzA4Yy0wLjIyLDAuMDE3LTAuNDQyLDAuMDM0LTAuNjY2LDAuMDV2LTQuOTg3DQoJYzEuMDE0LTAuMDY3LDIuMDE2LTAuMTQ3LDMtMC4yNDN2NC45NjZjLTAuNjE4LDAuMDY1LTEuMjUsMC4xMjYtMS44OTksMC4xNzlDMzQuOTU2LDQzLjY4NiwzNC44MTEsNDMuNjk3LDM0LjY2Niw0My43MDh6DQoJIE0zOSw0My4yNTh2LTQuOTQ2YzEuMDMxLTAuMTI0LDIuMDMyLTAuMjY1LDMtMC40MjJ2NC45MUM0MS4wNTgsNDIuOTY2LDQwLjA1Nyw0My4xMiwzOSw0My4yNTh6IE00NCwzNy41MzMNCgljMS4wNjItMC4yMDksMi4wNjYtMC40MzksMy0wLjY5MXY0LjgzMWMtMC44OTEsMC4yNTctMS44OTQsMC41MDYtMywwLjc0MVYzNy41MzN6IE0zMC4zMjUsMzIuOTY1DQoJYy0wLjc1Mi0wLjAxOS0xLjQ4Ny0wLjA0OC0yLjIwOS0wLjA4M2MtMC4wMzktMC4wMDItMC4wNzgtMC4wMDQtMC4xMTYtMC4wMDV2LTQuOTkzYzEuMDAyLDAuMDQ3LDIuMDA5LDAuMDc4LDMuMDE2LDAuMDk2DQoJYzAuMDUzLDAuMDAxLDAuMTA2LDAuMDAyLDAuMTU4LDAuMDAzYzAuMjc1LDAuMDA1LDAuNTUsMC4wMDksMC44MjUsMC4wMTJ2NC45OTNjLTAuNDg3LTAuMDA1LTAuOTc4LTAuMDA3LTEuNDUzLTAuMDE4DQoJQzMwLjQ3MywzMi45NjgsMzAuMzk4LDMyLjk2NywzMC4zMjUsMzIuOTY1eiBNNywxOC42NzR2LTQuODMxYzAuOTM0LDAuMjUyLDEuOTM4LDAuNDgyLDMsMC42OTF2NC44ODENCgljLTAuMTIzLTAuMDI2LTAuMjUtMC4wNTItMC4zNy0wLjA3OGMtMC41MzItMC4xMTctMS4wNTEtMC4yMzktMS41NDctMC4zNjhDNy43MDUsMTguODcyLDcuMzQ2LDE4Ljc3Myw3LDE4LjY3NHogTTI1LjE3NSwxNS45ODMNCgljMC4yNzUsMC4wMDUsMC41NSwwLjAwOSwwLjgyNSwwLjAxMnY0Ljk5M2MtMS4zNDYtMC4wMTMtMi42ODQtMC4wNDgtNC0wLjExNHYtNC45ODljMS4wMDIsMC4wNDcsMi4wMDksMC4wNzgsMy4wMTYsMC4wOTYNCglDMjUuMDY5LDE1Ljk4MSwyNS4xMjIsMTUuOTgyLDI1LjE3NSwxNS45ODN6IE0yOC45ODQsMTUuOThjMS4wMDctMC4wMTksMi4wMTQtMC4wNSwzLjAxNi0wLjA5NnY0Ljk4OQ0KCWMtMC4xNywwLjAwOC0wLjMzMywwLjAyLTAuNTA0LDAuMDI4Yy0wLjAxNCwwLjAwMS0wLjAyOCwwLjAwMS0wLjA0MywwLjAwMmMtMC42NzEsMC4wMy0xLjM1NSwwLjA1Mi0yLjA0OCwwLjA2OA0KCWMtMC4xMDgsMC4wMDMtMC4yMTYsMC4wMDQtMC4zMjQsMC4wMDdjLTAuMzU2LDAuMDA3LTAuNzIsMC4wMDgtMS4wODEsMC4wMTJ2LTQuOTk1YzAuMjc1LTAuMDAzLDAuNTUtMC4wMDcsMC44MjUtMC4wMTINCglDMjguODc4LDE1Ljk4MiwyOC45MzEsMTUuOTgxLDI4Ljk4NCwxNS45OHogTTUxLjc3MSwxNi40ODJsLTAuMDI4LTAuMDA2bC0wLjM2NCwwLjI4M0M1MC44NTEsMTcuMTcsNTAuMDQsMTcuNTg2LDQ5LDE3Ljk4OHYtNC43NTcNCgljMS4xODktMC40MTQsMi4yMDEtMC44NzMsMy0xLjM3NnY0LjEzOEM1MiwxNi4xNDUsNTEuOTIsMTYuMzA5LDUxLjc3MSwxNi40ODJ6IE0zOSwyMC4yNTJ2LTQuOTRjMS4wMzEtMC4xMjQsMi4wMzItMC4yNjUsMy0wLjQyMg0KCXY0LjkwMkM0MS4wNTIsMTkuOTYsNDAuMDU0LDIwLjExNCwzOSwyMC4yNTJ6IE00NCwxOS40MDd2LTQuODczYzEuMDYyLTAuMjA5LDIuMDY2LTAuNDM5LDMtMC42OTF2NC44Mg0KCUM0Ni4xMDQsMTguOTI0LDQ1LjA5NSwxOS4xNzMsNDQsMTkuNDA3eiBNMzcsMTUuNTI4djQuOTZjLTAuOTY2LDAuMTAyLTEuOTY2LDAuMTkxLTMsMC4yNjV2LTQuOTgyDQoJQzM1LjAxNCwxNS43MDQsMzYuMDE2LDE1LjYyMywzNywxNS41Mjh6IE0xNywyMC40OXYtNC45NjJjMC45ODQsMC4wOTUsMS45ODYsMC4xNzYsMywwLjI0M3Y0Ljk3OA0KCUMxOC45ODIsMjAuNjc2LDE3Ljk3OCwyMC41OTMsMTcsMjAuNDl6IE0xNSwxNS4zMTJ2NC45NDFjLTAuMTk4LTAuMDI2LTAuNDA0LTAuMDQ3LTAuNi0wLjA3NGMtMC4xMjgtMC4wMTgtMC4yNS0wLjAzNy0wLjM3Ni0wLjA1NQ0KCWMtMC41NzgtMC4wODMtMS4xNDMtMC4xNzItMS42OTctMC4yNjVDMTIuMjE2LDE5Ljg0LDEyLjEwOSwxOS44MiwxMiwxOS44MDF2LTQuOTFDMTIuOTY4LDE1LjA0NywxMy45NjksMTUuMTg5LDE1LDE1LjMxMnoNCgkgTTI1Ljc1MiwzMi43MzljLTAuMTM1LTAuMDEtMC4yNzEtMC4wMi0wLjQwNS0wLjAzYy0wLjY0LTAuMDUtMS4yNjUtMC4xMDUtMS44NzUtMC4xNjZjLTAuMTMxLTAuMDEzLTAuMjYyLTAuMDI3LTAuMzkyLTAuMDQNCglDMjMuMDUzLDMyLjUsMjMuMDI3LDMyLjQ5NiwyMywzMi40OTR2LTQuOTY2YzAuOTg0LDAuMDk1LDEuOTg2LDAuMTc2LDMsMC4yNDN2NC45ODRDMjUuOTE5LDMyLjc0OSwyNS44MzMsMzIuNzQ1LDI1Ljc1MiwzMi43Mzl6DQoJIE0xOS4xNDUsMzEuOTkyYy0wLjM5Ni0wLjA2My0wLjc2OC0wLjEzMS0xLjE0NS0wLjE5N3YtNC45MDRjMC45NjgsMC4xNTcsMS45NjksMC4yOTgsMywwLjQyMnY0Ljk0Ng0KCWMtMC42MTItMC4wODEtMS4yMTEtMC4xNjUtMS43ODYtMC4yNTVDMTkuMTkxLDMxLjk5OSwxOS4xNjgsMzEuOTk1LDE5LjE0NSwzMS45OTJ6IE0xNiwyNi41MzN2NC44NzMNCgljLTEuMTA1LTAuMjM3LTIuMTA3LTAuNDg5LTMtMC43NTF2LTQuODEzQzEzLjkzNCwyNi4wOTQsMTQuOTM4LDI2LjMyNSwxNiwyNi41MzN6IE0xMSwyNS4yMzF2NC43NTENCgljLTEuNTcyLTAuNjA3LTIuNTg2LTEuMjI3LTIuOTE2LTEuNzc5bC0wLjA2Ny0wLjExMkM4LjAxMSwyOC4wNiw4LjAwMSwyOC4wMjcsOCwyNy45OTZsMC00LjE0MQ0KCUM4Ljc5OSwyNC4zNTgsOS44MTEsMjQuODE3LDExLDI1LjIzMXogTTM0Ljk4NCwyNy45OGMxLjAwNy0wLjAxOSwyLjAxNC0wLjA1LDMuMDE2LTAuMDk2djQuOTg4Yy0xLjMxNCwwLjA2NS0yLjY1LDAuMTAxLTQsMC4xMTUNCgl2LTQuOTkyYzAuMjc1LTAuMDAzLDAuNTUtMC4wMDcsMC44MjUtMC4wMTJDMzQuODc4LDI3Ljk4MiwzNC45MzEsMjcuOTgxLDM0Ljk4NCwyNy45OHogTTQ3LjkwNywzMS44MTcNCgljLTAuNDM5LDAuMDc2LTAuODgyLDAuMTUxLTEuMzM3LDAuMjJjLTAuMjYxLDAuMDQtMC41MjgsMC4wNzgtMC43OTYsMC4xMTZjLTAuMjUzLDAuMDM2LTAuNTE2LDAuMDY3LTAuNzczLDAuMXYtNC45NDENCgljMS4wMzEtMC4xMjQsMi4wMzItMC4yNjUsMy0wLjQyMnY0LjkxQzQ3Ljk2OSwzMS44MDYsNDcuOTM4LDMxLjgxMiw0Ny45MDcsMzEuODE3eiBNNDEuMTM2LDMyLjY3MQ0KCWMtMC4zNzMsMC4wMzEtMC43NTgsMC4wNTEtMS4xMzYsMC4wNzh2LTQuOTc4YzEuMDE0LTAuMDY3LDIuMDE2LTAuMTQ3LDMtMC4yNDN2NC45NjFjLTAuNTgxLDAuMDYxLTEuMTYxLDAuMTIyLTEuNzU4LDAuMTcyDQoJQzQxLjIwNiwzMi42NjQsNDEuMTcyLDMyLjY2OCw0MS4xMzYsMzIuNjcxeiBNNTIuNTY0LDMwLjc5NmMtMC40OTgsMC4xMzktMS4wMjUsMC4yNjktMS41NjMsMC4zOTYNCgljLTAuMjQ5LDAuMDU4LTAuNTAzLDAuMTE2LTAuNzYzLDAuMTcyYy0wLjA3NywwLjAxNy0wLjE1OSwwLjAzMi0wLjIzNywwLjA0OXYtNC44NzljMS4wNjItMC4yMDksMi4wNjYtMC40MzksMy0wLjY5MXY0LjgzMQ0KCUM1Mi44NTcsMzAuNzE0LDUyLjcxMiwzMC43NTUsNTIuNTY0LDMwLjc5NnogTTU3Ljk4OSwyMS4wNjVjLTAuMDkyLDAuNjc5LTEuNjMxLDEuNTgyLTQuMzc4LDIuNDMxbDAsMA0KCWMtMy41MzgsMS4wOTMtOS4wNzQsMi4wOTQtMTYuMDksMi40MDRjLTAuMzU5LDAuMDE1LTAuNzE3LDAuMDMtMS4wODMsMC4wNDJjLTAuMjk5LDAuMDEtMC41OTksMC4wMTktMC45MDQsMC4wMjcNCglDMzQuNzA2LDI1Ljk4NywzMy44NjYsMjYsMzMsMjZzLTEuNzA2LTAuMDEzLTIuNTM0LTAuMDMyYy0wLjMwNC0wLjAwNy0wLjYwNC0wLjAxNy0wLjkwNC0wLjAyNw0KCWMtMC4zNjctMC4wMTEtMC43MjUtMC4wMjctMS4wODMtMC4wNDJjLTcuMDE2LTAuMzEtMTIuNTUzLTEuMzExLTE2LjA5LTIuNDA0bDAsMGMtMi43MjUtMC44NDItNC4yNjEtMS43MzgtNC4zNzUtMi40MTQNCgljMC4wMDUtMC4wMTksMC4wMDUtMC4wMzUsMC4wMTctMC4wNTljMC4wNjgsMC4wMTcsMC4xNDQsMC4wMzEsMC4yMTMsMC4wNDhjMC4zOTEsMC4wOTMsMC43OTIsMC4xODMsMS4yLDAuMjY5DQoJYzEuOTg3LDAuNDI4LDQuMTg5LDAuNzc5LDYuNTM1LDEuMDQ3YzAuMDA4LDAsMC4wMTQsMC4wMDQsMC4wMjEsMC4wMDRjMC4wMDIsMCwwLjAwNC0wLjAwMSwwLjAwNS0wLjAwMQ0KCWMxLjU5OCwwLjE4MiwzLjI1NiwwLjMyNSw0Ljk1OCwwLjQyNmMwLjAxMywwLDAuMDI0LDAuMDA3LDAuMDM3LDAuMDA3YzAuMDA3LDAsMC4wMTItMC4wMDQsMC4wMTktMC4wMDQNCgljMS4yMjUsMC4wNzIsMi40NjYsMC4xMjUsMy43MjIsMC4xNTNDMjUuNTEsMjIuOTksMjYuMjY1LDIzLDI3LDIzYzAuNTI1LDAsMS4wNjMtMC4wMDYsMS42MDYtMC4wMTYNCgljNy4yNjYtMC4xMTIsMTQtMC45NzYsMTguNjg2LTIuMzE1YzAuMjE2LTAuMDYxLDAuNDI3LTAuMTI0LDAuNjM1LTAuMTg3YzAuMTI3LTAuMDM5LDAuMjU3LTAuMDc3LDAuMzgtMC4xMTYNCgljMC4zNjItMC4xMTYsMC43MDktMC4yMzUsMS4wNDQtMC4zNTljMC4wNTgtMC4wMjIsMC4xMTMtMC4wNDQsMC4xNzEtMC4wNjZjMC4yODMtMC4xMDcsMC41NTUtMC4yMTgsMC44MTUtMC4zMzENCgljMC4wNzUtMC4wMzMsMC4xNTItMC4wNjUsMC4yMjUtMC4wOThjMC4yNzctMC4xMjUsMC41NDUtMC4yNTMsMC43OTMtMC4zODZjMC4xMTItMC4wNTksMC4yMDktMC4xMiwwLjMxNC0wLjE4DQoJYzAuMTItMC4wNjksMC4yNC0wLjEzOSwwLjM1MS0wLjIxYzAuMDYzLTAuMDQsMC4xMzgtMC4wNzgsMC4xOTgtMC4xMThDNTYuNjk1LDE5LjU4OSw1Ny44NzUsMjAuNjUxLDU3Ljk4OSwyMS4wNjV6IE0yNyw1DQoJYzE2LjQ4OSwwLDI0LjgyOSwyLjU5NiwyNC45ODUsNC4wODZjLTAuMTIxLDAuNjc2LTEuNjU2LDEuNTY5LTQuMzc0LDIuNDA5bDAsMGMtMy41MzgsMS4wOTMtOS4wNzQsMi4wOTQtMTYuMDksMi40MDQNCgljLTAuMzU5LDAuMDE1LTAuNzE3LDAuMDMtMS4wODMsMC4wNDJjLTAuMjk5LDAuMDEtMC41OTksMC4wMTktMC45MDQsMC4wMjdDMjguNzA2LDEzLjk4NywyNy44NjYsMTQsMjcsMTRzLTEuNzA2LTAuMDEzLTIuNTM0LTAuMDMyDQoJYy0wLjMwNC0wLjAwNy0wLjYwNC0wLjAxNy0wLjkwNC0wLjAyN2MtMC4zNjctMC4wMTEtMC43MjUtMC4wMjctMS4wODMtMC4wNDJjLTcuMDE2LTAuMzEtMTIuNTUzLTEuMzExLTE2LjA5LTIuNDA0bDAsMA0KCWMtMi43MTktMC44NC00LjI1My0xLjczMy00LjM3NC0yLjQwOUMyLjE3MSw3LjU5NiwxMC41MTEsNSwyNyw1eiBNMiwxNS45OTZsMC00LjE0MWMwLjc5OSwwLjUwMywxLjgxMSwwLjk2MiwzLDEuMzc2djQuNzg4DQoJQzMuMDU1LDE3LjI5LDIuMDAyLDE2LjU1OSwyLDE1Ljk5NnogTTYuODQ0LDI5LjgzNWMwLjAxNSwwLjAxNiwwLjAzOCwwLjAzLDAuMDUzLDAuMDQ2YzEuMzY5LDEuMzgyLDQuMjA0LDIuNDY4LDcuNzMzLDMuMjc4DQoJYzAuMDgxLDAuMDE5LDAuMTY3LDAuMDM3LDAuMjQ5LDAuMDU2YzAuMjU5LDAuMDU4LDAuNTIyLDAuMTE1LDAuNzg4LDAuMTdjMy4yNDEsMC42OSw3LjExLDEuMTg5LDExLjMyNSwxLjQzNg0KCWMwLjAwMywwLDAuMDA1LDAuMDAxLDAuMDA3LDAuMDAxYzAuMDAyLDAsMC4wMDMtMC4wMDEsMC4wMDQtMC4wMDFjMS4zNTQsMC4wNzksMi43MzksMC4xMzQsNC4xNTMsMC4xNTgNCglDMzEuNzgyLDM0Ljk5MiwzMi4zOTgsMzUsMzMsMzVjMC42OSwwLDEuMzk4LTAuMDA4LDIuMTE4LTAuMDI1YzEuMzA4LTAuMDI3LDIuNTk3LTAuMDgxLDMuODY4LTAuMTU1DQoJYzAuMDA1LDAsMC4wMDksMC4wMDMsMC4wMTQsMC4wMDNjMC4wMDksMCwwLjAxNi0wLjAwNSwwLjAyNS0wLjAwNWM0LjIyNi0wLjI0OSw4LjE5MS0wLjc1MywxMS41NDQtMS40NzgNCgljLTAuNzI2LDAuMzgtMS43MiwwLjc3My0yLjk1OCwxLjE1NmwwLDBjLTMuNzM1LDEuMTU0LTkuNywyLjIwNS0xNy4yODEsMi40NDljLTAuMjI1LDAuMDA3LTAuNDQ3LDAuMDE1LTAuNjc1LDAuMDIxDQoJYy0wLjI0NSwwLjAwNi0wLjQ5NCwwLjAxLTAuNzQzLDAuMDE1QzI4LjI4MywzNi45OTEsMjcuNjUsMzcsMjcsMzdjLTAuODY2LDAtMS43MDYtMC4wMTMtMi41MzQtMC4wMzINCgljLTAuMzA0LTAuMDA3LTAuNjA0LTAuMDE3LTAuOTA0LTAuMDI3Yy0wLjM2Ny0wLjAxMS0wLjcyNS0wLjAyNy0xLjA4My0wLjA0MmMtNy4wMTYtMC4zMS0xMi41NTMtMS4zMTEtMTYuMDktMi40MDRsMCwwDQoJYy0yLjc1LTAuODUtNC4yODktMS43NTQtNC4zNzgtMi40MzNDMi4xMjIsMzEuNjg2LDMuMTMzLDMwLjc0NSw2Ljg0NCwyOS44MzV6IE0yLDM4Ljk5NmwwLTQuMTQxYzAuNzk5LDAuNTAzLDEuODExLDAuOTYyLDMsMS4zNzYNCgl2NC43NjlsLTAuNTcxLTAuMjIyTDQuNDE3LDQwLjc5QzIuODQ3LDQwLjEzOSwyLjAwMiwzOS41LDIsMzguOTk2eiBNNSw0OS45OTZsMC00LjE0MWMwLjc5OSwwLjUwMywxLjgxMSwwLjk2MiwzLDEuMzc2djQuNzg4DQoJQzYuMDU1LDUxLjI5LDUuMDAyLDUwLjU1OSw1LDQ5Ljk5NnogTTUyLDUyLjAxOXYtNC43ODdjMS4xODktMC40MTQsMi4yMDEtMC44NzMsMy0xLjM3NnY0LjEzOA0KCUM1NC45OTksNTAuNTU3LDUzLjk0NSw1MS4yODksNTIsNTIuMDE5eiBNNTQuOTg3LDQzLjA3N2MtMC4xMDksMC42NzctMS42NDUsMS41NzUtNC4zNzYsMi40MTlsMCwwDQoJYy0zLjUzOCwxLjA5My05LjA3NCwyLjA5NC0xNi4wOSwyLjQwNGMtMC4zNTksMC4wMTUtMC43MTcsMC4wMy0xLjA4MywwLjA0MmMtMC4yOTksMC4wMS0wLjU5OSwwLjAxOS0wLjkwNCwwLjAyNw0KCUMzMS43MDYsNDcuOTg3LDMwLjg2Niw0OCwzMCw0OGMtMC44NjYsMC0xLjcwNy0wLjAxMy0yLjUzNi0wLjAzMmMtMC4zMDEtMC4wMDctMC41OTgtMC4wMTctMC44OTUtMC4wMjcNCgljLTAuMzY5LTAuMDEyLTAuNzI5LTAuMDI3LTEuMDktMC4wNDJjLTcuMDE2LTAuMzEtMTIuNTUyLTEuMzExLTE2LjA5LTIuNDA0bDAsMGMtMi42NDUtMC44MTctNC4xNzMtMS42ODUtNC4zNjUtMi4zNTUNCgljMC4yOTgsMC4xMDQsMC42MDcsMC4yMDUsMC45MjQsMC4zMDRjMC4wMzIsMC4wMSwwLjA2NCwwLjAyLDAuMDk2LDAuMDI5YzAuMjcsMC4wODMsMC41NDYsMC4xNjMsMC44MjksMC4yNDENCgljMC4xMDcsMC4wMywwLjIxNSwwLjA2LDAuMzI0LDAuMDg5YzAuMTYsMC4wNDMsMC4zMjQsMC4wODQsMC40ODgsMC4xMjZjMy42NDIsMC45MzMsOC4yOTEsMS41OTQsMTMuMzEsMS44OTENCgljMC4wMDIsMCwwLjAwMywwLjAwMSwwLjAwNSwwLjAwMWMwLjAwMSwwLDAuMDAyLTAuMDAxLDAuMDAzLTAuMDAxYzEuNTUsMC4wOTIsMy4xMzMsMC4xNDksNC43MzMsMC4xNjgNCglDMjYuMTYyLDQ1Ljk5NiwyNi41ODUsNDYsMjcsNDZjMC41NTEsMCwxLjExNS0wLjAwNywxLjY4Ni0wLjAxN2MxLjQ1OS0wLjAyNCwyLjg5OS0wLjA3OCw0LjMwNy0wLjE2Mg0KCWMwLjAwMywwLDAuMDA1LDAuMDAyLDAuMDA4LDAuMDAyYzAuMDA1LDAsMC4wMDgtMC4wMDMsMC4wMTMtMC4wMDNjMS43MTUtMC4xMDMsMy4zNzUtMC4yNSw0Ljk3LTAuNDMzDQoJYzAuMDA2LDAsMC4wMTEsMC4wMDMsMC4wMTcsMC4wMDNjMC4wMjIsMCwwLjA0LTAuMDExLDAuMDYyLTAuMDEzYzEuNzc2LTAuMjA1LDMuNDYtMC40NTcsNS4wMjMtMC43NQ0KCWMwLjMyMi0wLjA1OSwwLjYzOS0wLjEyLDAuOTUzLTAuMTgzYzAuMDctMC4wMTQsMC4xNC0wLjAyOCwwLjIxLTAuMDQzYzIuOTUzLTAuNjA2LDUuNTA5LTEuMzkxLDcuMjYzLTIuMzY0DQoJYzAuMDk2LTAuMDUyLDAuMTg2LTAuMTA2LDAuMjc3LTAuMTU5YzAuMTExLTAuMDY2LDAuMjE3LTAuMTMzLDAuMzItMC4yMDFjMC4wOTYtMC4wNjIsMC4yMDctMC4xMjIsMC4yOTUtMC4xODUNCglDNTQuMzc4LDQyLjE5Niw1NC45MjIsNDIuODI2LDU0Ljk4Nyw0My4wNzd6IE01NSwzMC4wMTl2LTQuNzg3YzEuMTg5LTAuNDE0LDIuMjAxLTAuODczLDMtMS4zNzZ2NC4xMzgNCglDNTcuOTk5LDI4LjU1Nyw1Ni45NDUsMjkuMjg5LDU1LDMwLjAxOXoiLz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjwvc3ZnPg0K'
    
    # Create different animations
    animations = {
        "fade_in": "fade_in",
        "scale_up": "scale_up", 
        "rotate": "rotate",
        "bounce": "bounce",
    }
    
  
    
    results = []
    
    for name, anim_type in animations.items():
        output_file = f"sample_{name}.json"
        
        try:
            result_path = svg_to_animated_lottie(
                base64_svg=svg_base64,
                output_path=output_file,
                animation_type=anim_type,
                fps=30,
                size=(200, 200)
            )
            results.append(f"Created: {result_path}")
        except Exception as e:
            results.append(f"Failed to create {name}: {str(e)}")
    
    return results


if __name__ == "__main__":
    print("SVG to Animated Lottie Converter")
    print("================================")
    
    # Create sample animations
    results = create_sample_animated_lottie()
    
    print("\nSample animations created:")
    for result in results:
        print(f"  - {result}")
    
    print("\nTo use this function in your code:")
    print("""
    from svg_to_lottie import svg_to_animated_lottie
    
    # Convert your base64 SVG to animated Lottie
    lottie_path = svg_to_animated_lottie(
        base64_svg="your_base64_svg_string",
        output_path="output.json",
        animation_type="bounce",  # or "fade_in", "scale_up", "rotate", "complex"
        fps=30,
        size=(512, 512)
    )
    """)
