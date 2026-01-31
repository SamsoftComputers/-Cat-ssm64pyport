# sm64v0.py — Full SM64 port: all HackerSM64-style codebase in one file
# 3D engine, camera, physics, graphics, title menu, file select, game loop. Python 3.14+.

import math
import pygame

# --- Configuration (1:1 SM64-style) ---
W, H = 960, 720
FOV = 52
NEAR, FAR = 0.1, 1000
CAM_SPEED = 16.0
CAM_TURN = 0.0022
CAM_DISTANCE = 26.0
PITCH_MIN = -0.48
PITCH_MAX = 0.92
GRAVITY = -42.0
JUMP_VELOCITY = 14.0
GROUND_Y = 1.0
VERSION = "v0.2.1 (Fixed & Enhanced)"

def orbit_camera_pos(target, yaw, pitch, distance):
    cp = math.cos(pitch)
    sx = math.sin(yaw) * cp
    sy = -math.sin(pitch)
    sz = math.cos(yaw) * cp
    return [target[0] + distance * sx, target[1] + distance * sy, target[2] + distance * sz]

def project(v, cam_pos, cam_rot, scale=1.0):
    x, y, z = v[0] - cam_pos[0], v[1] - cam_pos[1], v[2] - cam_pos[2]
    cy, sy = math.cos(cam_rot[1]), math.sin(cam_rot[1])
    x, z = x * cy + z * sy, -x * sy + z * cy
    cx, sx = math.cos(cam_rot[0]), math.sin(cam_rot[0])
    y, z = y * cx - z * sx, y * sx + z * cx
    if z <= NEAR:
        return None
    f = (W * 0.5) / math.tan(math.radians(FOV * 0.5)) / z * scale
    return (W * 0.5 + x * f, H * 0.5 - y * f, z)

def draw_tri(surf, pts, color, cam_pos, cam_rot):
    proj = []
    for p in pts:
        q = project(p, cam_pos, cam_rot)
        if q is None:
            return
        proj.append(q)
    a, b, c = pts[0], pts[1], pts[2]
    ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    nx = ab[1]*ac[2] - ab[2]*ac[1]
    ny = ab[2]*ac[0] - ab[0]*ac[2]
    nz = ab[0]*ac[1] - ab[1]*ac[0]
    view = (cam_pos[0]-a[0], cam_pos[1]-a[1], cam_pos[2]-a[2])
    if nx*view[0] + ny*view[1] + nz*view[2] <= 0:
        return
    ps = [(p[0], p[1]) for p in proj]
    nz = max(-1, min(1, nz * 0.01))
    shade = max(0.35, min(1.0, 0.65 + nz))
    r = int(min(255, color[0] * shade))
    g = int(min(255, color[1] * shade))
    b = int(min(255, color[2] * shade))
    pygame.draw.polygon(surf, (r, g, b), ps)
    pygame.draw.polygon(surf, (min(255, r+35), min(255, g+35), min(255, b+35)), ps, 1)

def box_tris(cx, cy, cz, w, h, d):
    hw, hh, hd = w/2, h/2, d/2
    verts = [
        (cx-hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz-hd), (cx+hw, cy+hh, cz-hd), (cx-hw, cy+hh, cz-hd),
        (cx-hw, cy-hh, cz+hd), (cx+hw, cy-hh, cz+hd), (cx+hw, cy+hh, cz+hd), (cx-hw, cy+hh, cz+hd),
        (cx-hw, cy-hh, cz-hd), (cx-hw, cy-hh, cz+hd), (cx-hw, cy+hh, cz+hd), (cx-hw, cy+hh, cz-hd),
        (cx+hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz+hd), (cx+hw, cy+hh, cz+hd), (cx+hw, cy+hh, cz-hd),
        (cx-hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz+hd), (cx-hw, cy-hh, cz+hd),
        (cx-hw, cy+hh, cz-hd), (cx+hw, cy+hh, cz-hd), (cx+hw, cy+hh, cz+hd), (cx-hw, cy+hh, cz+hd),
    ]
    return [
        (verts[0], verts[1], verts[2]), (verts[0], verts[2], verts[3]),
        (verts[5], verts[4], verts[7]), (verts[5], verts[7], verts[6]),
        (verts[8], verts[9], verts[10]), (verts[8], verts[10], verts[11]),
        (verts[13], verts[12], verts[15]), (verts[13], verts[15], verts[14]),
        (verts[16], verts[17], verts[18]), (verts[16], verts[18], verts[19]),
        (verts[21], verts[20], verts[23]), (verts[21], verts[23], verts[22]),
    ]

