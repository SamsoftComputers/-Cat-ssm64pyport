import pygame
import math

# Configuration
W, H = 960, 720
FOV = 60
NEAR, FAR = 0.1, 1000
CAM_SPEED = 20.0  # Units per second
CAM_TURN = 0.15
VERSION = "v0.2.1 (Fixed & Enhanced)"

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
    """SM64-style castle scene: ground, blocks, star, Mario placeholder."""
    green = (34, 139, 34)
    brown = (139, 90, 43)
    brick = (178, 34, 34)
    gold = (218, 165, 32)
    mario_red = (220, 20, 60)
    mario_skin = (255, 213, 170)
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
    scene.append((box_tris(5, 1.5, 5, 0.8, 1.5, 0.5), mario_red))
    scene.append((box_tris(5, 2.8, 5, 0.6, 0.5, 0.6), mario_skin))
    for i in range(3):
        s = 4 - i
        scene.append((box_tris(-15, i*2, 15, s, 2, s), green))
    return scene

def draw_hud(screen):
    font = pygame.font.Font(None, 28)
    t = font.render("WASD move | SPACE/LSHIFT up/down | ESC quit", True, (220, 220, 220))
    screen.blit(t, (10, H - 30))

def draw_menu(screen):
    # ... (same background, head rendering)
    
    def draw_text_3d(text, x, y, col, size=80):
        f = pygame.font.Font(None, size)
        for dx, dy in [(-2,2), (2,2), (2,-2), (-2,-2)]:
            s = f.render(text, True, (0, 0, 100))
            r = s.get_rect(center=(x+dx, y+dy))
            screen.blit(s, r)
        s = f.render(text, True, col)
        r = s.get_rect(center=(x, y))
        screen.blit(s, r)

    # ... rest unchanged

def main():
    global W, H
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption(f"Cat's ! SM64 {VERSION}")
    clock = pygame.time.Clock()

    # Menu loop unchanged...

    # --- GAME STATE ---
    cam_pos = [0.0, 2.0, 40.0]  # Start higher to see bridge
    cam_rot = [0.0, 0.0]
    
    scene = get_castle_scene()
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            if e.type == pygame.VIDEORESIZE:
                W, H = e.w, e.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

        # Mouse look with centering
        mx, my = pygame.mouse.get_rel()
        if mx or my:  # Only update if moved
            cam_rot[1] -= mx * CAM_TURN * dt * 60
            cam_rot[0] -= my * CAM_TURN * dt * 60
            cam_rot[0] = max(-1.57, min(1.57, cam_rot[0]))  # Clamp near ±90°
        pygame.mouse.set_pos((W//2, H//2))  # Center mouse

        # Movement
        keys = pygame.key.get_pressed()
        cy, sy = math.cos(cam_rot[1]), math.sin(cam_rot[1])
        move_speed = CAM_SPEED * dt
        
        if keys[pygame.K_w]: 
            cam_pos[0] += cy * move_speed
            cam_pos[2] -= sy * move_speed
        if keys[pygame.K_s]: 
            cam_pos[0] -= cy * move_speed
            cam_pos[2] += sy * move_speed
        if keys[pygame.K_a]: 
            cam_pos[0] -= sy * move_speed
            cam_pos[2] -= cy * move_speed
        if keys[pygame.K_d]: 
            cam_pos[0] += sy * move_speed
            cam_pos[2] += cy * move_speed
        if keys[pygame.K_SPACE]: cam_pos[1] += move_speed
        if keys[pygame.K_LSHIFT]: cam_pos[1] -= move_speed
        
        # Simple ground clamp
        if cam_pos[1] < 2.0:
            cam_pos[1] = 2.0

        # Render 3D scene
        screen.fill((135, 206, 235))
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
        to_draw.sort(key=lambda x: -x[2])
        for (tri, color, _) in to_draw:
            draw_tri(screen, tri, color, cam_pos, cam_rot)

        draw_hud(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
