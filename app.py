#!/usr/bin/env python3
"""
Flask API for SVG to Animated Lottie Converter

This Flask application provides REST API endpoints to convert base64-encoded SVG images 
to animated Lottie JSON files.
"""

import json
import tempfile
import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from svg_to_lottie import svg_to_animated_lottie

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "SVG to Animated Lottie Converter API",
        "version": "1.0.0"
    })


@app.route('/convert', methods=['POST'])
def convert_svg_to_lottie():
    """
    Convert base64-encoded SVG to animated Lottie JSON.
    
    Expected JSON payload:
    {
        "base64_svg": "data:image/svg+xml;base64,..." or just the base64 string,
        "animation_type": "bounce" | "shake",
        "custom_effects": {...},  // optional, for complex animations
        "fps": 30,  // optional, default 30
        "size": [width, height]  // optional, default derived from SVG
    }
    
    Returns:
        JSON response with Lottie animation data or error message
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "message": "Request body must contain valid JSON"
            }), 400
        
        # Validate required fields
        raw_base64 = data.get('base64_svg')
        if not raw_base64:
            return jsonify({
                "error": "Missing required field",
                "message": "base64_svg field is required"
            }), 400
        
        svg_base64 = f"data:image/svg+xml;base64,{raw_base64}"  # Data URL format
       
       
        
        # Extract optional parameters with defaults
        animation_type = data.get('animation_type', 'rotate')
        custom_effects = data.get('custom_effects', None)
        fps = data.get('fps', 30)
        size = data.get('size', None)
        
        # Validate animation type
        valid_animations = ['rotate', 'shake']
        if animation_type not in valid_animations:
            return jsonify({
                "error": "Invalid animation type",
                "message": f"animation_type must be one of: {', '.join(valid_animations)}",
                "provided": animation_type
            }), 400
        
        # Validate size if provided
        if size is not None:
            if not isinstance(size, list) or len(size) != 2 or not all(isinstance(x, int) for x in size):
                return jsonify({
                    "error": "Invalid size format",
                    "message": "size must be an array of two integers [width, height]"
                }), 400
            size = tuple(size)
        
        # Validate fps
        if not isinstance(fps, int) or fps <= 0:
            return jsonify({
                "error": "Invalid fps value",
                "message": "fps must be a positive integer"
            }), 400
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_output_path = temp_file.name
        
        try:
            # Convert SVG to animated Lottie
            result_path = svg_to_animated_lottie(
                base64_svg=svg_base64,
                output_path=temp_output_path,
                animation_type=animation_type,
                custom_effects=custom_effects,
                fps=fps,
                size=size
            )
            
            # Read the generated Lottie JSON
            with open(result_path, 'r') as lottie_file:
                lottie_data = json.load(lottie_file)
            
            # Return the Lottie JSON data
            return jsonify({
                "success": True,
                "message": "SVG successfully converted to Lottie animation",
                "animation_type": animation_type,
                "fps": fps,
                "size": size,
                "lottie_data": lottie_data
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
    
    except ValueError as e:
        return jsonify({
            "error": "Invalid input data",
            "message": str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/animation-types', methods=['GET'])
def get_animation_types():
    """
    Get available animation types and their descriptions.
    
    Returns:
        JSON response with available animation types
    """
    animation_types = {
        "rotate": {
            "description": "Elements rotate 360 degrees",
            "duration": "2 seconds (default)"
        },
    }
    
    return jsonify({
        "animation_types": animation_types,
        "default_fps": 30,
        "default_animation_type": "fade_in"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "GET /health - Health check",
            "POST /convert - Convert SVG to Lottie",
            "GET /animation-types - Get available animation types",
            "GET /convert/demo - Demo conversion with sample SVG"
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method is not supported for this endpoint"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    print("Starting SVG to Animated Lottie Converter API...")
    print("Available endpoints:")
    print("  GET  /health           - Health check")
    print("  POST /convert          - Convert SVG to Lottie")
    print("  GET  /animation-types  - Get available animation types")
    print("  GET  /convert/demo     - Demo conversion")
    print()
    print("Example usage:")
    print("""
    curl -X POST http://localhost:5000/convert \\
      -H "Content-Type: application/json" \\
      -d '{
        "base64_svg": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iIzMzNzNkYyIvPgo8L3N2Zz4=",
        "animation_type": "bounce",
        "fps": 30,
        "size": [400, 400]
      }'
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
