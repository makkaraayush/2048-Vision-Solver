import time
import logging
import uvicorn
from fastapi import FastAPI, WebSocket
import asyncio
from src.vision.scanner import BoardScanner
from src.ai.expectimax import ExpectimaxSolver
from src.core.board import Board
from src.core.controller import GameController
from train import GeneticTrainer, calculate_level
import src.ai.heuristics as heur
from pynput import keyboard, mouse
import threading
import os
from typing import Optional

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    t = threading.Thread(target=solver_loop, daemon=True)
    t.start()
    yield

app = FastAPI(title="CodeD3mon-2048 API", lifespan=lifespan)
connected_clients = set()
main_loop: asyncio.AbstractEventLoop = None

# Global state
saved_model = heur.load_saved_weights()
state = {
    "is_running": False,          # Scanning and calculating (Hint Mode)
    "automation_allowed": False,   # UI Toggle for safety
    "auto_play_active": False,     # Hotkey toggle for pressing keys
    "is_calibrated": False,        # True when user has manually calibrated board
    "calibration_status": "idle",  # "idle", "step1", "step2", "done", "error"
    "last_stats": {},
    "current_grid": [],
    "active_model": heur.get_active_model_mode(),  # "default" or "champion"
    "has_champion": heur.has_champion(),
    "champion_meta": heur.get_champion_meta(),
    "training_active": False,
    "training_stats": {
        "generation": saved_model.get("generation", 0),
        "level": calculate_level(saved_model.get("best_max_tile", 0)),
        "best_max_tile": saved_model.get("best_max_tile", 0),
        "best_score": saved_model.get("best_score", 0),
        "current_max_tile": 0,
        "current_score": 0,
        "games_played": saved_model.get("games_played", 0),
        "status": "Ready to Train"
    }
}

scanner_instance: Optional[BoardScanner] = None
trainer_instance: GeneticTrainer = None
trainer_thread: threading.Thread = None

calibration_start_time = 0.0
calibration_clicks = []
calibration_listener: Optional[mouse.Listener] = None

def start_calibration_session():
    global calibration_start_time, calibration_clicks, calibration_listener
    
    if calibration_listener and calibration_listener.is_alive():
        try:
            calibration_listener.stop()
        except:
            pass
            
    calibration_clicks = []
    calibration_start_time = time.time()
    state["calibration_status"] = "step1"
    trigger_broadcast()
    
    def on_click(x, y, button, pressed):
        global calibration_clicks, calibration_listener
        if not pressed or button != mouse.Button.left:
            return
            
        # Ignore clicks within 350ms of calibration start (clicking the UI button)
        if time.time() - calibration_start_time < 0.35:
            return
            
        calibration_clicks.append((int(x), int(y)))
        
        if len(calibration_clicks) == 1:
            state["calibration_status"] = "step2"
            logger.info(f"Calibration Step 1: Top-Left at ({x}, {y})")
            trigger_broadcast()
        elif len(calibration_clicks) >= 2:
            pt1 = calibration_clicks[0]
            pt2 = calibration_clicks[1]
            
            left = min(pt1[0], pt2[0])
            top = min(pt1[1], pt2[1])
            width = abs(pt2[0] - pt1[0])
            height = abs(pt2[1] - pt1[1])
            
            if width > 80 and height > 80:
                new_bbox = {"left": left, "top": top, "width": width, "height": height}
                if scanner_instance:
                    scanner_instance.set_manual_bbox(new_bbox)
                state["is_calibrated"] = True
                state["calibration_status"] = "done"
                logger.info(f"Manual board calibration complete: {new_bbox}")
            else:
                state["calibration_status"] = "error"
                logger.warning(f"Calibration box too small ({width}x{height})")
                
            trigger_broadcast()
            return False  # Stops the listener
            
    calibration_listener = mouse.Listener(on_click=on_click)
    calibration_listener.daemon = True
    calibration_listener.start()

def stop_calibration_session():
    global calibration_listener, calibration_clicks
    if calibration_listener and calibration_listener.is_alive():
        try:
            calibration_listener.stop()
        except:
            pass
    calibration_clicks = []
    state["calibration_status"] = "idle"
    trigger_broadcast()

def reset_calibration():
    stop_calibration_session()
    state["is_calibrated"] = False
    if scanner_instance:
        scanner_instance.reset_calibration()
    logger.info("Board calibration reset to automatic detection.")
    trigger_broadcast()

def on_press(key):
    try:
        if key == keyboard.Key.f9:
            if state["automation_allowed"]:
                state["auto_play_active"] = not state["auto_play_active"]
                logger.info(f"Auto-Play Active: {state['auto_play_active']}")
                trigger_broadcast()
            else:
                logger.warning("F9 pressed but Automation is not enabled in the UI!")
    except Exception:
        pass

# Start the global hotkey listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

async def broadcast_state():
    if not connected_clients:
        return
    data = state
    for client in list(connected_clients):
        try:
            await client.send_json(data)
        except:
            pass

def trigger_broadcast():
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_state(), main_loop)

