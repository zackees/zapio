"""Build utilities for Zapio.

This module provides utility functions for build operations like
printing size information and formatting build output.
"""

from typing import Optional

from ..build.linker import SizeInfo


class SizeInfoPrinter:
    """Utility class for printing firmware size information."""

    @staticmethod
    def print_size_info(size_info: Optional[SizeInfo]) -> None:
        """
        Print firmware size information in a formatted display.

        Args:
            size_info: Size information from linker (None to skip printing)
        """
        if not size_info:
            return

        print("Firmware Size:")
        print(f"  Program:  {size_info.total_flash:6d} bytes", end="")
        if size_info.flash_percent is not None:
            print(
                f" ({size_info.flash_percent:5.1f}% of {size_info.max_flash} bytes)"
            )
        else:
            print()

        print(f"  Data:     {size_info.data:6d} bytes")
        print(f"  BSS:      {size_info.bss:6d} bytes")
        print(f"  RAM:      {size_info.total_ram:6d} bytes", end="")
        if size_info.ram_percent is not None:
            print(f" ({size_info.ram_percent:5.1f}% of {size_info.max_ram} bytes)")
        else:
            print()
