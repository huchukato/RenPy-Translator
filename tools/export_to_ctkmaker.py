"""Export translator_tool.py UI layout to a CTkMaker project folder.

Generates project.json + assets/pages/*.ctkproj so the user can edit the
Ren'Py Translator GUI visually in CTkMaker.

Usage:
    python tools/export_to_ctkmaker.py
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "translator_tool.py"
OUTPUT = Path("/Volumes/NVME/dev-ai/CTMaker")

DEFAULT_SIZES = {
    "CTkFrame": (200, 120),
    "CTkLabel": (80, 28),
    "CTkButton": (120, 32),
    "CTkEntry": (180, 28),
    "CTkComboBox": (130, 28),
    "CTkRadioButton": (100, 22),
    "CTkProgressBar": (200, 16),
    "CTkTabview": (400, 250),
    "CTkTextbox": (200, 80),
    "CTkCheckBox": (120, 24),
    "CTkSwitch": (80, 24),
    "CTkOptionMenu": (120, 28),
    "CTkSegmentedButton": (200, 28),
    "CTkSlider": (160, 22),
}


def literal_value(node: ast.AST) -> Any:
    """Return a JSON-serialisable value from an AST expression."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [literal_value(e) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(literal_value(e) for e in node.elts)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{literal_value(node.value)}.{node.attr}"
    return ast.unparse(node)


def unpack_padding(value: Any) -> tuple[int, int]:
    """Convert padx/pady int or tuple into (start, end)."""
    if isinstance(value, (list, tuple)):
        if len(value) == 2:
            return int(value[0]), int(value[1])
        return int(value[0]), int(value[0])
    if isinstance(value, int):
        return value, value
    return 0, 0


def kwarg(call: ast.Call, name: str) -> Any:
    for kw in call.keywords:
        if kw.arg == name:
            return literal_value(kw.value)
    return None


def extract_pack_opts(call: ast.Call) -> dict:
    """Parse .pack(...) options from a Call AST node."""
    out = {
        "side": "top",
        "fill": "none",
        "expand": False,
        "padx": (0, 0),
        "pady": (0, 0),
        "anchor": "center",
    }
    for kw in call.keywords:
        val = literal_value(kw.value)
        if kw.arg == "side":
            out["side"] = val
        elif kw.arg == "fill":
            out["fill"] = val
        elif kw.arg == "expand":
            out["expand"] = bool(val)
        elif kw.arg == "padx":
            out["padx"] = unpack_padding(val)
        elif kw.arg == "pady":
            out["pady"] = unpack_padding(val)
        elif kw.arg == "anchor":
            out["anchor"] = val
    return out


class LayoutNode:
    """Temporary tree node while parsing source."""
    def __init__(self, var: str, widget_type: str, props: dict):
        self.var = var
        self.widget_type = widget_type
        self.props = props
        self.children: list[LayoutNode] = []
        self.pack: dict = {}
        self.next_x = 0
        self.next_y = 0


def make_ctkmaker_node(node: LayoutNode, x: int, y: int) -> dict:
    """Convert a LayoutNode to a CTkMaker WidgetNode dict."""
    props = dict(node.props)
    props.setdefault("x", x)
    props.setdefault("y", y)
    w, h = DEFAULT_SIZES.get(node.widget_type, (120, 32))
    props.setdefault("width", w)
    props.setdefault("height", h)
    result = {
        "id": str(uuid.uuid4()),
        "name": node.var or node.widget_type,
        "widget_type": node.widget_type,
        "properties": props,
        "visible": True,
        "locked": False,
        "children": [make_ctkmaker_node(c, c.props.get("x", 0), c.props.get("y", 0)) for c in node.children],
    }
    if node.widget_type == "CTkFrame":
        result["properties"].setdefault("layout_type", "place")
    return result


