; ====================================================================
; 100-Clicks Mouse Burst (AutoHotkey Script)
; 1 Right Click -> 100 Rapid Right Clicks
; Works with AutoHotkey v1.1+ and v2.0+
; ====================================================================

#NoEnv
#SingleInstance Force
SetBatchLines -1
Process, Priority,, High

global isEnabled := false
global clicksPerBurst := 100
global clickDelayMs := 3

; Hotkey: F6 to Toggle ON / OFF
F6::
    isEnabled := !isEnabled
    if (isEnabled) {
        SoundBeep, 1200, 150
        ToolTip, [100 Right-Clicks Burst: ON] - Click right mouse to burst!
    } else {
        SoundBeep, 600, 150
        ToolTip, [100 Right-Clicks Burst: OFF] - Normal mouse
    }
    SetTimer, RemoveToolTip, -1500
return

; Hotkey: ESC for Emergency Pause
Esc::
    if (isEnabled) {
        isEnabled := false
        SoundBeep, 600, 150
        ToolTip, [100 Right-Clicks Burst: PAUSED]
        SetTimer, RemoveToolTip, -1500
    }
return

; Hotkey: F8 to burst 100 Right Clicks directly at cursor position
F8::
    Loop, %clicksPerBurst% {
        Click, Right
        Sleep, %clickDelayMs%
    }
return

; Intercept Right Mouse Click when enabled
~$RButton::
    if (!isEnabled)
        return

    ; Fire 99 additional right clicks (1 physical + 99 synthetic = 100 clicks)
    extraClicks := clicksPerBurst - 1
    Loop, %extraClicks% {
        if (!isEnabled)
            break
        Click, Right
        Sleep, %clickDelayMs%
    }
    ; Wait for physical button release to avoid immediate re-trigger
    KeyWait, RButton
return

RemoveToolTip:
    ToolTip
return
