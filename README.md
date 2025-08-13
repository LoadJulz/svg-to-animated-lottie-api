# SVG to Animated Lottie Converter

A Flask-based REST API that converts base64-encoded SVG images into animated Lottie JSON files with various animation effects.

## Features

- Convert SVG to animated Lottie files
- Multiple animation types: fade in, scale up, bounce, and bottom to center
- Configurable frame rate
- REST API with CORS support
- Preserves original SVG dimensions
- Base64 encoding support

## Testing results

If you want to test the output, please avoid using the official Lottie viewer, as it may display the generated Lottie files incorrectly. Instead, use a website like [LottieLab Preview](https://www.lottielab.com/preview) or test the animations directly in your frontend application.

## Animation Types

### Available Animations

1. **fade_in** - Elements fade in from transparent to opaque
2. **scale_up** - Elements scale from 50% to 100% size
3. **bounce** - Elements bounce with a rhythmic scaling effect
4. **bottom_to_center** - Elements slide in from bottom to center position

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

### Dependencies

- Flask
- flask-cors
- lottie[all]
- Additional standard Python libraries (base64, json, tempfile, etc.)

## API Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5001`

### API Endpoints

#### Health Check

```
GET /health
```

Returns server status and version information.

#### Convert SVG to Lottie

```
POST /convert
```

**Request Body:**

```json
{
  "base64_svg": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iIzMzNzNkYyIvPgo8L3N2Zz4=",
  "animation_type": "bounce",
  "fps": 30,
  "duration": 60
}
```

**Parameters:**

- `base64_svg` (required): Base64-encoded SVG content
- `animation_type` (optional): Animation type - "fade_in", "scale_up", "bounce", or "bottom_to_center" (default: "fade_in")
- `fps` (optional): Frame rate for the animation (default: 30)
- `duration` (optional): Animation duration in frames (default: 60)

**Response:**

```json
{
  // Lottie JSON
}
```

#### Get Available Animation Types

```
GET /animation-types
```

Returns a list of available animation types.

### Example Usage

#### Using cURL

```bash
curl -X POST http://localhost:5001/convert \
  -H "Content-Type: application/json" \
  -d '{
    "base64_svg": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iIzMzNzNkYyIvPgo8L3N2Zz4=",
    "animation_type": "bottom_to_center",
    "fps": 30,
    "duration": 60
  }'
```

## Demo

Run the demo script to see examples of all animation types:

```bash
python demo.py
```

This will create sample Lottie files for each animation type using a demo SVG.

## How It Works

1. **SVG Processing**: The converter decodes base64 SVG input and extracts original dimensions
2. **Lottie Import**: Uses the python-lottie library to import the SVG into a Lottie animation object
3. **Animation Application**: Applies keyframe animations based on the selected animation type
4. **Export**: Exports the final animated Lottie JSON with proper metadata

### Animation Details

- **Duration**: All animations are 2 seconds (60 frames at 30fps)
- **Keyframes**: Each animation type uses specific keyframe patterns for smooth motion
- **Dimensions**: Original SVG dimensions are preserved in the output
- **Quality**: Maintains vector quality through the conversion process

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please use the GitHub issue tracker.
