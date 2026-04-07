import React, { useRef } from 'react';
import { Animated, Pressable } from 'react-native';

export default function ScalePressable({
  children,
  onPress,
  style,
  disabled,
  scaleTo = 0.97,
  ...rest
}) {
  const scale = useRef(new Animated.Value(1)).current;

  const animateTo = (toValue) => {
    Animated.spring(scale, {
      toValue,
      useNativeDriver: true,
      speed: 25,
      bounciness: 4,
    }).start();
  };

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <Pressable
        style={style}
        disabled={disabled}
        onPress={onPress}
        onPressIn={() => animateTo(scaleTo)}
        onPressOut={() => animateTo(1)}
        android_ripple={{ color: 'rgba(148,163,184,0.18)' }}
        unstable_pressDelay={30}
        hitSlop={4}
        accessibilityRole="button"
        {...rest}
      >
        {({ pressed }) => (
          <Animated.View style={{ opacity: pressed ? 0.86 : 1 }}>
            {children}
          </Animated.View>
        )}
      </Pressable>
    </Animated.View>
  );
}
