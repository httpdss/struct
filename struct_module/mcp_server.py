"""
MCP Server implementation for the struct tool using FastMCP stdio transport.

This module provides MCP (Model Context Protocol) support for:
1. Listing available structures
2. Getting detailed information about structures
3. Generating structures with various options
4. Validating structure configurations
"""
import asyncio
import logging
import os
import sys
import yaml
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from struct_module.commands.generate import GenerateCommand
from struct_module.commands.validate import ValidateCommand


class StructMCPServer:
    """FastMCP-based MCP Server for struct tool operations."""

    def __init__(self):
        self.app = FastMCP("struct-mcp-server", version="1.0.0")
        self.logger = logging.getLogger(__name__)
        self._register_tools()

    # =====================
    # Tool logic (transport-agnostic)
    # =====================
    def _list_structures_logic(self, structures_path: Optional[str] = None) -> str:
        this_file = os.path.dirname(os.path.realpath(__file__))
        contribs_path = os.path.join(this_file, "contribs")

        paths_to_list = [contribs_path]
        if structures_path:
            paths_to_list = [structures_path, contribs_path]

        all_structures = set()
        for path in paths_to_list:
            if os.path.exists(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith(".yaml"):
                            rel = os.path.relpath(os.path.join(root, file), path)[:-5]
                            if path != contribs_path:
                                rel = f"+ {rel}"
                            all_structures.add(rel)

        sorted_list = sorted(all_structures)
        result_text = "📃 Available structures:\n\n" + "\n".join([f" - {s}" for s in sorted_list])
        result_text += "\n\nNote: Structures with '+' sign are custom structures"
        return result_text

    def _get_structure_info_logic(self, structure_name: Optional[str], structures_path: Optional[str] = None) -> str:
        if not structure_name:
            return "Error: structure_name is required"

        # Resolve path
        if structure_name.startswith("file://") and structure_name.endswith(".yaml"):
            file_path = structure_name[7:]
        else:
            this_file = os.path.dirname(os.path.realpath(__file__))
            base = structures_path or os.path.join(this_file, "contribs")
            file_path = os.path.join(base, f"{structure_name}.yaml")

        if not os.path.exists(file_path):
            return f"❗ Structure not found: {file_path}"

        with open(file_path, "r") as f:
            config = yaml.safe_load(f) or {}

        result_lines = [
            "📒 Structure definition\n",
            f"   📌 Name: {structure_name}\n",
            f"   📌 Description: {config.get('description', 'No description')}\n",
        ]

        files = config.get("files", [])
        if files:
            result_lines.append("   📌 Files:\n")
            for item in files:
                for name in item.keys():
                    result_lines.append(f"       - {name}\n")

        folders = config.get("folders", [])
        if folders:
            result_lines.append("   📌 Folders:\n")
            for item in folders:
                if isinstance(item, dict):
                    for folder, content in item.items():
                        result_lines.append(f"       - {folder}\n")
                        if isinstance(content, dict):
                            structs = content.get("struct")
                            if isinstance(structs, list):
                                result_lines.append("         • struct(s):\n")
                                for s in structs:
                                    result_lines.append(f"           - {s}\n")
                            elif isinstance(structs, str):
                                result_lines.append(f"         • struct: {structs}\n")
                            if isinstance(content.get("with"), dict):
                                with_items = " ".join([f"{k}={v}" for k, v in content["with"].items()])
                                result_lines.append(f"         • with:{with_items}\n")
                else:
                    result_lines.append(f"       - {item}\n")

        return "".join(result_lines)

    def _generate_structure_logic(
        self,
        structure_definition: str,
        base_path: str,
        output: str = "files",
        dry_run: bool = False,
        mappings: Optional[Dict[str, str]] = None,
        structures_path: Optional[str] = None,
    ) -> str:
        class Args:
            pass
        args = Args()
        args.structure_definition = structure_definition
        args.base_path = base_path
        args.output = "console" if output == "console" else "file"
        args.dry_run = dry_run
        args.structures_path = structures_path
        args.vars = None
        args.mappings_file = None
        args.backup = None
        args.file_strategy = "overwrite"
        args.global_system_prompt = None
        args.non_interactive = True
        args.input_store = "/tmp/struct/input.json"
        args.diff = False
        args.log = "INFO"
        args.config_file = None
        args.log_file = None

        # If mappings provided, convert to vars string consumed by GenerateCommand
        if mappings:
            args.vars = ",".join([f"{k}={v}" for k, v in mappings.items()])

        if output == "console":
            from io import StringIO
            buf = StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                GenerateCommand(None).execute(args)
                text = buf.getvalue()
                return text.strip() or "Structure generation completed successfully"
            finally:
                sys.stdout = old
        else:
            GenerateCommand(None).execute(args)
            if dry_run:
                return f"Dry run completed for structure '{structure_definition}' at '{base_path}'"
            return f"Structure '{structure_definition}' generated successfully at '{base_path}'"

    def _validate_structure_logic(self, yaml_file: Optional[str]) -> str:
        if not yaml_file:
            return "Error: yaml_file is required"

        class Args:
            pass
        args = Args()
        args.yaml_file = yaml_file
        args.log = "INFO"
        args.config_file = None
        args.log_file = None

        from io import StringIO
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            ValidateCommand(None).execute(args)
            text = buf.getvalue()
            return text.strip() or f"✅ YAML file '{yaml_file}' is valid"
        finally:
            sys.stdout = old

    # =====================
    # FastMCP tool registration (maps to logic above)
    # =====================
    def _register_tools(self):
        @self.app.tool(name="list_structures", description="List all available structure definitions")
        async def list_structures(structures_path: Optional[str] = None) -> str:
            return self._list_structures_logic(structures_path)

        @self.app.tool(name="get_structure_info", description="Get detailed information about a specific structure")
        async def get_structure_info(structure_name: str, structures_path: Optional[str] = None) -> str:
            return self._get_structure_info_logic(structure_name, structures_path)

        @self.app.tool(name="generate_structure", description="Generate a project structure using specified definition and options")
        async def generate_structure(
            structure_definition: str,
            base_path: str,
            output: str = "files",
            dry_run: bool = False,
            mappings: Optional[Dict[str, str]] = None,
            structures_path: Optional[str] = None,
        ) -> str:
            return self._generate_structure_logic(
                structure_definition,
                base_path,
                output,
                dry_run,
                mappings,
                structures_path,
            )

        @self.app.tool(name="validate_structure", description="Validate a structure configuration YAML file")
        async def validate_structure(yaml_file: str) -> str:
            return self._validate_structure_logic(yaml_file)

    async def run(
        self,
        transport: str = "stdio",
        *,
        show_banner: bool = True,
        host: str | None = None,
        port: int | None = None,
        path: str | None = None,
        log_level: str | None = None,
        stateless_http: bool | None = None,
    ):
        """Run the FastMCP server with the specified transport.

        Note: FastMCP.run(...) is synchronous in fastmcp>=2.x, so we
        offload it to a thread to avoid blocking the event loop.

        Args:
            transport: "stdio" | "http" | "sse"
            show_banner: Whether to print the FastMCP banner
            host: Host to bind for HTTP/SSE transports
            port: Port to bind for HTTP/SSE transports
            path: Endpoint path for HTTP/SSE transports
            log_level: Log level for the HTTP server (uvicorn)
            stateless_http: Whether to use stateless HTTP mode (HTTP only)
        """
        loop = asyncio.get_running_loop()
        def _run():
            kwargs = {"show_banner": show_banner}
            if transport in {"http", "sse"}:
                if host is not None:
                    kwargs["host"] = host
                if port is not None:
                    kwargs["port"] = port
                if path is not None:
                    kwargs["path"] = path
                if log_level is not None:
                    kwargs["log_level"] = log_level
                if stateless_http is not None and transport == "http":
                    kwargs["stateless_http"] = stateless_http
            self.app.run(transport, **kwargs)
        await loop.run_in_executor(None, _run)


async def main():
    logging.basicConfig(level=logging.INFO)
    server = StructMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
