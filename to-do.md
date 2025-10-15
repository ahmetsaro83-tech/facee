# To-Do List: PyQt5 TikTok to Facebook App

### Phase 1: GUI Skeleton (PyQt5)
- [ ] Create `app.py`.
- [ ] In `app.py`, design the main application window (`QMainWindow`).
- [ ] Add input widgets (`QLineEdit`) for: TikTok URL, Facebook Email, Facebook Password.
- [ ] Add a "Start Process" button (`QPushButton`).
- [ ] Add a large, read-only text area (`QTextEdit`) to be used as a status log.
- [ ] Create a basic layout (`QVBoxLayout`, `QHBoxLayout`) to arrange the widgets neatly.

### Phase 2: Backend Modules (Logic)
- [ ] Create `tiktok_scraper.py` with the user-guided `scrape_tiktok_info` function.
- [ ] Create `video_downloader.py` with the user-guided `download_video` function.
- [ ] Create `data_manager.py` with its save/load functions.
- [ ] Create `gemini_handler.py` with the `enhance_content` function.
- [ ] Create `facebook_uploader.py` with the user-guided `upload_to_facebook` function.

### Phase 3: Background Worker (QThread)
- [ ] Create `worker.py`.
- [ ] In `worker.py`, define a `Worker` class that inherits from `QThread`.
- [ ] This class should have signals for progress updates (e.g., `progress = pyqtSignal(str)`) and completion (`finished = pyqtSignal()`).
- [ ] Create a `run` method in the `Worker` class. This method will contain the main automation logic (calling the scraper, downloader, etc.).
- [ ] Inside the `run` method, emit the `progress` signal after each major step (e.g., `self.progress.emit("Video downloading...")`).

### Phase 4: Integration (Connecting GUI to Logic)
- [ ] In `app.py`, import the `Worker` and all backend modules.
- [ ] Connect the "Start Process" button's `clicked` signal to a new method (e.g., `start_automation`).
- [ ] In `start_automation`:
    - [ ] Read the inputs (URL, email, etc.) from the GUI widgets.
    - [ ] Create an instance of the `Worker` thread, passing the necessary inputs to it.
    - [ ] Connect the worker's `progress` signal to a method that updates the status log (`QTextEdit`).
    - [ ] Connect the worker's `finished` signal to a method that re-enables the "Start" button and shows a "Completed" message.
    - [ ] Start the worker thread using `worker.start()`.

### Phase 5: Final Touches
- [ ] Implement saving/loading of settings (e.g., Facebook email) for user convenience.
- [ ] Add comprehensive error handling. If any step in the worker fails, it should emit a signal with the error message to be displayed on the GUI.