#!/usr/bin/env python3

import base64
import tempfile
import os
import json
import re
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

from animations import AnimationFactory, BaseAnimation


# Constants
DEFAULT_DIMENSIONS = (512, 512)
DEFAULT_FPS = 30
DEFAULT_DURATION = 60
SVG_DATA_URL_PREFIX = 'data:image/svg+xml;base64,'


class SVGParsingError(Exception):
    """Raised when SVG parsing fails."""
    pass


class LottieConversionError(Exception):
    """Raised when Lottie conversion fails."""
    pass


def decode_base64_svg(base64_svg: str) -> str:
    """
    Decode base64 encoded SVG string.
    
    Args:
        base64_svg: Base64 encoded SVG string, optionally with data URL prefix
        
    Returns:
        Decoded SVG content as string
        
    Raises:
        ValueError: If decoding fails
    """
    try:
        # Remove data URL prefix if present
        if base64_svg.startswith(SVG_DATA_URL_PREFIX):
            base64_svg = base64_svg.replace(SVG_DATA_URL_PREFIX, '')
        
        svg_bytes = base64.b64decode(base64_svg)
        return svg_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decode base64 SVG: {str(e)}") from e


def extract_svg_dimensions(svg_content: str) -> Tuple[int, int]:
    """
    Extract dimensions from SVG content.
    
    Args:
        svg_content: SVG content as string
        
    Returns:
        Tuple of (width, height) as integers
    """
    
    # Try to extract from viewBox
    viewbox_dims = None
    viewbox_match = re.search(r'viewBox\s*=\s*["\']?([^"\']*)["\']?', svg_content, re.IGNORECASE)
    if viewbox_match:
        viewbox_values = viewbox_match.group(1).split()
        if len(viewbox_values) >= 4:
            try:
                viewbox_dims = (int(float(viewbox_values[2])), int(float(viewbox_values[3])))
            except (ValueError, IndexError):
                pass

    if viewbox_dims:
        return viewbox_dims
    

    width_match = re.search(r'width\s*=\s*["\']?(\d+(?:\.\d+)?)["\']?', svg_content, re.IGNORECASE)
    height_match = re.search(r'height\s*=\s*["\']?(\d+(?:\.\d+)?)["\']?', svg_content, re.IGNORECASE)
    
    width_height_dims = None
    if width_match and height_match:
        width_height_dims = (int(float(width_match.group(1))), int(float(height_match.group(1))))
    
        return width_height_dims
    
    
    return DEFAULT_DIMENSIONS


def apply_animation_to_layers(lottie_animation: objects.Animation, animation: BaseAnimation) -> None:
    """
    Apply animation to all layers in the Lottie animation.
    
    Args:
        lottie_animation: Lottie animation object
        animation: Animation instance to apply
    """
    if not lottie_animation.layers:
        return
    
    animation_size = (
        lottie_animation.width or DEFAULT_DIMENSIONS[0],
        lottie_animation.height or DEFAULT_DIMENSIONS[1]
    )
    
    for layer in lottie_animation.layers:
        if hasattr(layer, 'transform'):
            animation.apply(layer.transform, animation_size)
        # Extend layer's out-point to match the animation duration
        if hasattr(layer, 'out_point'):
            layer.out_point = animation.duration


def create_lottie_metadata(width: int, height: int, fps: int, duration: int) -> Dict[str, Any]:
    """
    Create Lottie metadata dictionary.
    
    Args:
        width: Animation width
        height: Animation height
        fps: Frames per second
        duration: Animation duration in frames
        
    Returns:
        Metadata dictionary
    """
    return {
        "w": width,
        "h": height,
        "ip": 0,
        "op": duration,
        "fr": fps,
        "meta": {
            "g": "SVG to Lottie Converter",
            "a": "",
            "k": "",
            "d": "",
            "tc": ""
        }
    }

def svg_to_animated_lottie(
    base64_svg: str,
    animation_type: str = "fade_in",
    fps: int = DEFAULT_FPS,
    duration: int = DEFAULT_DURATION
) -> Dict[str, Any]:
    """
    Convert base64 encoded SVG to animated Lottie JSON.
    
    Args:
        base64_svg: Base64 encoded SVG string
        animation_type: Type of animation to apply
        fps: Frames per second for the animation
        duration: Animation duration in frames
        
    Returns:
        Lottie animation as dictionary
        
    Raises:
        ValueError: If input parameters are invalid
        SVGParsingError: If SVG parsing fails
        LottieConversionError: If Lottie conversion fails
    """
    # Validate inputs
    if not base64_svg:
        raise ValueError("base64_svg cannot be empty")
    
    if fps <= 0:
        raise ValueError("fps must be positive")
    
    if duration <= 0:
        raise ValueError("duration must be positive")
    
    try:
        # Decode SVG
        svg_content = decode_base64_svg(base64_svg)
        
        # Extract dimensions
        svg_width, svg_height = extract_svg_dimensions(svg_content)
        print(f"Extracted SVG dimensions: {svg_width}x{svg_height}")
        
        # Create temporary SVG file
        temp_svg_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
                temp_svg.write(svg_content)
                temp_svg_path = temp_svg.name
            
            # Convert SVG to Lottie
            lottie_animation = import_svg(temp_svg_path)
            
            # Configure animation properties
            lottie_animation.frame_rate = fps
            lottie_animation.width = svg_width
            lottie_animation.height = svg_height
            lottie_animation.out_point = duration
            
            # Apply animation
            animation = AnimationFactory.create_animation(animation_type, duration)
            apply_animation_to_layers(lottie_animation, animation)
            
            # Convert to dictionary and add metadata
            lottie_dict = lottie_animation.to_dict()
            metadata = create_lottie_metadata(svg_width, svg_height, fps, duration)
            lottie_dict.update(metadata)
            
            return lottie_dict
            
        finally:
            # Clean up temporary file
            if temp_svg_path and os.path.exists(temp_svg_path):
                os.unlink(temp_svg_path)
                
    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        raise LottieConversionError(f"Failed to convert SVG to Lottie: {str(e)}") from e
