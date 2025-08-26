from __future__ import annotations
import pkgutil, inspect
import ux_analyzer_lc.prompts as prompts_pkg

def test_prompts_have_format_instructions():
    missing = []
    for _, modname, _ in pkgutil.iter_modules(prompts_pkg.__path__):
        mod = __import__(f"{prompts_pkg.__name__}.{modname}", fromlist=["*"])
        for obj_name, obj in inspect.getmembers(mod):
            if obj_name.startswith("PROMPT"):
                tpl = getattr(mod, obj_name)
                if isinstance(tpl, str) and "{format_instructions}" not in tpl:
                    missing.append(f"{modname}.{obj_name}")
    assert not missing, f"Нет {{format_instructions}} в: {missing}"