"""Run deterministic gameplay checks without opening a window."""
from game import World, PLATFORMS


def run_checks():
    w = World()
    w.jump()
    for _ in range(150):
        w.update(1/120, 0)
    assert w.grounded and w.y == 640
    # Verify each shelf is reachable with ordinary horizontal movement.
    for index in range(len(PLATFORMS)-1):
        start, target = PLATFORMS[index:index+2]
        w = World()
        w.monster_hp = 0
        w.x = 170 if index == 0 else (start[0]+start[2]-15 if target[0] > start[0] else start[0]+15)
        w.y = start[1]-25
        destination = target[0]+20 if target[0] > start[0] else target[0]+target[2]-20
        w.jump()
        landed = False
        for _ in range(150):
            direction = 1 if destination-w.x > 3 else -1 if destination-w.x < -3 else 0
            w.update(1/120, direction)
            if w.grounded and w.y == target[1]-25:
                landed = True
                break
        assert landed, f'Shelf {index+1} unreachable'
    w = World()
    w.x, w.y = 170, 526
    w.update_battle(.01)
    assert w.ammo == 1
    w.ammo = 6
    w.invincible = 100
    for _ in range(6):
        w.throw_eye()
        for _ in range(120):
            w.update_battle(1/120)
    assert w.monster_hp == 0
    w.x, w.y, w.grounded = 790, 130, True
    w.update_battle(.01)
    assert w.state == 'won'
    w.reset()
    for _ in range(3):
        w.invincible = 0
        w.slime = [[w.x, w.y, 0, 0]]
        w.update_battle(.01)
    assert w.state == 'lost'
    w.reset()
    assert w.health == 3 and w.state == 'playing' and not w.shots
    # A real final hit starts a full seven-second escape window.
    w.monster_hp = 1
    w.shots = [[545, 390, 0, 0]]
    w.update_battle(.01)
    assert w.monster_hp == 0 and w.respawn_timer == 7
    w.update_battle(6.99)
    assert w.monster_hp == 0
    w.update_battle(.02)
    assert w.monster_hp == 6 and w.respawn_timer == 0
    assert w.state == 'eaten' and w.health == 0
    w.update(1.6, 0)
    assert w.eaten_timer >= 1.5
    w.reset()
    w.x, w.y = 800, 100
    w.update(.01, 0)
    assert w.x == 714 and w.state == 'playing'
    # Defeat opens the gate; winning before the deadline freezes it.
    w.monster_hp = 1
    w.shots = [[545, 390, 0, 0]]
    w.update_battle(.01)
    assert w.hurt_timer > 0 and len(w.particles) == 100
    w.x, w.y, w.grounded = 790, 130, True
    w.update_battle(.01)
    assert w.state == 'won'
    w.update(8, 0)
    assert w.state == 'won' and w.monster_hp == 0
    w.reset()
    w.update_battle(1.11)
    assert len(w.slime) == 1
    assert round((w.slime[0][2]**2+w.slime[0][3]**2)**.5) == 285
    print('PASS: faster attacks, seven-second revival, repeated defeat, win deadline')
    print('PASS: jumping, all shelf transitions, collecting, combat, win, lose, restart')


if __name__ == '__main__':
    run_checks()
