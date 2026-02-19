"""Initialization utilities for nanobot."""

from pathlib import Path
import shutil
from rich.console import Console
from nanobot.config.schema import Config

console = Console()

def initialize_nanobot(target_root: Path, force: bool = False) -> None:
    """
    Initialize nanobot configuration and workspace in the target directory (e.g. ~/.nanobot).
    
    Args:
        target_root: The root directory for nanobot data (containing config.json and workspace/).
        force: If True, overwrite existing configuration without asking (use with caution).
               Note: Current implementation of force logic is inside the caller or handled by
               safe checks below. This function primarily ensures structure exists.
    """
    from nanobot.config.loader import save_config
    
    # Ensure root exists
    if not target_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)
    
    config_path = target_root / "config.json"
    workspace_path = target_root / "workspace"
    
    # 1. Config initialization
    # Source config.example.json from package
    pkg_root = Path(__file__).parent.parent
    pkg_config = pkg_root / "config.example.json"
    
    created_config = False
    if not config_path.exists():
        if pkg_config.exists():
            try:
                shutil.copy2(pkg_config, config_path)
                console.print(f"[green]✓[/green] Created config at {config_path}")
                created_config = True
            except Exception as e:
                console.print(f"[red]Failed to copy config template: {e}[/red]")
        else:
            save_config(Config(), config_path)
            console.print(f"[green]✓[/green] Created default config at {config_path}")
            created_config = True
    else:
        # Config exists. If we wanted to force overwrite, we would do it here.
        # But generally we want to preserve user config.
        pass

    # 2. Workspace initialization
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created workspace at {workspace_path}")

    # Copy templates
    _copy_workspace_templates(workspace_path, pkg_root / "workspace")
    
    if created_config:
        console.print(f"\n[bold]Initialized nanobot at {target_root}[/bold]")


def _copy_workspace_templates(target_dir: Path, source_dir: Path):
    """Recursively copy template files from source to target."""
    if not source_dir.exists():
        console.print(f"[yellow]Warning: Template directory not found at {source_dir}[/yellow]")
        return

    console.print("  [dim]Checking templates...[/dim]")
    
    # Walk through the source directory
    for src_path in source_dir.rglob("*"):
        if src_path.is_dir():
            continue
            
        # Calculate relative path to maintain structure
        rel_path = src_path.relative_to(source_dir)
        dest_path = target_dir / rel_path
        
        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Don't overwrite existing files (user data)
        if not dest_path.exists():
            try:
                shutil.copy2(src_path, dest_path)
                console.print(f"  [dim]Created {rel_path}[/dim]")
            except Exception as e:
                console.print(f"[red]Failed to copy {rel_path}: {e}[/red]")
        else:
            pass
