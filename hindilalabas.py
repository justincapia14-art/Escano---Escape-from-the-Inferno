def apply_screen_bounds(player_x, player_y, player_w, player_h, screen_w, screen_h):
    # Left at Right Bounds (X-axis)
    if player_x < 0:
        player_x = 0
    elif player_x > screen_w - player_w:
        player_x = screen_w - player_w

    # Top at Bottom Bounds (Y-axis)
    if player_y < 0:
        player_y = 0
    elif player_y > screen_h - player_h:
        player_y = screen_h - player_h

    return player_x, player_y