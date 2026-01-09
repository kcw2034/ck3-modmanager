import sys
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QLabel, 
                               QPushButton, QSplitter, QComboBox, QMessageBox,
                               QCheckBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QSize, Signal, QThread
from PySide6.QtGui import QColor, QPalette, QKeySequence

from ck3_mod_manager.database.launcher_db import LauncherDB
from ck3_mod_manager.analyzer import ModAnalyzer

class ModListItemWidget(QWidget):
    def __init__(self, mod, parent=None, show_checkbox=True, show_handle=True):
        super().__init__(parent)
        self.mod = mod
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Drag Handle
        if show_handle:
            self.drag_handle = QLabel("≡")
            self.drag_handle.setStyleSheet("color: #666; font-size: 16px; font-weight: bold;")
            self.drag_handle.setCursor(Qt.OpenHandCursor)
            layout.addWidget(self.drag_handle)
        
        # Checkbox
        if show_checkbox:
            self.checkbox = QCheckBox()
            self.checkbox.setChecked(mod.get('enabled', False))
            layout.addWidget(self.checkbox)
        else:
            self.checkbox = None
        
        # Info Layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Name
        display_name = mod.get('displayName') or mod.get('name') or "Unknown"
        self.name_label = QLabel(display_name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        info_layout.addWidget(self.name_label)
        
        # Version
        version = mod.get('version', '?')
        self.version_label = QLabel(f"v{version}")
        self.version_label.setStyleSheet("color: #aaa; font-size: 11px;")
        info_layout.addWidget(self.version_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()

        # Conflict Icon
        self.conflict_icon = QLabel("⚠️")
        self.conflict_icon.setStyleSheet("color: #ffc107; font-size: 16px; margin-right: 5px;")
        self.conflict_icon.setToolTip("No conflicts detected")
        self.conflict_icon.hide()
        layout.addWidget(self.conflict_icon)

    def is_checked(self):
        return self.checkbox.isChecked() if self.checkbox else False
        
    def set_conflict_status(self, conflicting_mods):
        if conflicting_mods:
            self.conflict_icon.show()
            mods_str = ", ".join(conflicting_mods[:3])
            if len(conflicting_mods) > 3:
                mods_str += f", and {len(conflicting_mods)-3} others"
            self.conflict_icon.setToolTip(f"Conflicts with: {mods_str}")
        else:
            self.conflict_icon.hide()

class ModLibraryWidget(QWidget):
    mod_added = Signal()

    def __init__(self, db: LauncherDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.all_mods = []
        self.init_ui()
        self.load_mods()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search all available mods...")
        self.search_input.textChanged.connect(self.filter_mods)
        search_layout.addWidget(self.search_input)
        
        self.add_btn = QPushButton("Add to Current Playset")
        self.add_btn.setStyleSheet("background-color: #198754; font-weight: bold;")
        self.add_btn.clicked.connect(self.add_selected_mod)
        search_layout.addWidget(self.add_btn)
        
        layout.addLayout(search_layout)
        
        # List
        self.mod_list = QListWidget()
        self.mod_list.setSelectionMode(QListWidget.SingleSelection)
        self.mod_list.setDragEnabled(True)
        layout.addWidget(self.mod_list)

    def load_mods(self):
        self.all_mods = self.db.get_all_mods()
        self.update_list()

    def update_list(self, filter_text=""):
        self.mod_list.clear()
        filter_text = filter_text.lower()
        
        for mod in self.all_mods:
            display_name = mod.get('displayName') or mod.get('name') or "Unknown"
            if filter_text and filter_text not in display_name.lower():
                continue
                
            item = QListWidgetItem(self.mod_list)
            item.setSizeHint(QSize(0, 50))
            widget = ModListItemWidget(mod, show_checkbox=False, show_handle=False)
            item.setData(Qt.UserRole, mod['mod_id'])
            
            self.mod_list.addItem(item)
            self.mod_list.setItemWidget(item, widget)

    def filter_mods(self, text):
        self.update_list(text)

    def add_selected_mod(self):
        items = self.mod_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "Please select a mod to add.")
            return
            
        mod_id = items[0].data(Qt.UserRole)
        
        # Helper to get main window's current playset (a bit coupled, but simple for now)
        # Ideally we'd emit a signal with the mod_id and let MainWindow handle it
        main_window = self.window()
        if isinstance(main_window, MainWindow) and main_window.current_playset_id:
            if self.db.add_mod_to_playset(main_window.current_playset_id, mod_id):
                QMessageBox.information(self, "Success", "Mod added to playset.")
                self.mod_added.emit()
            else:
                QMessageBox.warning(self, "Error", "Mod already in playset or failed to add.")
        else:
             QMessageBox.warning(self, "Error", "No active playset found.")

class ConflictWorker(QThread):
    finished = Signal(dict)
    
    def __init__(self, analyzer, mods):
        super().__init__()
        self.analyzer = analyzer
        self.mods = mods
        
    def run(self):
        conflicts = self.analyzer.analyze_conflicts(self.mods)
        self.finished.emit(conflicts)

class ConflictReportWidget(QWidget):
    def __init__(self, db: LauncherDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.analyzer = ModAnalyzer()
        self.current_playset_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run Compatibility Check")
        self.run_btn.setStyleSheet("background-color: #d63384; font-weight: bold;") # Pinkish
        self.run_btn.clicked.connect(self.run_check)
        ctrl_layout.addWidget(self.run_btn)
        
        self.status_label = QLabel("Click run to check for file conflicts in the active playset.")
        self.status_label.setStyleSheet("color: #bbb; margin-left: 10px;")
        ctrl_layout.addWidget(self.status_label)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)
        
        # Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File / Mod", "Conflict Type"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.tree)

    def set_current_playset(self, playset_id):
        self.current_playset_id = playset_id
        self.tree.clear()
        self.status_label.setText("Ready to check active playset.")

    def run_check(self):
        if not self.current_playset_id:
            QMessageBox.warning(self, "Warning", "No active playset selected.")
            return

        # Get enabled mods only
        all_mods = self.db.get_mods_for_playset(self.current_playset_id)
        enabled_mods = [m for m in all_mods if m.get('enabled')]
        
        if len(enabled_mods) < 2:
            QMessageBox.information(self, "Info", "Need at least 2 enabled mods to check for conflicts.")
            return

        self.run_btn.setEnabled(False)
        self.status_label.setText("Scanning files... This may take a moment.")
        self.tree.clear()
        
        # Run in thread to keep UI responsive
        self.worker = ConflictWorker(self.analyzer, enabled_mods)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.start()

    def on_check_finished(self, conflicts):
        self.run_btn.setEnabled(True)
        self.tree.clear()
        
        if not conflicts:
            self.status_label.setText("No file conflicts found!")
            QMessageBox.information(self, "Result", "No file conflicts detected among enabled mods.")
            return

        self.status_label.setText(f"Found {len(conflicts)} conflicting files.")
        
        # Populate tree
        for file_path, mod_names in sorted(conflicts.items()):
            file_item = QTreeWidgetItem(self.tree)
            file_item.setText(0, file_path)
            file_item.setText(1, f"{len(mod_names)} Mods")
            file_item.setForeground(0, QColor("#ff6b6b")) # Reddish for file
            
            for mod_name in mod_names:
                mod_item = QTreeWidgetItem(file_item)
                mod_item.setText(0, mod_name)
                mod_item.setText(1, "Overwrites")
                mod_item.setForeground(0, QColor("#ddd"))

        self.tree.expandAll()

class EditorListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDrop) # Support internal reordering + drops

    def dropEvent(self, event):
        source = event.source()
        
        # Internal Move
        if source == self:
            super().dropEvent(event)
            return

        # Drop from Library
        if isinstance(source, QListWidget): # Simple check, can be more robust
            item = source.currentItem()
            if item:
                mod_id = item.data(Qt.UserRole)
                if hasattr(self, 'editor_callback'):
                    self.editor_callback(mod_id)
        
        event.accept()

class PlaysetEditorWidget(QWidget):
    def __init__(self, db: LauncherDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.analyzer = ModAnalyzer()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Mod List
        self.mod_list_widget = EditorListWidget()
        self.mod_list_widget.editor_callback = self.handle_library_drop
        self.mod_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.mod_list_widget.setAlternatingRowColors(False)
        layout.addWidget(self.mod_list_widget)

        # Remove Button
        self.remove_btn = QPushButton("Remove Selected Mod")
        self.remove_btn.setStyleSheet("background-color: #dc3545; font-weight: bold;")
        self.remove_btn.clicked.connect(self.remove_selected_mod)
        layout.addWidget(self.remove_btn)
        
        # Shortcut for delete
        self.shortcut_del = QKeySequence(Qt.Key_Delete)
        self.shortcut_backspace = QKeySequence(Qt.Key_Backspace)

    def keyPressEvent(self, event):
        if event.matches(self.shortcut_del) or event.matches(self.shortcut_backspace):
            self.remove_selected_mod()
        else:
            super().keyPressEvent(event)

    def load_mods(self, playset_id):
        mods = self.db.get_mods_for_playset(playset_id)
        self.mod_list_widget.clear()
        
        for mod in mods:
            item = QListWidgetItem(self.mod_list_widget)
            item.setSizeHint(QSize(0, 50))
            
            widget = ModListItemWidget(mod)
            if widget.checkbox:
                widget.checkbox.stateChanged.connect(self.trigger_conflict_check)
            
            item.setData(Qt.UserRole, mod)
            
            self.mod_list_widget.addItem(item)
            self.mod_list_widget.setItemWidget(item, widget)
            
        self.trigger_conflict_check()

    def trigger_conflict_check(self):
        # Gather enabled mods
        enabled_mods = []
        for i in range(self.mod_list_widget.count()):
            item = self.mod_list_widget.item(i)
            widget = self.mod_list_widget.itemWidget(item)
            if widget and widget.is_checked():
                mod = item.data(Qt.UserRole)
                enabled_mods.append(mod)
        
        # Stop existing worker if running
        if self.worker and self.worker.isRunning():
            self.worker.wait() # Or terminate? Wait is safer but might block briefly.
        
        self.worker = ConflictWorker(self.analyzer, enabled_mods)
        self.worker.finished.connect(self.update_conflict_icons)
        self.worker.start()

    def update_conflict_icons(self, conflicts):
        # Create map: mod_name -> list of conflicting mod names (derived from file conflicts)
        mod_conflict_map = {}
        
        for file_path, mod_names in conflicts.items():
            for mod_name in mod_names:
                if mod_name not in mod_conflict_map:
                    mod_conflict_map[mod_name] = set()
                # Add other mods as conflicting with this one
                others = [m for m in mod_names if m != mod_name]
                mod_conflict_map[mod_name].update(others)
                
        # Update UI items
        for i in range(self.mod_list_widget.count()):
            item = self.mod_list_widget.item(i)
            widget = self.mod_list_widget.itemWidget(item)
            mod = item.data(Qt.UserRole)
            name = mod.get('displayName') or mod.get('name') or "Unknown"
            
            if name in mod_conflict_map and widget.is_checked():
                widget.set_conflict_status(list(mod_conflict_map[name]))
            else:
                widget.set_conflict_status([])



    def save_current_order(self, playset_id):
        ordered_mods = []
        for i in range(self.mod_list_widget.count()):
            item = self.mod_list_widget.item(i)
            widget = self.mod_list_widget.itemWidget(item)
            mod = item.data(Qt.UserRole)
            
            if widget:
                mod_data = {
                    'mod_id': mod['mod_id'],
                    'enabled': 1 if widget.is_checked() else 0
                }
                ordered_mods.append(mod_data)
            
        self.db.update_playset_mods(playset_id, ordered_mods)

    def remove_selected_mod(self):
        items = self.mod_list_widget.selectedItems()
        if not items:
            return
            
        item = items[0]
        mod = item.data(Qt.UserRole)
        mod_name = mod.get('displayName') or mod.get('name')
        
        reply = QMessageBox.question(self, 'Remove Mod', 
                                     f"Are you sure you want to remove '{mod_name}' from this playset?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                     
        if reply == QMessageBox.Yes:
            # Get current playset ID from parent window (a bit hacky but works for now)
            main_window = self.window()
            if isinstance(main_window, MainWindow) and main_window.current_playset_id:
                if self.db.remove_mod_from_playset(main_window.current_playset_id, mod['mod_id']):
                    # Refresh list
                    row = self.mod_list_widget.row(item)
                    self.mod_list_widget.takeItem(row)
                    self.trigger_conflict_check() # Re-check conflicts
                    main_window.refresh_current_playset() # Update status/counts
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove mod from database.")

    def handle_library_drop(self, mod_id):
        # Called when item dropped from library
        main_window = self.window()
        if isinstance(main_window, MainWindow) and main_window.current_playset_id:
             if self.db.add_mod_to_playset(main_window.current_playset_id, mod_id):
                # We need to refresh the list fully to get correct order and widget
                main_window.refresh_current_playset()
             else:
                # Likely already exists
                pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CK3 Mod Manager (DB Mode)")
        self.resize(1000, 750)
        
        self.db = LauncherDB()
        self.current_playset_id = None
        self.playsets = []
        
        try:
            self.db.connect()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to connect to launcher database:\n{e}")
            sys.exit(1)

        self.apply_theme()
        self.init_ui()
        self.load_playsets()

    def apply_theme(self):
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        dark_color = QColor(45, 45, 45)
        
        dark_palette.setColor(QPalette.Window, dark_color)
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, dark_color)
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, dark_color)
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        app.setPalette(dark_palette)
        
        app.setStyleSheet("""
            QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
            QListWidget { border: 1px solid #444; border-radius: 4px; padding: 5px; }
            QListWidget::item { border-bottom: 1px solid #333; padding: 5px; }
            QListWidget::item:selected { background-color: #383838; border: 1px solid #2a82da; }
            QFrame { border: none; }
            QPushButton { background-color: #0d6efd; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:pressed { background-color: #0a58ca; }
            QLabel { color: #ddd; }
            QComboBox { background-color: #333; color: white; padding: 5px; border: 1px solid #555; border-radius: 4px; }
            QLineEdit { background-color: #333; color: white; padding: 5px; border: 1px solid #555; border-radius: 4px; }
            QTabWidget::pane { border: 1px solid #444; top: -1px; } 
            QTabBar::tab { background: #333; color: #aaa; padding: 8px 12px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #444; color: white; border-bottom: 2px solid #2a82da; }
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5) # Minimal margin for window edge
        main_layout.setSpacing(5)

        # Header (Common)
        header_layout = QHBoxLayout()
        title_label = QLabel("Playset:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #fff;")
        
        self.playset_combo = QComboBox()
        self.playset_combo.currentIndexChanged.connect(self.on_playset_changed)
        
        self.active_btn = QPushButton("Set Active")
        self.active_btn.setStyleSheet("background-color: #444; border: 1px solid #666;")
        self.active_btn.clicked.connect(self.set_active_playset)

        save_btn = QPushButton("Save Order")
        save_btn.clicked.connect(self.save_mods)
        
        launch_btn = QPushButton("Launch Game")
        launch_btn.setStyleSheet("background-color: #198754; font-weight: bold;")
        launch_btn.clicked.connect(self.launch_game)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.playset_combo, 1)
        header_layout.addWidget(self.active_btn)
        header_layout.addStretch()
        header_layout.addWidget(save_btn)
        header_layout.addWidget(launch_btn)
        main_layout.addLayout(header_layout)

        # Main Content (Split View)
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(4)
        main_layout.addWidget(content_splitter)
        
        # Left Panel: Editor
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 2, 0) # Minimal right margin
        editor_layout.setSpacing(0) # Remove spacing between header and widget
        
        editor_header = QLabel("Active Playset")
        editor_header.setStyleSheet("font-size: 14px; font-weight: bold; margin: 0; padding: 2px 0;")
        editor_layout.addWidget(editor_header)
        
        self.editor_tab = PlaysetEditorWidget(self.db)
        editor_layout.addWidget(self.editor_tab)
        content_splitter.addWidget(editor_container)
        
        # Right Panel: Library
        library_container = QWidget()
        library_layout = QVBoxLayout(library_container)
        library_layout.setContentsMargins(2, 0, 0, 0) # Minimal left margin
        library_layout.setSpacing(0)
        
        library_header = QLabel("Mod Library (Drag to Add)")
        library_header.setStyleSheet("font-size: 14px; font-weight: bold; margin: 0; padding: 2px 0;")
        library_layout.addWidget(library_header)
        
        self.library_tab = ModLibraryWidget(self.db)
        self.library_tab.mod_added.connect(self.refresh_current_playset)
        library_layout.addWidget(self.library_tab)
        content_splitter.addWidget(library_container)
        
        content_splitter.setStretchFactor(0, 6)
        content_splitter.setStretchFactor(1, 4)

        # Status Bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        self.statusBar().addWidget(self.status_label)

    def load_playsets(self):
        self.playsets = self.db.get_playsets()
        self.playset_combo.blockSignals(True)
        self.playset_combo.clear()
        
        active_index = 0
        for i, ps in enumerate(self.playsets):
            name = ps['name']
            if ps.get('isActive'):
                name += " (Active)"
                active_index = i
            self.playset_combo.addItem(name, ps['id'])
            
        self.playset_combo.blockSignals(False)
        self.playset_combo.setCurrentIndex(active_index)
        
        if self.playsets:
            self.current_playset_id = self.playsets[active_index]['id']
            self.refresh_current_playset()

    def on_playset_changed(self, index):
        if index < 0: 
            return
        playset_id = self.playset_combo.itemData(index)
        self.current_playset_id = playset_id
        self.refresh_current_playset()

    def refresh_current_playset(self):
        if self.current_playset_id:
            self.editor_tab.load_mods(self.current_playset_id)
            mod_count = self.editor_tab.mod_list_widget.count()
            self.status_label.setText(f"Loaded {mod_count} mods for playset.")

    def set_active_playset(self):
        if not self.current_playset_id: 
            return
        self.db.set_active_playset(self.current_playset_id)
        self.load_playsets()
        self.status_label.setText("Active playset updated.")

    def save_mods(self):
        if not self.current_playset_id:
            return
        self.editor_tab.save_current_order(self.current_playset_id)
        self.status_label.setText("Playset order and state saved to database.")

    def launch_game(self):
        try:
            # Steam protocol URL for CK3 (App ID 1158310)
            cmd = ["open", "steam://run/1158310"]
            subprocess.run(cmd, check=True)
            self.status_label.setText("Launching Crusader Kings 3 via Steam...")
        except subprocess.CalledProcessError as e:
             QMessageBox.critical(self, "Launch Error", f"Failed to open Steam: {e}")
        except FileNotFoundError:
             QMessageBox.critical(self, "Launch Error", "Could not find 'open' command. Are you on macOS?")

def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())