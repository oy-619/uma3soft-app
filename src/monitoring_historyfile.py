# -*- coding: utf-8 -*-
"""
Monitoring History File - Background Process

STEP 1: System Overview
- Background monitoring of conversation history files
- Automatic data processing and synchronization
- Integration with ChromaDB for persistent storage
- Real-time change detection and processing

STEP 2: Core Features
- File system monitoring using watchdog
- Conversation data extraction and parsing
- Automatic ChromaDB updates
- Error handling and logging

STEP 3: Background Processing
- Runs as independent background process
- Communicates with main system via file/database
- Handles large conversation datasets
- Maintains data integrity and consistency
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add current directory and parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Debug info only when running as main
if __name__ == "__main__":
    print(f"[MONITOR] Starting monitoring from: {current_dir}")
    print(f"[MONITOR] Parent directory: {parent_dir}")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    if __name__ == "__main__":
        print("[MONITOR] Watchdog library available")
except ImportError:
    if __name__ == "__main__":
        print("[WARNING] Watchdog not available - using polling mode")
    WATCHDOG_AVAILABLE = False

try:
    # Try multiple import paths
    RAG_AVAILABLE = False

    # Method 1: Direct import
    try:
        from uma3_rag_engine import Uma3RAGEngine
        if __name__ == "__main__":
            print("[MONITOR] Successfully imported Uma3RAGEngine (direct)")
        RAG_AVAILABLE = True
    except ImportError:
        pass

    # Method 2: Import from src
    if not RAG_AVAILABLE:
        try:
            from src.uma3_rag_engine import Uma3RAGEngine
            if __name__ == "__main__":
                print("[MONITOR] Successfully imported Uma3RAGEngine (src)")
            RAG_AVAILABLE = True
        except ImportError:
            pass

    # Method 3: Try ChromaDB improver
    if not RAG_AVAILABLE:
        try:
            from uma3_chroma_improver import Uma3ChromaDBImprover as Uma3RAGEngine
            if __name__ == "__main__":
                print("[MONITOR] Successfully imported Uma3ChromaDBImprover as RAGEngine")
            RAG_AVAILABLE = True
        except ImportError:
            pass

    if not RAG_AVAILABLE:
        if __name__ == "__main__":
            print("[WARNING] RAG components not available - monitoring will run without RAG integration")
        # Create a dummy RAG engine class for testing
        class DummyRAGEngine:
            def add_documents(self, texts, metadatas):
                if __name__ == "__main__":
                    print(f"[DUMMY RAG] Would add {len(texts)} documents")
                return True
            def add_texts(self, texts, metadatas):
                if __name__ == "__main__":
                    print(f"[DUMMY RAG] Would add {len(texts)} texts")
                return True

        Uma3RAGEngine = DummyRAGEngine
        RAG_AVAILABLE = True
        if __name__ == "__main__":
            print("[MONITOR] Using dummy RAG engine for testing")

except Exception as e:
    if __name__ == "__main__":
        print(f"[WARNING] Error importing RAG components: {e}")
    RAG_AVAILABLE = False
# === STEP 4: Configuration ===
class MonitoringConfig:
    """
    STEP 4.1: Monitoring configuration settings
    """
    def __init__(self):
        # Set paths relative to the current script location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        self.watch_directory = os.path.join(parent_dir, "logs")
        self.chroma_directory = os.path.join(parent_dir, "db", "chroma_store")
        self.conversation_db = os.path.join(parent_dir, "db", "conversation_history.db")
        self.polling_interval = 10  # seconds (reduced for more responsive monitoring)
        self.log_file = os.path.join(parent_dir, "monitoring.log")

        # File patterns to monitor (expanded for LINE Bot logs)
        self.monitor_patterns = [
            "*.log",
            "conversation_*.json",
            "history_*.txt",
            "chat_history_*.json",
            "line_chat_*.log",
            "debug_*.log"
        ]

        if __name__ == "__main__":
            print(f"[CONFIG] Watch directory: {self.watch_directory}")
            print(f"[CONFIG] ChromaDB directory: {self.chroma_directory}")
            print(f"[CONFIG] Polling interval: {self.polling_interval}s")


# === STEP 5: File System Event Handler ===
class ConversationFileHandler(FileSystemEventHandler):
    """
    STEP 5.1: Handle file system events for conversation files
    """

    def __init__(self, config: MonitoringConfig):
        super().__init__()
        self.config = config
        self.rag_engine = None
        self.history_manager = None

        # Initialize components if available
        if RAG_AVAILABLE:
            try:
                # Simple RAG engine initialization
                try:
                    self.rag_engine = Uma3RAGEngine()
                    if __name__ == "__main__":
                        print("[INIT] RAG engine initialized successfully")
                except Exception as rag_e:
                    if __name__ == "__main__":
                        print(f"[WARNING] RAG engine init failed: {rag_e}")
                    # Use dummy engine
                    class DummyRAGEngine:
                        def add_documents(self, texts, metadatas):
                            if __name__ == "__main__":
                                print(f"[DUMMY] Would add {len(texts)} documents")
                            return True
                        def add_texts(self, texts, metadatas):
                            if __name__ == "__main__":
                                print(f"[DUMMY] Would add {len(texts)} texts")
                            return True
                    self.rag_engine = DummyRAGEngine()
                    if __name__ == "__main__":
                        print("[INIT] Using dummy RAG engine")

                # History manager is optional
                self.history_manager = None
                if __name__ == "__main__":
                    print("[INFO] History manager disabled for stability")

            except Exception as e:
                if __name__ == "__main__":
                    print(f"[ERROR] Failed to initialize components: {e}")
                    print("[INFO] Continuing without RAG engine")

    def on_modified(self, event):
        """
        STEP 5.2: Handle file modification events
        """
        if event.is_directory:
            return

        file_path = event.src_path
        if self._should_process_file(file_path):
            print(f"[MONITOR] Processing modified file: {file_path}")
            self._process_conversation_file(file_path)

    def on_created(self, event):
        """
        STEP 5.3: Handle file creation events
        """
        if event.is_directory:
            return

        file_path = event.src_path
        if self._should_process_file(file_path):
            print(f"[MONITOR] Processing new file: {file_path}")
            self._process_conversation_file(file_path)

    def _should_process_file(self, file_path: str) -> bool:
        """
        STEP 5.4: Check if file should be processed
        """
        file_name = os.path.basename(file_path)
        for pattern in self.config.monitor_patterns:
            if pattern.replace("*", "") in file_name:
                return True
        return False

    def _process_conversation_file(self, file_path: str):
        """
        STEP 5.5: Process conversation file content
        """
        try:
            if not os.path.exists(file_path):
                print(f"[MONITOR] File does not exist: {file_path}")
                return

            print(f"[MONITOR] Processing file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print(f"[MONITOR] File is empty: {file_path}")
                return

            print(f"[MONITOR] File content length: {len(content)} characters")

            # Parse conversation data
            conversations = self._parse_conversation_content(content)
            print(f"[MONITOR] Parsed {len(conversations)} conversations")

            if conversations and self.rag_engine:
                # Add to RAG engine
                texts = [conv.get('text', '') for conv in conversations if conv.get('text') and len(conv.get('text', '').strip()) > 0]
                metadatas = [{'source': file_path, 'timestamp': conv.get('timestamp', datetime.now().isoformat())}
                           for conv in conversations if conv.get('text') and len(conv.get('text', '').strip()) > 0]

                if texts:
                    try:
                        # Try different methods to add documents
                        if hasattr(self.rag_engine, 'add_documents'):
                            success = self.rag_engine.add_documents(texts, metadatas)
                        elif hasattr(self.rag_engine, 'add_texts'):
                            success = self.rag_engine.add_texts(texts, metadatas)
                        else:
                            print("[MONITOR] RAG engine doesn't have recognized add method")
                            return

                        if success:
                            print(f"[MONITOR] Successfully added {len(texts)} conversations to RAG engine")
                        else:
                            print(f"[MONITOR] Failed to add conversations to RAG engine")
                    except Exception as rag_error:
                        print(f"[ERROR] RAG engine error: {rag_error}")
                else:
                    print("[MONITOR] No valid texts to add")
            elif not self.rag_engine:
                print("[MONITOR] RAG engine not available - skipping document addition")
            else:
                print("[MONITOR] No conversations to process")

        except UnicodeDecodeError as e:
            print(f"[ERROR] Unicode decode error in file {file_path}: {e}")
            # Try with different encodings
            for encoding in ['utf-8-sig', 'shift_jis', 'cp932']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"[MONITOR] Successfully read with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
        except Exception as e:
            print(f"[ERROR] Failed to process file {file_path}: {e}")
            import traceback
            traceback.print_exc()

    def _parse_conversation_content(self, content: str) -> List[Dict]:
        """
        STEP 5.6: Parse conversation content from various formats
        """
        conversations = []

        try:
            # Try JSON format first
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                if isinstance(data, list):
                    conversations = data
                elif isinstance(data, dict):
                    conversations = [data]
            else:
                # Try plain text format
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10:  # Filter out short lines
                        conversations.append({
                            'text': line,
                            'timestamp': datetime.now().isoformat()
                        })

        except json.JSONDecodeError:
            # Fallback to line-by-line processing
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:
                    conversations.append({
                        'text': line,
                        'timestamp': datetime.now().isoformat()
                    })

        return conversations


# === STEP 6: Main Monitoring Class ===
class ConversationMonitor:
    """
    STEP 6.1: Main monitoring system
    """

    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.observer = None
        self.event_handler = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self):
        """
        STEP 6.2: Start file monitoring
        """
        print(f"[MONITOR] Starting conversation file monitoring...")
        print(f"[MONITOR] Watch directory: {self.config.watch_directory}")
        print(f"[MONITOR] Monitor patterns: {self.config.monitor_patterns}")

        # Create watch directory if it doesn't exist
        try:
            os.makedirs(self.config.watch_directory, exist_ok=True)
            print(f"[MONITOR] Created/verified watch directory: {self.config.watch_directory}")
        except Exception as e:
            print(f"[ERROR] Failed to create watch directory: {e}")
            return

        # Check if directory exists and is readable
        if not os.path.exists(self.config.watch_directory):
            print(f"[ERROR] Watch directory does not exist: {self.config.watch_directory}")
            return

        if not os.access(self.config.watch_directory, os.R_OK):
            print(f"[ERROR] Watch directory is not readable: {self.config.watch_directory}")
            return

        print(f"[MONITOR] Watchdog available: {WATCHDOG_AVAILABLE}")
        print(f"[MONITOR] RAG available: {RAG_AVAILABLE}")

        if WATCHDOG_AVAILABLE:
            self._start_watchdog_monitoring()
        else:
            self._start_polling_monitoring()

    def _start_watchdog_monitoring(self):
        """
        STEP 6.3: Start watchdog-based monitoring
        """
        try:
            self.event_handler = ConversationFileHandler(self.config)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.config.watch_directory,
                recursive=True
            )

            self.observer.start()
            print("[MONITOR] Watchdog monitoring started")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("[MONITOR] Stopping monitoring...")
                self.observer.stop()

            self.observer.join()

        except Exception as e:
            print(f"[ERROR] Watchdog monitoring failed: {e}")
            self._start_polling_monitoring()

    def _start_polling_monitoring(self):
        """
        STEP 6.4: Start polling-based monitoring
        """
        print("[MONITOR] Starting polling-based monitoring")
        processed_files = set()

        try:
            while True:
                try:
                    # Scan for new files
                    watch_path = Path(self.config.watch_directory)
                    if watch_path.exists():
                        for file_path in watch_path.rglob("*"):
                            if file_path.is_file():
                                file_str = str(file_path)
                                if (file_str not in processed_files and
                                    self._should_process_file(file_str)):
                                    print(f"[MONITOR] Processing: {file_str}")
                                    self._process_file(file_str)
                                    processed_files.add(file_str)

                    time.sleep(self.config.polling_interval)

                except KeyboardInterrupt:
                    print("[MONITOR] Stopping polling monitoring...")
                    break
                except Exception as e:
                    print(f"[ERROR] Polling error: {e}")
                    time.sleep(self.config.polling_interval)

        except Exception as e:
            print(f"[ERROR] Monitoring failed: {e}")

    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        file_name = os.path.basename(file_path)
        for pattern in self.config.monitor_patterns:
            if pattern.replace("*", "") in file_name:
                return True
        return False

    def _process_file(self, file_path: str):
        """Process individual file"""
        try:
            if not RAG_AVAILABLE:
                return

            handler = ConversationFileHandler(self.config)
            handler._process_conversation_file(file_path)

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")


# === STEP 7: Entry Point ===
def main():
    """
    STEP 7.1: Main entry point for monitoring process
    """
    print("=== Uma3 Conversation File Monitor ===")
    print(f"Started at: {datetime.now()}")

    try:
        config = MonitoringConfig()
        monitor = ConversationMonitor(config)
        monitor.start_monitoring()

    except KeyboardInterrupt:
        print("\n[MONITOR] Monitoring stopped by user")
    except Exception as e:
        print(f"[ERROR] Monitor failed: {e}")
    finally:
        print(f"[MONITOR] Stopped at: {datetime.now()}")


if __name__ == "__main__":
    main()
