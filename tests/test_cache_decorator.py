"""Regression test for the Streamlit cache-decorator factory."""

import inspect


def test_cached_factory_returns_a_real_function_decorator():
    # Importing the module used to fail because the decorator function itself
    # was passed to st.cache_data and Streamlit attempted to hash a function.
    from physics_playground.simulation_cache import cached_collision

    signature = inspect.signature(cached_collision)
    assert "p" in signature.parameters
