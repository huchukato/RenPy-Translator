#!/usr/bin/env python3
"""
Ren'Py Translator - Extractor Module
Gestisce l'estrazione dei file .rpa e la decompilazione dei file .rpyc
"""

import os
import sys
import subprocess
from pathlib import Path


class TRExtractor:
    def __init__(self, game_path):
        self.game_path = Path(game_path)
        self.game_dir = self._find_game_dir()
        self.script_dir = Path(__file__).parent
        self.unren_tools = self.script_dir / "UnRen Tools"

    def _find_game_dir(self):
        if self.game_path.suffix == '.app':
            d = self.game_path / "Contents" / "Resources" / "autorun" / "game"
            if d.exists():
                return d
        d = self.game_path / "game"
        if d.exists():
            return d
        return self.game_path

    def extract_rpa_files(self, progress_callback=None):
        rpa_files = list(self.game_dir.glob("*.rpa"))
        if not rpa_files:
            print("Nessun file .rpa trovato")
            return True
        print(f"Trovati {len(rpa_files)} file .rpa")
        rpatool = self.unren_tools / "rpatool"
        for i, rpa in enumerate(rpa_files):
            if progress_callback:
                progress_callback(i + 1, len(rpa_files))
            print(f"Estrazione {rpa.name}...")
            try:
                r = subprocess.run(
                    [sys.executable, str(rpatool), '-x', str(rpa), '-o', str(self.game_dir)],
                    capture_output=True, text=True
                )
                if r.returncode != 0:
                    print(f"Errore: {r.stderr}")
                    return False
            except Exception as e:
                print(f"Errore estrazione: {e}")
                return False
        print("Estrazione completata")
        return True

    def decompile_rpyc_files(self, progress_callback=None):
        skip = {'gui', 'screens', 'options', 'images'}
        rpyc_files = [
            f for f in self.game_dir.rglob("*.rpyc")
            if not any(x in f.name.lower() for x in skip)
            and 'tl' not in f.parts
        ]
        if not rpyc_files:
            print("Nessun file .rpyc trovato")
            return True
        print(f"Trovati {len(rpyc_files)} file .rpyc")
        decompiler_dir = self.unren_tools / "decompiler"
        if str(decompiler_dir) not in sys.path:
            sys.path.insert(0, str(decompiler_dir))
        unrpyc = self.unren_tools / "unrpyc.py"
        batch_size = 50
        for i in range(0, len(rpyc_files), batch_size):
            batch = rpyc_files[i:i + batch_size]
            if progress_callback:
                progress_callback(i + len(batch), len(rpyc_files))
            try:
                r = subprocess.run(
                    [sys.executable, str(unrpyc), '-c'] + [str(f) for f in batch],
                    capture_output=True, text=True, cwd=str(self.game_dir)
                )
                if r.returncode != 0:
                    print(f"Errore decompilazione: {r.stderr}")
                    return False
            except Exception as e:
                print(f"Errore: {e}")
                return False
        print("Decompilazione completata")
        return True

    def get_rpy_files(self):
        skip = {'gui', 'screens', 'options', 'images'}
        return [
            f for f in self.game_dir.rglob("*.rpy")
            if not any(x in f.name.lower() for x in skip)
            and 'wtmod' not in f.parts
            and 'tl' not in f.parts
        ]
