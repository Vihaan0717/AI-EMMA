import os
import subprocess
import logging
from mcp_base.agent_mcp_server import AgentMCPServer

# Initialize MCP Server for OS Controller
os_server = AgentMCPServer("os_controller", "God-Mode Windows OS Executive")
mcp = os_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def announce_task(message: str, voice_name: str = None, rate: int = 0):
    """
    Uses built-in Windows PowerShell Speech Synthesis for instant, zero-latency announcements.
    Supports routing to specific voices (e.g. Zira for Psyche) and adjusting speech rate.
    """
    logger.info(f"Announcing: {message} [Voice: {voice_name}, Rate: {rate}]")
    # Clean the message to prevent PowerShell syntax errors on single quotes or newlines
    clean_message = message.replace("'", "''").replace("\n", " ").replace("\r", " ")
    
    ps_command = (
        "Add-Type -AssemblyName System.Speech; "
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.Rate = {rate}; "
    )
    if voice_name:
        ps_command += f"try {{ $synth.SelectVoice('{voice_name}') }} catch {{ }}; "
        
    ps_command += f"$synth.Speak('{clean_message}')"
    
    subprocess.run(["powershell", "-Command", ps_command], capture_output=True)

def os_open_app(app_name: str) -> str:
    """
    Opens common applications on Windows.
    Supported short names: 'spotify', 'whatsapp', 'chrome', 'notepad', 'calculator'
    """
    app_map = {
        "spotify": "spotify",
        "whatsapp": "whatsapp",
        "chrome": "chrome",
        "notepad": "notepad",
        "calculator": "calc"
    }
    
    target = app_map.get(app_name.lower(), app_name)
    
    try:
        subprocess.run(["powershell", "-Command", f"start {target}"], check=True)
        announce_task(f"Successfully opened {app_name}")
        return f"Opened application: {target}"
    except Exception as e:
        err_msg = f"Failed to open {app_name}. Please ensure it is installed."
        announce_task(err_msg)
        return err_msg

def os_media_control(action: str) -> str:
    """
    Controls media playback on Windows (Spotify, YouTube, etc).
    Valid actions: 'play_pause', 'next', 'previous'
    """
    # Using PowerShell to simulate media key presses
    key_map = {
        "play_pause": "0xB3", # VK_MEDIA_PLAY_PAUSE
        "next": "0xB0",       # VK_MEDIA_NEXT_TRACK
        "previous": "0xB1"    # VK_MEDIA_PREV_TRACK
    }
    
    vk_code = key_map.get(action.lower())
    if not vk_code:
        return f"Invalid action: {action}. Use play_pause, next, or previous."
        
    ps_script = f"""
    $wsh = New-Object -ComObject WScript.Shell
    $wsh.SendKeys([char]{vk_code})
    """
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True)
        announce_task(f"Media {action.replace('_', ' ')} executed.")
        return f"Executed media control: {action}"
    except Exception as e:
        return f"Failed to execute media control: {str(e)}"

def os_volume_control(level: int) -> str:
    """
    Sets the master system volume (0 to 100).
    """
    if level < 0 or level > 100:
        return "Volume must be between 0 and 100."
        
    # PowerShell script to change volume via AudioEndpointVolume API
    ps_script = f"""
    $obj = new-object -com wscript.shell 
    $obj.SendKeys([char]173) 
    # Note: Sending volume keys is tricky, a better script is needed for exact %
    # For simplicity in God-Mode, we use an endpoint volume script:
    
    Add-Type -TypeDefinition @"
    using System.Runtime.InteropServices;
    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioEndpointVolume {{
        int f(); int g(); int h(); int i();
        int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
        int j(); int GetMasterVolumeLevelScalar(out float pfLevel);
    }}
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {{
        int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
    }}
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {{
        int f();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }}
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDeviceEnumeratorComObject {{}}
    public class Audio {{
        public static void SetVolume(int volume) {{
            IMMDeviceEnumerator de = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
            IMMDevice device; de.GetDefaultAudioEndpoint(0, 1, out device);
            IAudioEndpointVolume aev; System.Guid guid = typeof(IAudioEndpointVolume).GUID;
            device.Activate(ref guid, 1, 0, out aev);
            aev.SetMasterVolumeLevelScalar((float)volume / 100, System.Guid.Empty);
        }}
    }}
"@
    [Audio]::SetVolume({level})
    """
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True)
        announce_task(f"Volume set to {level} percent.")
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume: {str(e)}"

def os_execute_powershell(script: str) -> str:
    """
    GOD MODE: Executes arbitrary PowerShell code.
    Use this for complex OS tasks like checking RAM, clearing temp files, etc.
    """
    try:
        result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        
        # Announce success generically
        if result.returncode == 0:
            announce_task("PowerShell task successfully executed.")
        else:
            announce_task("PowerShell task encountered an error.")
            
        return f"Output:\n{output}\nErrors:\n{result.stderr}"
    except Exception as e:
        return f"Execution failed: {str(e)}"

if mcp:
    mcp.tool()(os_open_app)
    mcp.tool()(os_media_control)
    mcp.tool()(os_volume_control)
    mcp.tool()(os_execute_powershell)

if __name__ == "__main__":
    logger.info("Starting OS Controller MCP Server...")
    os_server.run()