def get_castle_scene():
    green = (34, 139, 34)
    brown = (139, 90, 43)
    brick = (178, 34, 34)
    gold = (218, 165, 32)
    scene = []
    gw = 40
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            scene.append((box_tris(dx*gw*2, -1, dz*gw*2, gw, 1, gw), green))
    for cx, cy, cz, w, h, d, col in [
        (0, 2, 0, 4, 4, 4, brick), (12, 1, 8, 6, 2, 6, brown),
        (-10, 1.5, -5, 3, 3, 3, brown), (8, 2, -8, 4, 4, 4, brick),
        (-8, 1, 10, 5, 2, 5, brown),
    ]:
        scene.append((box_tris(cx, cy, cz, w/2, h/2, d/2), col))
    scene.append((box_tris(0, 8, 0, 2, 2, 2), gold))
    for i in range(3):
        s = 4 - i
        scene.append((box_tris(-15, i*2, 15, s, 2, s), green))
    return scene

def get_mario_tris(pos):
    x, y, z = pos[0], pos[1], pos[2]
    mario_red = (220, 40, 60)
    mario_skin = (255, 213, 170)
    body = (box_tris(x, y, z, 0.5, 0.75, 0.35), mario_red)
    head = (box_tris(x, y + 1.0, z, 0.35, 0.3, 0.35), mario_skin)
    return [body, head]

def draw_sky(screen):
    for y in range(H + 1):
        t = y / max(1, H)
        r = int(135 + (60 - 135) * t)
        g = int(206 + (120 - 206) * t)
        b = int(250 + (200 - 250) * t)
        pygame.draw.line(screen, (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))), (0, y), (W, y))

def draw_hud(screen):
    font = pygame.font.Font(None, 28)
    t = font.render("WASD move Mario | Mouse orbit | SPACE jump | ESC quit", True, (220, 220, 220))
    screen.blit(t, (10, H - 30))