def on_training_update(stats: dict):
    state["training_stats"].update(stats)
    # Update champion availability if a new champion was discovered
    state["has_champion"] = heur.has_champion()
    state["champion_meta"] = heur.get_champion_meta()
    trigger_broadcast()

def start_training_thread():
    global trainer_instance, trainer_thread
    trainer_instance = GeneticTrainer(callback=on_training_update)
    state["training_active"] = True
    trigger_broadcast()
    trainer_instance.run()
    state["training_active"] = False
    state["training_stats"]["status"] = "Training Paused"
    state["has_champion"] = heur.has_champion()
    state["champion_meta"] = heur.get_champion_meta()
    trigger_broadcast()

def stop_training():
    global trainer_instance
    if trainer_instance:
        trainer_instance.stop()
    state["training_active"] = False
    state["training_stats"]["status"] = "Stopping..."
    trigger_broadcast()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Refresh champion availability on new connection
        state["has_champion"] = heur.has_champion()
        state["champion_meta"] = heur.get_champion_meta()
        state["active_model"] = heur.get_active_model_mode()
        await websocket.send_json(state)
        while True:
            data = await websocket.receive_text()
            if data == "toggle":
                state["is_running"] = not state["is_running"]
                if state["is_running"] and scanner_instance:
                    scanner_instance.board_bbox = None  # Force fresh board detection
                logger.info(f"Scanner Running: {state['is_running']}")
                await broadcast_state()
            elif data == "toggle_automation":
                state["automation_allowed"] = not state["automation_allowed"]
                if not state["automation_allowed"]:
                    state["auto_play_active"] = False
                logger.info(f"Automation Allowed: {state['automation_allowed']}")
                await broadcast_state()
            elif data == "start_calibration":
                logger.info("Manual calibration requested via Web UI.")
                start_calibration_session()
            elif data == "cancel_calibration":
                logger.info("Manual calibration cancelled via Web UI.")
                stop_calibration_session()
            elif data == "reset_calibration":
                logger.info("Resetting calibration to auto-detect via Web UI.")
                reset_calibration()
            elif data == "toggle_model":
                if state["has_champion"]:
                    new_mode = "champion" if state["active_model"] == "default" else "default"
                    heur.set_active_model(new_mode)
                    state["active_model"] = heur.get_active_model_mode()
                    logger.info(f"Switched model to: {state['active_model']}")
                    await broadcast_state()
                else:
                    logger.warning("toggle_model requested but no champion is available yet.")
            elif data.startswith("set_model:"):
                target = data.split(":", 1)[1].strip()
                if target == "champion" and not state["has_champion"]:
                    logger.warning("Cannot set champion: no champion trained yet.")
                else:
                    heur.set_active_model(target)
                    state["active_model"] = heur.get_active_model_mode()
                    logger.info(f"Active model set to: {state['active_model']}")
                    await broadcast_state()
            elif data == "toggle_training":
                global trainer_thread
                if not state["training_active"]:
                    logger.info("Starting background evolutionary training...")
                    trainer_thread = threading.Thread(target=start_training_thread, daemon=True)
                    trainer_thread.start()
                else:
                    logger.info("Stopping background evolutionary training...")
                    stop_training()
                await broadcast_state()
            elif data in ("reset_weights", "delete_weights"):
                logger.info("Reset champion weights requested via Web UI.")
                heur.delete_saved_weights()
                state["active_model"] = "default"
                state["has_champion"] = False
                state["champion_meta"] = {}
                state["training_stats"] = {
                    "generation": 0,
                    "level": 1,
                    "best_max_tile": 0,
                    "best_score": 0,
                    "current_max_tile": 0,
                    "current_score": 0,
                    "games_played": 0,
                    "status": "Ready to Train"
                }
                logger.info("Champion weights reset to default starter baseline.")
                await broadcast_state()
            elif data == "shutdown":
                logger.info("Shutdown requested via Web UI. Exiting...")
                stop_training()
                os._exit(0)
    except Exception:
        pass
    finally:
        connected_clients.discard(websocket)

def solver_loop():
    global scanner_instance
    scanner = BoardScanner()
    scanner_instance = scanner
    solver = ExpectimaxSolver()
    controller = GameController(delay=0.1)

    logger.info("Solver thread started. Use Web UI to start scanner and allow automation.")
    
    while True:
        if state["is_running"]:
            try:
                grid = scanner.extract_grid()
                state["current_grid"] = grid
                
                board = Board(grid=grid)
                if board.is_game_over():
                    logger.info("Game Over detected!")
                    state["is_running"] = False
                    state["auto_play_active"] = False
                    trigger_broadcast()
                    continue
                    
                best_move, stats = solver.get_best_move(board)
                
                if best_move is not None:
                    state["last_stats"] = stats
                    
                    if state["automation_allowed"] and state["auto_play_active"]:
                        controller.execute_move(best_move)
                        # Wait for sliding animation before next screenshot
                        time.sleep(0.15)
                        
                    trigger_broadcast()
                else:
                    pass
                    
            except Exception as e:
                logger.error(f"Error in solver loop: {e}")
                time.sleep(1)
        else:
            time.sleep(0.1)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
