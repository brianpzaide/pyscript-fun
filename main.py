from asyncio import Event
import asyncio

from pyscript import when
from pyweb import pydom

universe_size = 64
cell_size = 8
cell_size_inner = 6
line_width = 2
canvas_size = 512
cells = [0]*4096
canvas = pydom["canvas#universe"][0]
start_pause_button = pydom["button#btn-start-pause"][0]
reset_button = pydom["button#btn-reset"][0]
simulation_speed_slider = pydom["input#simulation-speed"][0]
is_continue = Event()
simulation_speed = 1


def draw_universe():
    ctx = canvas._js.getContext("2d")
    ctx.strokeStyle = "black"
    # draw border(vertical lines)
    ctx.moveTo(0, 0)
    ctx.lineTo(0, 512)
    ctx.moveTo(512, 0)
    ctx.lineTo(512, 512)
    # //draw border (horizontal lines)
    ctx.moveTo(0, 0)
    ctx.lineTo(5120, 0)
    ctx.moveTo(0, 512)
    ctx.lineTo(512, 512)

    ctx.stroke()
    for i in range(0, 512, 8):
        # draw vertical lines
        ctx.moveTo(i, 0)
        ctx.lineTo(i, 512)
        # draw horizontal lines
        ctx.moveTo(0, i)
        ctx.lineTo(512, i)

    ctx.stroke()

@when("mousedown", "#universe")
def canvas_event_listener(e):
    is_continue.clear()
    start_pause_button.html = "Start"
    col = e.offsetX // cell_size
    row = e.offsetY // cell_size
    cells[row*universe_size + col] = (cells[row*universe_size + col] + 1) % 2
    ctx = canvas._js.getContext("2d")
    if cells[row*universe_size + col] == 1:
        ctx.fillStyle = "black"
        ctx.fillRect(col*cell_size+1, row*cell_size + 1, cell_size-2, cell_size-2)
    else:
        ctx.fillStyle = "white"
        ctx.fillRect(col*cell_size+1, row*cell_size + 1, cell_size-2, cell_size-2)

@when("click", "#btn-start-pause")
def start_pause():
    start_pause_button.html = "Pause" if start_pause_button.html == "Start" else "Start"
    if is_continue.is_set():
        is_continue.clear()
    else:
        is_continue.set()

@when("click", "#btn-reset")
def reset_universe():
    is_continue.clear()
    global cells
    cells = [0]*4096
    update_canvas()
    start_pause_button.html = "Start"

@when("input", "#simulation-speed")
def update_simulation_speed():
    is_continue.clear()
    start_pause_button.html = "Start"
    global simulation_speed
    simulation_speed = 1 / int(simulation_speed_slider.value)

def update_canvas():
    ctx = canvas._js.getContext("2d")
    for row in range(universe_size):
        for col in range(universe_size):
            if cells[row*universe_size + col] == 1:
                ctx.fillStyle = "black"
                ctx.fillRect(col*cell_size+1, row*cell_size + 1, cell_size-2, cell_size-2)
            else:
                ctx.fillStyle = "white"
                ctx.fillRect(col*cell_size+1, row*cell_size + 1, cell_size-2, cell_size-2)


async def main():
    while True:
        await asyncio.sleep(simulation_speed)
        if is_continue.is_set():
            global cells
            next_generation = [0]*4096 
            # do computations
            for row in range(universe_size):
                for col in range(universe_size):
                    next_generation[row*universe_size + col] = cells[row*universe_size + col] 
                    neighbors = [((row-1) % universe_size, (col-1) % universe_size),
                            ((row-1) % universe_size, col),
                            ((row-1) % universe_size, (col+1) % universe_size),
                            (row, (col-1) % universe_size),
                            (row, (col+1) % universe_size),
                            ((row+1) % universe_size, (col-1) % universe_size),
                            ((row+1) % universe_size, col),
                            ((row+1) % universe_size, (col+1) % universe_size),
                            ]
                    n_alive_neighbors = sum(
                        [cells[r*universe_size + c] for (r, c) in neighbors]
                    )
                    if cells[row * universe_size + col] == 1:
                        if n_alive_neighbors < 2 or n_alive_neighbors > 3:
                            next_generation[row * universe_size + col] = 0
                        else:
                            next_generation[row * universe_size + col] = 1
                    else:
                        if n_alive_neighbors == 3:
                            next_generation[row * universe_size + col] = 1
            
            cells = next_generation

            update_canvas()

draw_universe()
asyncio.ensure_future(main())