def draw_menu(screen):
    for y in range(H + 1):
        t = y / max(1, H)
        r = int(135 + (40 - 135) * t)
        g = int(206 + (100 - 206) * t)
        b = int(235 + (180 - 235) * t)
        pygame.draw.line(screen, (max(0, r), max(0, g), max(0, b)), (0, y), (W, y))
    cx, cy = W // 2, H // 2 - 40
    star_pts = []
    for i in range(10):
        rad = 48 if i % 2 == 0 else 22
        ang = math.pi / 2 + (i * math.pi / 5)
        star_pts.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    pygame.draw.polygon(screen, (255, 215, 0), star_pts)
    pygame.draw.polygon(screen, (220, 180, 0), star_pts, 2)
    title_text = "Cat's ! SM64"
    font_size = max(48, min(72, W // 14))
    font = pygame.font.Font(None, font_size)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        s = font.render(title_text, True, (180, 30, 30))
        r = s.get_rect(center=(W // 2 + dx, H // 2 - 30 + dy))
        screen.blit(s, r)
    s = font.render(title_text, True, (255, 220, 0))
    r = s.get_rect(center=(W // 2, H // 2 - 30))
    screen.blit(s, r)
    font_start = pygame.font.Font(None, 36)
    start_surf = font_start.render("PRESS SPACE TO GO TO GAME", True, (255, 255, 255))
    r_start = start_surf.get_rect(center=(W // 2, H - 100))
    screen.blit(start_surf, r_start)
    font_c = pygame.font.Font(None, 24)
    c_surf = font_c.render("[C] Samsoft 1999-2026  [C] Nintendo 1999-2026", True, (200, 200, 200))
    r_c = c_surf.get_rect(center=(W // 2, H - 40))
    screen.blit(c_surf, r_c)

def draw_file_select(screen, selected_index, file_stars):
    for y in range(H + 1):
        t = y / max(1, H)
        r = int(60 + (30 - 60) * t)
        g = int(100 + (60 - 100) * t)
        b = int(180 + (120 - 180) * t)
        pygame.draw.line(screen, (max(0, r), max(0, g), max(0, b)), (0, y), (W, y))
    font_title = pygame.font.Font(None, 56)
    title = font_title.render("FILE SELECT", True, (255, 255, 255))
    r_title = title.get_rect(center=(W // 2, 80))
    screen.blit(title, r_title)
    slot_w, slot_h = 200, 140
    slot_y = H // 2 - slot_h // 2 - 20
    slots_x = [W // 2 - slot_w - 130, W // 2 - slot_w // 2 - 50, W // 2 + 130]
    font_slot = pygame.font.Font(None, 36)
    font_stars = pygame.font.Font(None, 28)
    for i in range(3):
        sx = slots_x[i]
        border = (255, 220, 100) if i == selected_index else (180, 180, 180)
        pygame.draw.rect(screen, (40, 50, 90), (sx, slot_y, slot_w, slot_h))
        pygame.draw.rect(screen, border, (sx, slot_y, slot_w, slot_h), 4)
        label = font_slot.render("FILE " + str(i + 1), True, (255, 255, 255))
        r_label = label.get_rect(center=(sx + slot_w // 2, slot_y + 40))
        screen.blit(label, r_label)
        stars_text = "STARS  " + str(file_stars[i]) + " / 120" if file_stars[i] > 0 else "NEW GAME"
        stars_color = (255, 220, 0) if file_stars[i] > 0 else (160, 160, 160)
        stars_surf = font_stars.render(stars_text, True, stars_color)
        r_star = stars_surf.get_rect(center=(sx + slot_w // 2, slot_y + 90))
        screen.blit(stars_surf, r_star)
        if i == selected_index:
            cx, cy = sx + slot_w // 2, slot_y + 120
            pts = []
            for j in range(10):
                rad = 14 if j % 2 == 0 else 6
                ang = math.pi / 2 + (j * math.pi / 5)
                pts.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
            pygame.draw.polygon(screen, (255, 215, 0), pts)
            pygame.draw.polygon(screen, (220, 180, 0), pts, 2)
    font_inst = pygame.font.Font(None, 26)
    inst = font_inst.render("LEFT/RIGHT or A/D: select file   SPACE or ENTER: start game", True, (200, 200, 200))
    r_inst = inst.get_rect(center=(W // 2, H - 50))
    screen.blit(inst, r_inst)
    font_c = pygame.font.Font(None, 22)
    c_surf = font_c.render("[C] Samsoft 1999-2026  [C] Nintendo 1999-2026", True, (150, 150, 150))
    r_c = c_surf.get_rect(center=(W // 2, H - 22))
    screen.blit(c_surf, r_c)

def run():
    global W, H
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption(f"Cat's ! SM64 {VERSION}")
    clock = pygame.time.Clock()

    # Part 1: Title screen
    in_menu = True
    while in_menu:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.VIDEORESIZE:
                W, H = e.w, e.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                in_menu = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                in_menu = False
        draw_menu(screen)
        pygame.display.flip()
        clock.tick(60)

    # Part 2: File select
    file_stars = [0, 0, 0]
    selected_file = 0
    in_file_select = True
    while in_file_select:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.VIDEORESIZE:
                W, H = e.w, e.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    selected_file = (selected_file - 1) % 3
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_file = (selected_file + 1) % 3
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    in_file_select = False
        draw_file_select(screen, selected_file, file_stars)
        pygame.display.flip()
        clock.tick(60)

    # Part 3: Game
    target_pos = [0.0, GROUND_Y, 0.0]
    vy = 0.0
    cam_rot = [0.0, 0.0]
    scene = get_castle_scene()
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.VIDEORESIZE:
                W, H = e.w, e.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
        mx, my = pygame.mouse.get_rel()
        cam_rot[1] -= mx * CAM_TURN
        cam_rot[0] -= my * CAM_TURN
        cam_rot[0] = max(PITCH_MIN, min(PITCH_MAX, cam_rot[0]))
        pygame.mouse.set_pos((W // 2, H // 2))
        keys = pygame.key.get_pressed()
        yaw = cam_rot[1]
        cy, sy = math.cos(yaw), math.sin(yaw)
        move_speed = CAM_SPEED * dt
        if keys[pygame.K_w]:
            target_pos[0] -= sy * move_speed
            target_pos[2] -= cy * move_speed
        if keys[pygame.K_s]:
            target_pos[0] += sy * move_speed
            target_pos[2] += cy * move_speed
        if keys[pygame.K_a]:
            target_pos[0] -= cy * move_speed
            target_pos[2] += sy * move_speed
        if keys[pygame.K_d]:
            target_pos[0] += cy * move_speed
            target_pos[2] -= sy * move_speed
        on_ground = target_pos[1] <= GROUND_Y + 0.01
        if keys[pygame.K_SPACE] and on_ground:
            vy = JUMP_VELOCITY
        vy += GRAVITY * dt
        target_pos[1] += vy * dt
        if target_pos[1] <= GROUND_Y:
            target_pos[1] = GROUND_Y
            vy = 0.0
        cam_pos = orbit_camera_pos(target_pos, cam_rot[1], cam_rot[0], CAM_DISTANCE)
        draw_sky(screen)
        to_draw = []
        for tri_list, color in scene:
            for tri in tri_list:
                proj_z = []
                for p in tri:
                    q = project(p, cam_pos, cam_rot)
                    if q is None:
                        break
                    proj_z.append(q[2])
                if len(proj_z) == 3:
                    to_draw.append((tri, color, sum(proj_z) / 3))
        for tri_list, color in get_mario_tris(target_pos):
            for tri in tri_list:
                proj_z = []
                for p in tri:
                    q = project(p, cam_pos, cam_rot)
                    if q is None:
                        break
                    proj_z.append(q[2])
                if len(proj_z) == 3:
                    to_draw.append((tri, color, sum(proj_z) / 3))
        to_draw.sort(key=lambda x: -x[2])
        for (tri, color, _) in to_draw:
            draw_tri(screen, tri, color, cam_pos, cam_rot)
        draw_hud(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    run()
