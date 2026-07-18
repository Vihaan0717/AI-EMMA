import logging

logger = logging.getLogger("VisionTools")

async def look_at_screen(query: str, system_instance=None):
    """
    Called by an agent when they need to see the screen.
    Requires the `system_instance` (NexusSystem) to access the ScreenMonitor and AIEngine.
    """
    logger.info(f"Agent requested vision context for query: '{query}'")
    
    if not system_instance or not hasattr(system_instance, 'screen_monitor'):
        return "Error: Screen Monitor is not active or available."

    context = system_instance.screen_monitor.get_latest_context()
    img_path = context.get('latest_screenshot')
    active_win = context.get('active_window')
    
    if not img_path:
        return f"I know the active window is '{active_win}', but no recent screenshot is available."

    logger.info(f"Analyzing {img_path} with query: {query}")
    
    try:
        # ai_engine.vision_analyze returns text extracted from the image
        result = await system_instance.ai.vision_analyze(query, img_path)
        return f"Active Window: '{active_win}'.\nVisual Analysis: {result}"
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        return f"Failed to analyze screen visually: {e}"
