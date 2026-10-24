import * as THREE from 'three';
import { VRM } from '@pixiv/three-vrm';

/**
 * Eye tracking with 0.5s lag for realism.
 * Also handles natural random-interval blinking.
 */
export class EyeController {
  private targetX = 0;
  private targetY = 0;
  public currentX = 0;
  public currentY = 0;
  private lagSpeed = 12.0; // Faster for responsive eyes
  
  private blinkTimer = 0;
  private nextBlinkAt = 3;
  private blinkValue = 0;
  private blinkDecay = 10; // how fast blink closes/opens
  
  private blinkOverrideLeft?: number;
  private blinkOverrideRight?: number;
  private baseEyelids = { left: 0, right: 0 };
  private gazeOffset = { x: 0, y: 0 };

  setLookAt(yaw: number, pitch: number) {
    this.targetX = yaw + this.gazeOffset.x;
    this.targetY = pitch + this.gazeOffset.y;
  }

  setGazeOffset(x: number, y: number) {
    this.gazeOffset = { x, y };
  }

  setBaseEyelids(left: number, right: number) {
    this.baseEyelids = {
      left: Math.max(0, Math.min(1, left)),
      right: Math.max(0, Math.min(1, right)),
    };
  }

  forceBlink() {
    this.blinkValue = 1;
  }

  update(vrm: VRM, delta: number) {
    if (!vrm) return;

    // --- Eye tracking with smoother, faster response ---
    const t = Math.min(1, delta * this.lagSpeed);
    this.currentX += (this.targetX - this.currentX) * t;
    this.currentY += (this.targetY - this.currentY) * t;

    if (vrm.lookAt) {
      // Disable the built-in auto-lookAt system because it fights with manual bone rotations
      vrm.lookAt.autoUpdate = false;
    }

    // --- Natural blinking (paused if eyes are held completely wide in surprise) ---
    this.blinkTimer += delta;
    if (this.blinkTimer >= this.nextBlinkAt) {
      this.blinkValue = 1;
      this.blinkTimer = 0;
      // Random interval: 2.5 - 5.5 seconds, with occasional quick double-blink
      this.nextBlinkAt = 2.5 + Math.random() * 3.0;
    }

    // Decay blink
    if (this.blinkValue > 0) {
      this.blinkValue = Math.max(0, this.blinkValue - delta * this.blinkDecay);
    }

    if (vrm.expressionManager) {
      let finalLeft: number;
      let finalRight: number;

      if (this.blinkOverrideLeft !== undefined && this.blinkOverrideRight !== undefined) {
        finalLeft = this.blinkOverrideLeft;
        finalRight = this.blinkOverrideRight;
      } else {
        finalLeft = Math.min(1.0, this.baseEyelids.left + this.blinkValue);
        finalRight = Math.min(1.0, this.baseEyelids.right + this.blinkValue);
      }

      this.applyEyelidExpressions(vrm, finalLeft, finalRight);
    }
  }

  private applyEyelidExpressions(vrm: VRM, left: number, right: number): void {
    if (!vrm.expressionManager) return;

    const setExpr = (name: string, val: number) => {
      if (!vrm.expressionManager) return;
      if (vrm.expressionManager.getExpression(name)) {
        vrm.expressionManager.setValue(name, val);
        return;
      }
      const lower = name.toLowerCase();
      for (const expr of vrm.expressionManager.expressions) {
        if (expr.expressionName.toLowerCase() === lower) {
          vrm.expressionManager.setValue(expr.expressionName, val);
          return;
        }
      }
    };

    setExpr('blinkLeft', left);
    setExpr('blinkRight', right);
    setExpr('blink_l', left);
    setExpr('blink_r', right);

    if (Math.abs(left - right) < 0.05) {
      setExpr('blink', Math.max(left, right));
    } else {
      // Asymmetric blink (e.g. wink): clear symmetric blink
      setExpr('blink', 0);
    }
  }

  setBlinkOverride(value: number) {
    this.blinkValue = value;
  }

  setBlinkExact(left?: number, right?: number) {
    this.blinkOverrideLeft = left;
    this.blinkOverrideRight = right;
  }
}
