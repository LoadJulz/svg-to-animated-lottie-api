#!/usr/bin/env python3

import base64
import json
from svg_to_lottie import svg_to_animated_lottie, SVGParsingError, LottieConversionError
from animations import AnimationFactory

def create_sample_svg(): 
    base64_svg = '[PUT YOUR BASE64 ENCODED SVG HERE]'
    return base64_svg

def demo_animations():
    """Demonstrate different animation types."""
    print("🎬 SVG to Animated Lottie Demo")
    print("=" * 40)
    
    # Create sample SVG
    base64_svg = create_sample_svg()
    print("✅ Created sample SVG")
    
    # Get available animation types
    available_types = AnimationFactory.get_available_types()
    print(f"📋 Available animations: {', '.join(available_types)}")
    print()
    
    # Test each animation type
    for animation_type in available_types:
        print(f"🎭 Testing '{animation_type}' animation...")
        
        try:
            # Convert with different parameters
            lottie_data = svg_to_animated_lottie(
                base64_svg=base64_svg,
                animation_type=animation_type,
                fps=30,
                duration=90  # 3 seconds at 30fps
            )
            
            # Verify the result
            if isinstance(lottie_data, dict):
                print(f"   ✅ Success! Generated Lottie with {len(str(lottie_data))} characters")
                print(f"   📐 Dimensions: {lottie_data.get('w', 'N/A')}x{lottie_data.get('h', 'N/A')}")
                print(f"   🎬 FPS: {lottie_data.get('fr', 'N/A')}, Duration: {lottie_data.get('op', 'N/A')} frames")
                
                # Save to file for inspection
                filename = f"output_{animation_type}.json"
                with open(filename, 'w') as f:
                    json.dump(lottie_data, f, indent=2)
                print(f"   💾 Saved to: {filename}")
            else:
                print("   ❌ Failed: Unexpected return type")
                
        except (ValueError, SVGParsingError, LottieConversionError) as e:
            print(f"   ❌ Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        print()

def demo_error_handling():
    """Demonstrate error handling."""
    print("🚨 Error Handling Demo")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Empty base64",
            "base64_svg": "",
            "animation_type": "fade_in"
        },
        {
            "name": "Invalid animation type",
            "base64_svg": create_sample_svg(),
            "animation_type": "invalid_animation"
        },
        {
            "name": "Invalid FPS",
            "base64_svg": create_sample_svg(),
            "animation_type": "fade_in",
            "fps": -1
        },
        {
            "name": "Invalid duration",
            "base64_svg": create_sample_svg(),
            "animation_type": "fade_in",
            "fps": 30,
            "duration": 0
        }
    ]
    
    for test_case in test_cases:
        print(f"🧪 Testing: {test_case['name']}")
        try:
            result = svg_to_animated_lottie(**{k: v for k, v in test_case.items() if k != 'name'})
            print(f"   ❌ Expected error but got success!")
        except Exception as e:
            print(f"   ✅ Caught expected error: {type(e).__name__}: {e}")
        print()

if __name__ == "__main__":
    try:
        demo_animations()
        demo_error_handling()
        print("🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
