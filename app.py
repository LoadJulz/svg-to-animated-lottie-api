#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from svg_to_lottie import svg_to_animated_lottie, SVGParsingError, LottieConversionError
from animations import AnimationFactory


# Configuration
class Config:
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Register routes
    register_routes(app)
    register_error_handlers(app)
    
    return app


def register_routes(app: Flask) -> None:
    """Register application routes."""
    
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
        """Convert SVG to animated Lottie."""
        try:
            # Validate request
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "No JSON data provided",
                    "message": "Request body must contain valid JSON"
                }), 400
            
            # Extract and validate parameters
            base64_svg = data.get('base64_svg')
            if not base64_svg:
                return jsonify({
                    "error": "Missing required field",
                    "message": "base64_svg field is required"
                }), 400
            
            animation_type = data.get('animation_type', 'fade_in')
            fps = data.get('fps', 30)
            duration = data.get('duration', 60)
            
            # Validate animation type
            available_types = AnimationFactory.get_available_types()
            if animation_type not in available_types:
                return jsonify({
                    "error": "Invalid animation type",
                    "message": f"animation_type must be one of: {', '.join(available_types)}",
                    "provided": animation_type
                }), 400
            
            # Validate numeric parameters
            if not isinstance(fps, int) or fps <= 0:
                return jsonify({
                    "error": "Invalid fps value",
                    "message": "fps must be a positive integer"
                }), 400
            
            if not isinstance(duration, int) or duration <= 0:
                return jsonify({
                    "error": "Invalid duration value",
                    "message": "duration must be a positive integer"
                }), 400
            
            # Convert SVG to Lottie
            lottie_data = svg_to_animated_lottie(
                base64_svg=base64_svg,
                animation_type=animation_type,
                fps=fps,
                duration=duration
            )
            
            return jsonify(lottie_data)
        
        except (ValueError, SVGParsingError) as e:
            return jsonify({
                "error": "Invalid input data",
                "message": str(e)
            }), 400
        
        except LottieConversionError as e:
            return jsonify({
                "error": "Conversion failed",
                "message": str(e)
            }), 422
        
        except Exception as e:
            app.logger.error(f"Unexpected error in convert endpoint: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }), 500

    @app.route('/animation-types', methods=['GET'])
    def get_animation_types():
        """Get available animation types."""
        return jsonify({
            "available_types": AnimationFactory.get_available_types(),
            "default": "fade_in"
        })


def register_error_handlers(app: Flask) -> None:
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": [
                "GET /health - Health check",
                "POST /convert - Convert SVG to Lottie",
                "GET /animation-types - Get available animation types"
            ]
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed",
            "message": "The HTTP method is not supported for this endpoint"
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500


def print_startup_info():
    """Print startup information."""
    print("Starting SVG to Animated Lottie Converter API...")
    print("Available endpoints:")
    print("  GET  /health           - Health check")
    print("  POST /convert          - Convert SVG to Lottie")
    print("  GET  /animation-types  - Get available animation types")
    print()
    print("Example usage:")
    print("""
    curl -X POST http://localhost:5001/convert \\
      -H "Content-Type: application/json" \\
      -d '{
        "base64_svg": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iIzMzNzNkYyIvPgo8L3N2Zz4=",
        "animation_type": "bottom_to_center",
        "fps": 30,
        "duration": 60
      }'
    """)
    
app = create_app()

if __name__ == '__main__':
    print_startup_info()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
