# SVG to Animated Lottie Converter

A Python library that converts base64-encoded SVG images into animated Lottie files using the powerful `python-lottie` framework. Now available as both a standalone library and a Flask web API!

## 🚀 Deployment Options

### 1. Standalone Library

Use as a Python library in your local projects.

### 2. Flask Web API

Deploy as a web API on platforms like PythonAnywhere, Heroku, or any Python hosting service.

## Features

- Convert base64-encoded SVG to animated Lottie JSON files
- Multiple built-in animation types (fade in, scale up, rotation, bounce)
- Complex custom animations with multiple effects
- Support for custom frame rates and output dimensions
- Handles both plain base64 strings and data URLs
- Easy-to-use Python API
- **🌐 Flask web API with CORS support**
- **☁️ Ready for deployment on PythonAnywhere**
- **🔧 Local development server included**

## PythonAnywhere Deployment

For deploying on PythonAnywhere, see [PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md) for detailed instructions.

### Quick PythonAnywhere Setup

1. **Upload your code** to PythonAnywhere
2. **Install dependencies**: `pip3.11 install --user -r requirements.txt`
3. **Configure web app** with the provided `wsgi.py` file
4. **Your API will be live** at `https://yourusername.pythonanywhere.com`

### API Usage

```bash
curl -X POST "https://yourusername.pythonanywhere.com/convert" \
  -H "Content-Type: application/json" \
  -d '{"svg": "your_base64_svg", "animation_type": "bounce"}'
```

## Local Development

### Standalone Library Installation

```bash
pip install -r requirements.txt
```

Or install dependencies manually:

```bash
pip install lottie[all] cairosvg pillow
```

## Quick Start

```python
from svg_to_lottie import svg_to_animated_lottie
import base64

# Read and encode your SVG
with open('your_image.svg', 'r') as file:
    svg_content = file.read()
svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

# Convert to animated Lottie
lottie_path = svg_to_animated_lottie(
    base64_svg=svg_base64,
    output_path="animated_output.json",
    animation_type="bounce",
    fps=30,
    size=(512, 512)
)

print(f"Animated Lottie created: {lottie_path}")
```

## Animation Types

### Basic Animations

1. **fade_in** - Elements fade from transparent to opaque
2. **scale_up** - Elements scale from 0% to 100% size
3. **rotate** - Elements rotate 360 degrees
4. **bounce** - Elements bounce with scaling effects

### Complex Animations

Use `animation_type="complex"` with custom effects:

```python
custom_effects = {
    "duration": 120,  # 4 seconds at 30fps
    "fade_in": {"start": 0, "end": 30},
    "scale_pulse": {"start": 30, "end": 90},
    "rotation": {"start": 60, "end": 120, "degrees": 720}
}

svg_to_animated_lottie(
    base64_svg=your_base64_svg,
    output_path="complex_animation.json",
    animation_type="complex",
    custom_effects=custom_effects
)
```

## API Reference

### `svg_to_animated_lottie(base64_svg, output_path, animation_type="fade_in", custom_effects=None, fps=30, size=None)`

**Parameters:**

- `base64_svg` (str): Base64-encoded SVG string or data URL
- `output_path` (str): Path where the Lottie JSON file will be saved
- `animation_type` (str): Animation type - "fade_in", "scale_up", "rotate", "bounce", or "complex"
- `custom_effects` (dict, optional): Custom animation effects for complex animations
- `fps` (int): Frame rate for the animation (default: 30)
- `size` (tuple, optional): Output dimensions as (width, height)

**Returns:**

- `str`: Path to the created Lottie file

## Running the Demo

```bash
python demo.py
```

This will create several example animations showing different animation types.

## Using the Generated Lottie Files

### Web Usage

```html
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
<lottie-player
  src="your_animation.json"
  background="transparent"
  speed="1"
  loop
  autoplay
></lottie-player>
```

### Preview Online

Upload your generated JSON files to [LottieFiles Preview](https://lottiefiles.com/preview) to see them in action.

### Convert to Other Formats

Use the included `lottie_convert.py` script:

```bash
lottie_convert.py your_animation.json output.gif
lottie_convert.py your_animation.json output.mp4
```

## File Structure

```
svg-to-animated-lottie/
├── svg_to_lottie.py      # Main converter module
├── demo.py               # Demo script with examples
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Dependencies

- **lottie[all]** - Core Lottie manipulation library
- **cairosvg** - SVG processing and rendering
- **pillow** - Image processing support

## Error Handling

The library includes comprehensive error handling for:

- Invalid base64 encoding
- Malformed SVG content
- File I/O errors
- Missing dependencies

## Examples

### Simple Fade In Animation

```python
svg_to_animated_lottie(
    base64_svg=your_svg_base64,
    output_path="fade_in.json",
    animation_type="fade_in"
)
```

### Bouncing Logo Animation

```python
svg_to_animated_lottie(
    base64_svg=logo_base64,
    output_path="bouncing_logo.json",
    animation_type="bounce",
    fps=60,
    size=(300, 300)
)
```

### Custom Multi-Effect Animation

```python
effects = {
    "duration": 180,  # 6 seconds
    "fade_in": {"start": 0, "end": 30},
    "scale_pulse": {"start": 30, "end": 120},
    "rotation": {"start": 90, "end": 180, "degrees": 360}
}

svg_to_animated_lottie(
    base64_svg=your_svg_base64,
    output_path="multi_effect.json",
    animation_type="complex",
    custom_effects=effects
)
```

## License

This project is open source. The `python-lottie` dependency is licensed under AGPLv3+.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this library.

## Credits

Built using the excellent [python-lottie](https://gitlab.com/mattbas/python-lottie/) framework by Mattia Basaglia.
