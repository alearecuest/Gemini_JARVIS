import os
import importlib.util
import inspect

class PluginManager:
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.tools = []
        self.tool_map = {}

    def cargar_plugins(self):
        """Escanea la carpeta plugins/ y registra automáticamente las herramientas."""
        self.tools.clear()
        self.tool_map.clear()

        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            return []

        for archivo in sorted(os.listdir(self.plugins_dir)):
            if archivo.endswith(".py") and not archivo.startswith("__"):
                ruta_completa = os.path.join(self.plugins_dir, archivo)
                nombre_modulo = archivo[:-3]
                try:
                    self._cargar_modulo(nombre_modulo, ruta_completa)
                except Exception as e:
                    print(f"   [!] Advertencia: No se pudo cargar '{archivo}' -> {e}")

        print(f" > [PluginManager]: {len(self.tools)} herramientas listas y activas.")
        return self.tools

    def _cargar_modulo(self, nombre_modulo, ruta):
        spec = importlib.util.spec_from_file_location(nombre_modulo, ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        for nombre, funcion in inspect.getmembers(modulo, inspect.isfunction):
            if getattr(funcion, "_es_herramienta_jarvis", False):
                self.tools.append(funcion)
                self.tool_map[nombre] = funcion
                print(f"   [+] Plugin registrado: {nombre} ({nombre_modulo}.py)")

def jarvis_tool(func):
    func._es_herramienta_jarvis = True
    return func