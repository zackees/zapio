"""
Build system components for Zapio.

This module provides the build system implementation including:
- Source file discovery and preprocessing
- Compilation (avr-gcc/avr-g++)
- Linking (avr-gcc linker, avr-objcopy)
- Build orchestration
"""

from .source_scanner import SourceScanner, SourceCollection

__all__ = [
    'SourceScanner',
    'SourceCollection',
]

# Import other components if they exist
try:
    from .compiler import Compiler  # noqa: F401
    __all__.append('Compiler')
except ImportError:
    pass

try:
    from .linker import Linker  # noqa: F401
    __all__.append('Linker')
except ImportError:
    pass

try:
    from .orchestrator import BuildOrchestrator  # noqa: F401
    __all__.append('BuildOrchestrator')
except ImportError:
    pass

try:
    from .esp32_orchestrator import ESP32Orchestrator  # noqa: F401
    __all__.append('ESP32Orchestrator')
except ImportError:
    pass

try:
    from .binary_generator import BinaryGenerator  # noqa: F401
    __all__.append('BinaryGenerator')
except ImportError:
    pass

try:
    from .build_utils import SizeInfoPrinter  # noqa: F401
    __all__.append('SizeInfoPrinter')
except ImportError:
    pass

try:
    from .flag_builder import FlagBuilder  # noqa: F401
    __all__.append('FlagBuilder')
except ImportError:
    pass

try:
    from .compilation_executor import CompilationExecutor  # noqa: F401
    __all__.append('CompilationExecutor')
except ImportError:
    pass

try:
    from .archive_creator import ArchiveCreator  # noqa: F401
    __all__.append('ArchiveCreator')
except ImportError:
    pass

try:
    from .library_dependency_processor import (  # noqa: F401
        LibraryDependencyProcessor,
        LibraryProcessingResult
    )
    __all__.extend(['LibraryDependencyProcessor', 'LibraryProcessingResult'])
except ImportError:
    pass

try:
    from .source_compilation_orchestrator import (  # noqa: F401
        SourceCompilationOrchestrator,
        SourceCompilationOrchestratorError,
        MultiGroupCompilationResult
    )
    __all__.extend([
        'SourceCompilationOrchestrator',
        'SourceCompilationOrchestratorError',
        'MultiGroupCompilationResult'
    ])
except ImportError:
    pass

try:
    from .build_component_factory import BuildComponentFactory  # noqa: F401
    __all__.append('BuildComponentFactory')
except ImportError:
    pass
