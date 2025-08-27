#!/usr/bin/env python3

from abc import ABC, abstractmethod
from lottie import Point
from typing import Dict, Type, Tuple


class BaseAnimation(ABC):
    def __init__(self, duration: int = 60):
        self.duration = duration
    
    @abstractmethod
    def apply(self, transform, animation_size: Tuple[int, int]) -> None:
        pass


class FadeInAnimation(BaseAnimation):
    
    def apply(self, transform, animation_size: Tuple[int, int]) -> None:
        transform.opacity.add_keyframe(0, 0)
        transform.opacity.add_keyframe(30, 100)
        
        transform.scale.add_keyframe(0, Point(100, 100))
        transform.scale.add_keyframe(30, Point(100, 100))
        transform.scale.add_keyframe(self.duration, Point(100, 100))


class ScaleUpAnimation(BaseAnimation):
    
    def apply(self, transform, animation_size: Tuple[int, int]) -> None:
        transform.scale.add_keyframe(0, Point(50, 50))
        transform.scale.add_keyframe(30, Point(100, 100))


class BounceAnimation(BaseAnimation):
    
    def apply(self, transform, animation_size: Tuple[int, int]) -> None:
        keyframes = [
            (0, Point(90, 90)),
            (15, Point(100, 100)),
            (30, Point(90, 90)),
            (45, Point(100, 100)),
            (60, Point(90, 90)),
            (75, Point(100, 100))
        ]
        
        for frame, scale in keyframes:
            transform.scale.add_keyframe(frame, scale)
        
        transform.scale.add_keyframe(self.duration, Point(100, 100))


class BottomToCenterAnimation(BaseAnimation):
    
    def apply(self, transform, animation_size: Tuple[int, int]) -> None:
        width, height = animation_size
        
        start_position = Point(0, height * 2)
        end_position = Point(0, 0)
        
        transform.position.add_keyframe(0, start_position)
        transform.position.add_keyframe(30, end_position)
        
        # Maintain scale throughout
        transform.scale.add_keyframe(0, Point(100, 100))
        transform.scale.add_keyframe(30, Point(100, 100))


class AnimationFactory:
    
    _animations: Dict[str, Type[BaseAnimation]] = {
        "fade_in": FadeInAnimation,
        "scale_up": ScaleUpAnimation,
        "bounce": BounceAnimation,
        "bottom_to_center": BottomToCenterAnimation,
    }
    
    @classmethod
    def create_animation(cls, animation_type: str, duration: int = 60) -> BaseAnimation:
        if animation_type not in cls._animations:
            available = ", ".join(cls._animations.keys())
            raise ValueError(f"Unknown animation type '{animation_type}'. Available: {available}")
        
        return cls._animations[animation_type](duration)
    
    @classmethod
    def get_available_types(cls) -> list:
        return list(cls._animations.keys())
