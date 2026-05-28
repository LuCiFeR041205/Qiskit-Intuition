from .base_agent import load_root_agent

_root_builder = load_root_agent("builder_agent")
build_circuit_from_prompt = _root_builder.build_circuit_from_prompt
