#!/usr/bin/env python3
"""
(Claude) Code Graph Generator

Generate dependency and call graphs for Python codebases using grimp and PyCG.

Requirements (☑️✅🧪):
- Extract import relationships between modules using grimp
- Generate call graph using PyCG
- Create nodes from modules and functions
- Output JSON files for import edges, call edges, and nodes
- Support for custom package path

⛔ Out of scope:
- yFiles integration (handled separately)
- Interactive visualization
- GraphML output (JSON only for now)

⏳ TODO:
- Add filtering for external packages
- Add grouping by package/module hierarchy
- Add detection of "state" modules (global state, config, etc.)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set
import grimp
import networkx as nx

# Import PyCG for call graph generation
try:
    # Handle both PyCG and pycg package names
    try:
        from PyCG.pycg import CallGraphGenerator
        from PyCG import formats
    except ImportError:
        from pycg.pycg import CallGraphGenerator
        from pycg import formats
    PYCG_AVAILABLE = True
except ImportError:
    PYCG_AVAILABLE = False
    print("Warning: PyCG not available, call graph generation will be skipped")


class CodeGraphGenerator:
    """Generate code dependency and call graphs from Python packages."""

    def __init__(self, package_name: str, package_path: str = None):
        """
        Initialize graph generator.

        Args:
            package_name: Name of the Python package to analyze
            package_path: Optional path to package directory (defaults to current dir)
        """
        self.package_name = package_name
        self.package_path = Path(package_path) if package_path else Path.cwd()

        # Add package path to sys.path so grimp can find it
        package_parent = str(self.package_path.absolute())
        if package_parent not in sys.path:
            sys.path.insert(0, package_parent)
            print(f"Added {package_parent} to Python path")

        self.import_graph = None
        self.call_graph_data = None
        self.nodes = []
        self.import_edges = []
        self.call_edges = []

    def generate_import_graph(self) -> List[Dict]:
        """
        Use grimp to extract import relationships.

        Returns:
            List of edge dictionaries with source, target, type
        """
        print(f"📊 Generating import graph for '{self.package_name}'...")

        try:
            # Build import graph using grimp
            self.import_graph = grimp.build_graph(self.package_name)

            # Extract edges by iterating through modules
            edges = []
            for module in self.import_graph.modules:
                # Find all modules that this module imports
                imported_modules = self.import_graph.find_modules_directly_imported_by(module)
                for imported in imported_modules:
                    edges.append({
                        'source': module,
                        'target': imported,
                        'type': 'imports'
                    })

            self.import_edges = edges
            print(f"✓ Found {len(edges)} import relationships across {len(self.import_graph.modules)} modules")
            return edges

        except Exception as e:
            print(f"✗ Error generating import graph: {e}")
            raise

    def generate_call_graph(self, max_iter: int = 3) -> List[Dict]:
        """
        Use PyCG to extract call relationships.

        Args:
            max_iter: Maximum iterations for PyCG analysis

        Returns:
            List of edge dictionaries with source, target, type
        """
        print(f"📞 Generating call graph using PyCG (max_iter={max_iter})...")

        if not PYCG_AVAILABLE:
            print("⚠ PyCG not available, skipping call graph generation")
            return []

        try:
            # Use PyCG directly as a library
            cg = CallGraphGenerator(
                entry_point=[],  # No specific entry points
                package=self.package_name,
                max_iter=max_iter,
                operation="call-graph"  # Default operation
            )

            # Analyze the package
            print(f"Analyzing package '{self.package_name}'...")
            cg.analyze()

            # Format output
            formatter = formats.Simple(cg)
            self.call_graph_data = formatter.generate()

            # Save to file for reference
            callgraph_path = self.package_path / "callgraph.json"
            with open(callgraph_path, 'w') as f:
                json.dump(self.call_graph_data, f, indent=2)
            print(f"Saved call graph to {callgraph_path}")

            # Convert PyCG format to edge list
            edges = []
            for caller, callees in self.call_graph_data.items():
                if isinstance(callees, list):
                    for callee in callees:
                        edges.append({
                            'source': caller,
                            'target': callee,
                            'type': 'calls'
                        })

            self.call_edges = edges
            print(f"✓ Found {len(edges)} call relationships")
            return edges

        except Exception as e:
            print(f"✗ Error generating call graph: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - just continue with empty call graph
            self.call_edges = []
            return []

    def extract_nodes(self) -> List[Dict]:
        """
        Extract nodes from import graph and call graph.

        Returns:
            List of node dictionaries with id, label, type, group
        """
        print("🔍 Extracting nodes from graphs...")

        nodes_set = set()
        nodes = []

        # Add module nodes from import graph
        if self.import_graph:
            for module in self.import_graph.modules:
                if module not in nodes_set:
                    nodes_set.add(module)
                    nodes.append({
                        'id': module,
                        'label': module.split('.')[-1],  # Use last part as label
                        'type': 'module',
                        'group': '.'.join(module.split('.')[:-1]) if '.' in module else self.package_name
                    })

        # Add function/class nodes from call graph
        if self.call_graph_data:
            for function in self.call_graph_data.keys():
                if function not in nodes_set:
                    nodes_set.add(function)
                    # Parse function name to determine type
                    node_type = 'class' if '.<' in function else 'function'
                    module_name = function.split('.')[0] if '.' in function else self.package_name

                    nodes.append({
                        'id': function,
                        'label': function.split('.')[-1],
                        'type': node_type,
                        'group': module_name
                    })

        self.nodes = nodes
        print(f"✓ Extracted {len(nodes)} unique nodes")
        return nodes

    def save_to_json(self, output_dir: Path = None):
        """
        Save nodes and edges to JSON files.

        Args:
            output_dir: Directory to save JSON files (defaults to current dir)
        """
        output_dir = Path(output_dir) if output_dir else self.package_path
        output_dir.mkdir(exist_ok=True, parents=True)

        # Save import edges
        import_edges_path = output_dir / "edges_import.json"
        with open(import_edges_path, 'w') as f:
            json.dump(self.import_edges, f, indent=2)
        print(f"✓ Saved {len(self.import_edges)} import edges to {import_edges_path}")

        # Save call edges
        call_edges_path = output_dir / "edges_call.json"
        with open(call_edges_path, 'w') as f:
            json.dump(self.call_edges, f, indent=2)
        print(f"✓ Saved {len(self.call_edges)} call edges to {call_edges_path}")

        # Save nodes
        nodes_path = output_dir / "nodes.json"
        with open(nodes_path, 'w') as f:
            json.dump(self.nodes, f, indent=2)
        print(f"✓ Saved {len(self.nodes)} nodes to {nodes_path}")

        # Save combined graph
        combined_path = output_dir / "graph_combined.json"
        combined = {
            'nodes': self.nodes,
            'edges': self.import_edges + self.call_edges
        }
        with open(combined_path, 'w') as f:
            json.dump(combined, f, indent=2)
        print(f"✓ Saved combined graph to {combined_path}")

    def generate_all(self, max_iter: int = 3, output_dir: Path = None):
        """
        Run complete graph generation pipeline.

        Args:
            max_iter: Maximum iterations for PyCG analysis
            output_dir: Directory to save JSON files
        """
        print(f"\n{'='*60}")
        print(f"Code Graph Generation for '{self.package_name}'")
        print(f"{'='*60}\n")

        try:
            # Generate import graph
            self.generate_import_graph()

            # Generate call graph
            self.generate_call_graph(max_iter=max_iter)

            # Extract nodes
            self.extract_nodes()

            # Save to JSON
            self.save_to_json(output_dir=output_dir)

            print(f"\n{'='*60}")
            print("✓ Graph generation complete!")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n✗ Graph generation failed: {e}")
            raise


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_code_graph.py <package_name> [package_path] [max_iter]")
        print("\nExample:")
        print("  python generate_code_graph.py mypackage")
        print("  python generate_code_graph.py mypackage /path/to/package 5")
        sys.exit(1)

    package_name = sys.argv[1]
    package_path = sys.argv[2] if len(sys.argv) > 2 else None
    max_iter = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    generator = CodeGraphGenerator(package_name, package_path)
    generator.generate_all(max_iter=max_iter)


if __name__ == "__main__":
    main()
