try:
    from . import (
        colors_manager,
        fonts_manager,
    )
except ImportError:
    import colors_manager
    import fonts_manager

import importlib.util
import os
import types
import uuid
import weakref


def _offset(initial, amount):
    if colors_manager.check_full_white_or_black(initial) == -1:
        return initial.brighten(amount)
    else:
        return initial.darken(amount)


class DefaultRef:
    """Reference to a named default value managed by defaults.py."""

    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return f"DefaultRef({self.name!r})"


class StyleRef:
    """Reference to a named style profile managed by defaults.py."""

    def __init__(self, manager, name):
        self._manager = manager
        self.name = str(name)

    def resolve(self):
        return self._manager.resolve_style(self.name)

    def __repr__(self):
        return f"StyleRef({self.name!r})"


class new:
    def __init__(self, file=None):
        self._defaults = {}
        self._styles = {}
        self._style_cache = {}
        self._style_refs = {}
        self._subscribers = weakref.WeakSet()
        self._source = None
        self.load(file)

    def _builtin_profile(self):
        return {
            "defaults": {
                "default_text_color": "black",
                "default_fill": "white",
                "default_border": "black",
                "default_font": "default",
                "default_window_background": "#FFFFFF",
            },
            "styles": {},
        }

    def _normalize_profile(self, raw_profile):
        profile = {}
        if raw_profile is None:
            profile = {}
        elif isinstance(raw_profile, dict):
            profile = dict(raw_profile)
        elif isinstance(raw_profile, types.ModuleType):
            if hasattr(raw_profile, "PROFILE"):
                profile = dict(getattr(raw_profile, "PROFILE"))
            else:
                profile = {}
                if hasattr(raw_profile, "DEFAULTS"):
                    profile["defaults"] = dict(getattr(raw_profile, "DEFAULTS"))
                elif hasattr(raw_profile, "defaults"):
                    profile["defaults"] = dict(getattr(raw_profile, "defaults"))
                if hasattr(raw_profile, "STYLES"):
                    profile["styles"] = dict(getattr(raw_profile, "STYLES"))
                elif hasattr(raw_profile, "styles"):
                    profile["styles"] = dict(getattr(raw_profile, "styles"))
                if hasattr(raw_profile, "THEME"):
                    theme = getattr(raw_profile, "THEME")
                    if isinstance(theme, dict):
                        profile.setdefault("defaults", {}).update(theme)
        else:
            raise TypeError(
                "Defaults file must be None, a dict, a module, or a python file path."
            )

        defaults_data = dict(profile.get("defaults", {}))
        styles_data = dict(profile.get("styles", {}))

        # Also support flat dict modules where top-level default_* keys are provided.
        for key, value in profile.items():
            if key.startswith("default_"):
                defaults_data[key] = value

        merged_defaults = dict(self._builtin_profile()["defaults"])
        merged_defaults.update(defaults_data)

        return {"defaults": merged_defaults, "styles": styles_data}

    def _load_module_from_path(self, path):
        module_path = os.path.abspath(path)
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Defaults file not found: {module_path}")
        module_name = f"nebulatk_defaults_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load defaults module from: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _coerce_default_value(self, key, value):
        if isinstance(value, DefaultRef):
            return value
        if key == "default_font":
            return fonts_manager.Font(value)
        if key.startswith("default_"):
            if (
                "color" in key
                or "background" in key
                or key.endswith("fill")
                or key.endswith("border")
                or key.endswith("image")
            ):
                return colors_manager.Color(value)
        return value

    def _refresh_default_attributes(self):
        for key, value in self._defaults.items():
            setattr(self, key, value)

    def _resolve_style_recursive(self, style_name, stack):
        if style_name in self._style_cache:
            return dict(self._style_cache[style_name])
        if style_name not in self._styles:
            raise AttributeError(f"Unknown style: {style_name}")
        if style_name in stack:
            path = " -> ".join(stack + [style_name])
            raise ValueError(f"Cyclic style inheritance detected: {path}")

        entry = self._styles[style_name]
        if not isinstance(entry, dict):
            raise TypeError(f"Style '{style_name}' must be a dict.")

        extends = entry.get("extends")
        merged = {}
        stack = stack + [style_name]
        if extends:
            parents = extends if isinstance(extends, (list, tuple)) else [extends]
            for parent in parents:
                merged.update(self._resolve_style_recursive(str(parent), stack))

        for key, value in entry.items():
            if key == "extends":
                continue
            merged[key] = value

        self._style_cache[style_name] = dict(merged)
        return merged

    def resolve_style(self, style_name):
        return self._resolve_style_recursive(str(style_name), [])

    def list_styles(self):
        return sorted(self._styles.keys())

    def ref(self, name):
        return DefaultRef(name)

    def style(self, name):
        style_name = str(name)
        if style_name not in self._styles:
            raise AttributeError(f"Unknown style: {style_name}")
        if style_name not in self._style_refs:
            self._style_refs[style_name] = StyleRef(self, style_name)
        return self._style_refs[style_name]

    def get_default(self, name):
        key = str(name)
        if key not in self._defaults:
            raise AttributeError(f"Unknown default: {key}")
        return self._defaults[key]

    def subscribe(self, widget):
        if widget is not None:
            self._subscribers.add(widget)

    def unsubscribe(self, widget):
        if widget is not None and widget in self._subscribers:
            self._subscribers.remove(widget)

    def _notify_subscribers(self):
        for widget in list(self._subscribers):
            if hasattr(widget, "_on_defaults_changed"):
                widget._on_defaults_changed()

    def _coerce_source(self, file_or_module):
        if file_or_module is None:
            return None
        if isinstance(file_or_module, str):
            return self._load_module_from_path(file_or_module)
        return file_or_module

    def load(self, file_or_module=None, notify=False):
        source = self._coerce_source(file_or_module)
        profile = self._normalize_profile(source)
        self._source = file_or_module
        self._defaults = {
            key: self._coerce_default_value(key, value)
            for key, value in profile["defaults"].items()
        }
        self._styles = dict(profile["styles"])
        self._style_cache = {}
        self._style_refs = {}
        self._refresh_default_attributes()
        if notify:
            self._notify_subscribers()
        return self

    def switch(self, file_or_module):
        return self.load(file_or_module, notify=True)

    def __getattr__(self, name):
        if name in self._defaults:
            return self._defaults[name]
        if name in self._styles:
            return self.style(name)
        raise AttributeError(name)
