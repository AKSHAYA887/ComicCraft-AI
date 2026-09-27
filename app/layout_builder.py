def build_comic_layout(outline, stories, image_paths):
    story_map = {story.get("panel_number"): story for story in stories}
    layout = []
    for index, panel in enumerate(outline):
        number = panel.get("panel_number", index + 1)
        story = story_map.get(number, {})
        layout.append({
            "panel_number": number,
            "title": panel.get("title", f"Panel {number}"),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", ""),
            "image_path": image_paths[index] if index < len(image_paths) else None,
            "caption": story.get("caption", ""),
            "narration": story.get("narration", ""),
            "dialogue": story.get("dialogue", "")
        })
    return layout