def class_methods(tree: ast.Module) -> dict[str, list[ast.stmt]]:
    """Return a mapping class_name -> list of body statements."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            out[node.name] = node.body
    return out


def find_builder(class_body: list[ast.stmt]) -> list[ast.stmt] | None:
    """Locate _build_ui or __init__ method body."""
    for item in class_body:
        if isinstance(item, ast.FunctionDef) and item.name == "_build_ui":
            return item.body
    for item in class_body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            return item.body
    return None


def parse_builder_statements(stmts: list[ast.stmt]) -> LayoutNode:
    """Walk builder statements and build a layout tree."""
    root = LayoutNode("root", "CTkFrame", {"fg_color": "transparent", "width": 1200, "height": 800})
    var_to_node: dict[str, LayoutNode] = {"self": root}
    last_var: str | None = None
    tabview_tabs: dict[str, str] = {}
    current_tab: str | None = None

    def _target_name(target: ast.AST) -> str | None:
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            return target.attr
        return None

    def _lookup_var(expr: ast.AST) -> str | None:
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name) and expr.value.id == "self":
            return expr.attr
        return None

    for stmt in stmts:
        # CTk assignments: var = ctk.CTk...(...) or self.x = ctk.CTk...(...)
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                name = _target_name(target)
                if not name:
                    continue
                value = stmt.value
                if isinstance(value, ast.Call):
                    wt, props = call_to_props(value)
                    if wt:
                        parent_var = props.pop("_parent", "self")
                        node = LayoutNode(name, wt, props)
                        parent = var_to_node.get(parent_var, root)
                        parent.children.append(node)
                        var_to_node[name] = node
                        last_var = name
                        # Detect tab additions: tabs.add("name")
                        if wt == "CTkTabview" and "tab_names" in props:
                            tabview_tabs[name] = props["tab_names"]

        # Anonymous chained ctk.CTk...(...).pack(...)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            func = call.func
            if isinstance(func, ast.Attribute) and func.attr == "pack" and isinstance(func.value, ast.Call):
                inner = func.value
                wt, props = call_to_props(inner)
                if wt:
                    parent_var = props.pop("_parent", "self")
                    parent = var_to_node.get(parent_var, root)
                    node = LayoutNode(f"{wt}_{len(var_to_node)}", wt, props)
                    node.pack = extract_pack_opts(call)
                    parent.children.append(node)
                    last_var = node.var

            # var.pack(...) or self.x.pack(...)
            elif isinstance(func, ast.Attribute) and func.attr == "pack":
                var = _lookup_var(func.value)
                if var:
                    node = var_to_node.get(var)
                    if node:
                        node.pack = extract_pack_opts(call)

    # Second pass: assign positions from pack options
    layout_tree(root)
    return root


def call_to_props(call: ast.Call) -> tuple[str | None, dict]:
    """Convert a ctk.CTk*(parent, ...) call to (widget_type, properties)."""
    if not isinstance(call.func, ast.Attribute):
        return None, {}
    attr = call.func
    if not (isinstance(attr.value, ast.Name) and attr.value.id == "ctk"):
        return None, {}
    widget_type = f"CTk{attr.attr[3:].capitalize()}" if attr.attr.startswith("ctk") else attr.attr
    if attr.attr.startswith("CTk"):
        widget_type = attr.attr
    elif attr.attr.startswith("ctk_"):
        widget_type = f"CTk{''.join(p.capitalize() for p in attr.attr[4:].split('_'))}"
    else:
        return None, {}

    args = call.args
    kwargs = call.keywords
    props: dict[str, Any] = {}
    parent_var = "self"
    if args and isinstance(args[0], ast.Name):
        parent_var = args[0].id

    # Map relevant kwargs to CTkMaker properties
    for kw in kwargs:
        key = kw.arg
        val = literal_value(kw.value)
        if key == "text" and isinstance(val, str):
            props["text"] = val
        elif key == "placeholder_text" and isinstance(val, str):
            props["placeholder_text"] = val
        elif key == "values" and isinstance(val, list):
            props["values"] = "\n".join(str(v) for v in val)
            if val:
                props["initial_value"] = str(val[0])
        elif key == "width" and isinstance(val, (int, float)):
            props["width"] = int(val)
        elif key == "height" and isinstance(val, (int, float)):
            props["height"] = int(val)
        elif key == "fg_color":
            props["fg_color"] = resolve_color(val)
        elif key == "text_color":
            props["text_color"] = resolve_color(val)
        elif key == "image":
            # image is not a string here, skip
            pass
        elif key == "command" and isinstance(val, str):
            props["description"] = f"command: {val}"
        elif key == "state":
            props["button_enabled"] = (val != "disabled")

    props["_parent"] = parent_var
    return widget_type, props


def resolve_color(val: Any) -> str | None:
    """Map a python expression (COLOR_* variable or string) to a colour."""
    if isinstance(val, str) and val.startswith("#"):
        return val
    if isinstance(val, str) and val.startswith("COLOR_"):
        return None  # we do not run the module, leave token
    if isinstance(val, str):
        return val
    return None


def layout_tree(node: LayoutNode, start_x: int = 0, start_y: int = 0) -> None:
    """Compute x/y for children using pack-style placement inside the parent."""
    cx, cy = 0, 0
    for child in node.children:
        pack = child.pack
        side = pack.get("side", "top")
        fill = pack.get("fill", "none")
        padx_start, padx_end = pack.get("padx", (0, 0))
        pady_start, pady_end = pack.get("pady", (0, 0))
        w = child.props.get("width", DEFAULT_SIZES.get(child.widget_type, (120, 32))[0])
        h = child.props.get("height", DEFAULT_SIZES.get(child.widget_type, (120, 32))[1])
        if fill in ("x", "both"):
            w = node.props.get("width", w)
        if fill in ("y", "both"):
            h = node.props.get("height", h)

        if side in ("left", "right"):
            child.props["x"] = cx + padx_start
            child.props["y"] = pady_start
            cx += w + padx_start + padx_end
        else:
            child.props["x"] = padx_start
            child.props["y"] = cy + pady_start
            cy += h + pady_start + pady_end

        layout_tree(child)


def build_document(class_name: str, body: list[ast.stmt], is_toplevel: bool = False) -> dict:
    root = parse_builder_statements(body)
    widgets = [make_ctkmaker_node(c, c.props.get("x", 0), c.props.get("y", 0)) for c in root.children]
    return {
        "id": str(uuid.uuid4()),
        "name": class_name if not is_toplevel else f"{class_name} Dialog",
        "width": root.props.get("width", 1200),
        "height": root.props.get("height", 800),
        "canvas_x": 0,
        "canvas_y": 0,
        "window_properties": {
            "fg_color": "transparent",
            "resizable_x": True,
            "resizable_y": True,
            "frameless": False,
            "grid_style": "dots",
            "grid_color": "#555555",
            "grid_spacing": 20,
            "layout_type": "place",
            "alignment_lines_enabled": True,
            "snap_enabled": True,
        },
        "is_toplevel": is_toplevel,
        "widgets": widgets,
    }


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(text)

    classes = class_methods(tree)
    docs = []
    for name, body in classes.items():
        if name == "TranslatorApp":
            stmts = find_builder(body)
            if stmts:
                docs.append(build_document("Main Window", stmts, is_toplevel=False))
        elif name.endswith("Dialog") and name != "Dialog":
            stmts = find_builder(body)
            if stmts:
                docs.append(build_document(name, stmts, is_toplevel=True))
    docs.sort(key=lambda d: (0 if d["name"] == "Main Window" else 1, d["name"]))

    if not docs:
        raise SystemExit("No buildable classes found in translator_tool.py")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "assets" / "images").mkdir(parents=True, exist_ok=True)

    # Copy assets
    for img in (REPO_ROOT / "img").iterdir():
        if img.is_file():
            shutil.copy2(img, OUTPUT / "assets" / "images" / img.name)

    # CTkMaker opens a single .ctkproj containing multiple documents
    project_file = OUTPUT / "RenPy Translator.ctkproj"
    project_file.write_text(
        json.dumps(
            {
                "version": 2,
                "active_document": docs[0]["id"],
                "documents": docs,
                "variables": [],
                "name": "RenPy Translator",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Exported {len(docs)} document(s) to {project_file}")


if __name__ == "__main__":
    main()
