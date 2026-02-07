"""Unit tests for pagination utilities."""

from mcp_server_spira.features.common.pagination import (
    paginate_client_side,
    paginate_server_side,
)


class TestPaginateClientSide:
    """Tests for paginate_client_side function."""

    def test_paginate_first_page_full(self):
        """Test pagination for first page with full results."""
        items = list(range(1, 101))  # 100 items
        result = paginate_client_side(items, limit=25, offset=0)

        assert result["data"] == list(range(1, 26))
        assert result["pagination"]["limit"] == 25
        assert result["pagination"]["offset"] == 0
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["total_count"] == 100
        assert result["pagination"]["has_more"] is True
        assert result["pagination"]["pagination_type"] == "client-side"

    def test_paginate_middle_page(self):
        """Test pagination for middle page."""
        items = list(range(1, 101))  # 100 items
        result = paginate_client_side(items, limit=25, offset=25)

        assert result["data"] == list(range(26, 51))
        assert result["pagination"]["offset"] == 25
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["has_more"] is True

    def test_paginate_last_page_full(self):
        """Test pagination for last page with full results."""
        items = list(range(1, 101))  # 100 items
        result = paginate_client_side(items, limit=25, offset=75)

        assert result["data"] == list(range(76, 101))
        assert result["pagination"]["offset"] == 75
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["total_count"] == 100
        assert result["pagination"]["has_more"] is False

    def test_paginate_last_page_partial(self):
        """Test pagination for last page with partial results."""
        items = list(range(1, 48))  # 47 items
        result = paginate_client_side(items, limit=25, offset=25)

        assert result["data"] == list(range(26, 48))
        assert result["pagination"]["returned_count"] == 22
        assert result["pagination"]["total_count"] == 47
        assert result["pagination"]["has_more"] is False

    def test_paginate_empty_list(self):
        """Test pagination with empty list."""
        items: list[dict] = []
        result = paginate_client_side(items, limit=25, offset=0)

        assert result["data"] == []
        assert result["pagination"]["returned_count"] == 0
        assert result["pagination"]["total_count"] == 0
        assert result["pagination"]["has_more"] is False

    def test_paginate_offset_beyond_end(self):
        """Test pagination with offset beyond end of list."""
        items = list(range(1, 26))  # 25 items
        result = paginate_client_side(items, limit=25, offset=50)

        assert result["data"] == []
        assert result["pagination"]["returned_count"] == 0
        assert result["pagination"]["total_count"] == 25
        assert result["pagination"]["has_more"] is False

    def test_paginate_single_item(self):
        """Test pagination with single item."""
        items = [{"id": 1, "name": "Task 1"}]
        result = paginate_client_side(items, limit=25, offset=0)

        assert result["data"] == [{"id": 1, "name": "Task 1"}]
        assert result["pagination"]["returned_count"] == 1
        assert result["pagination"]["total_count"] == 1
        assert result["pagination"]["has_more"] is False

    def test_paginate_limit_larger_than_total(self):
        """Test pagination when limit is larger than total items."""
        items = list(range(1, 11))  # 10 items
        result = paginate_client_side(items, limit=100, offset=0)

        assert result["data"] == list(range(1, 11))
        assert result["pagination"]["returned_count"] == 10
        assert result["pagination"]["total_count"] == 10
        assert result["pagination"]["has_more"] is False

    def test_paginate_limit_one(self):
        """Test pagination with limit of 1."""
        items = list(range(1, 6))  # 5 items
        result = paginate_client_side(items, limit=1, offset=0)

        assert result["data"] == [1]
        assert result["pagination"]["returned_count"] == 1
        assert result["pagination"]["total_count"] == 5
        assert result["pagination"]["has_more"] is True

    def test_paginate_offset_at_last_item(self):
        """Test pagination with offset at last item."""
        items = list(range(1, 11))  # 10 items
        result = paginate_client_side(items, limit=25, offset=9)

        assert result["data"] == [10]
        assert result["pagination"]["returned_count"] == 1
        assert result["pagination"]["has_more"] is False

    def test_paginate_preserves_data_types(self):
        """Test that pagination preserves complex data types."""
        items = [
            {"TaskId": 1, "Name": "Task 1", "Tags": ["bug", "critical"]},
            {"TaskId": 2, "Name": "Task 2", "Tags": ["feature"]},
            {"TaskId": 3, "Name": "Task 3", "Tags": []},
        ]
        result = paginate_client_side(items, limit=2, offset=0)

        assert result["data"] == items[:2]
        assert result["data"][0]["Tags"] == ["bug", "critical"]
        assert result["pagination"]["total_count"] == 3

    def test_paginate_exact_multiple_of_limit(self):
        """Test pagination when total is exact multiple of limit."""
        items = list(range(1, 51))  # 50 items
        result = paginate_client_side(items, limit=25, offset=25)

        assert result["data"] == list(range(26, 51))
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["has_more"] is False

    def test_paginate_has_more_calculation(self):
        """Test has_more flag calculation for various scenarios."""
        items = list(range(1, 101))  # 100 items

        # First page - has more
        result1 = paginate_client_side(items, limit=25, offset=0)
        assert result1["pagination"]["has_more"] is True

        # Second page - has more
        result2 = paginate_client_side(items, limit=25, offset=25)
        assert result2["pagination"]["has_more"] is True

        # Third page - has more
        result3 = paginate_client_side(items, limit=25, offset=50)
        assert result3["pagination"]["has_more"] is True

        # Last page - no more
        result4 = paginate_client_side(items, limit=25, offset=75)
        assert result4["pagination"]["has_more"] is False

    def test_paginate_metadata_structure(self):
        """Test that pagination metadata has correct structure."""
        items = list(range(1, 11))
        result = paginate_client_side(items, limit=5, offset=0)

        pagination = result["pagination"]
        assert "limit" in pagination
        assert "offset" in pagination
        assert "returned_count" in pagination
        assert "total_count" in pagination
        assert "has_more" in pagination
        assert "pagination_type" in pagination
        assert pagination["pagination_type"] == "client-side"

    def test_paginate_with_zero_offset(self):
        """Test pagination explicitly with offset=0."""
        items = list(range(1, 11))
        result = paginate_client_side(items, limit=5, offset=0)

        assert result["data"] == list(range(1, 6))
        assert result["pagination"]["offset"] == 0


class TestPaginateServerSide:
    """Tests for paginate_server_side function."""

    def test_paginate_server_side_first_page(self):
        """Test server-side pagination for first page."""
        items = list(range(1, 26))  # 25 items (already paginated by server)
        result = paginate_server_side(items, limit=25, offset=0, total_count=100)

        assert result["data"] == items
        assert result["pagination"]["limit"] == 25
        assert result["pagination"]["offset"] == 0
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["total_count"] == 100
        assert result["pagination"]["has_more"] is True
        assert result["pagination"]["pagination_type"] == "server-side"

    def test_paginate_server_side_middle_page(self):
        """Test server-side pagination for middle page."""
        items = list(range(26, 51))  # Items 26-50
        result = paginate_server_side(items, limit=25, offset=25, total_count=100)

        assert result["data"] == items
        assert result["pagination"]["offset"] == 25
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["has_more"] is True

    def test_paginate_server_side_last_page_full(self):
        """Test server-side pagination for last page with full results."""
        items = list(range(76, 101))  # Items 76-100
        result = paginate_server_side(items, limit=25, offset=75, total_count=100)

        assert result["data"] == items
        assert result["pagination"]["returned_count"] == 25
        assert result["pagination"]["has_more"] is False

    def test_paginate_server_side_last_page_partial(self):
        """Test server-side pagination for last page with partial results."""
        items = list(range(26, 48))  # 22 items
        result = paginate_server_side(items, limit=25, offset=25, total_count=47)

        assert result["data"] == items
        assert result["pagination"]["returned_count"] == 22
        assert result["pagination"]["total_count"] == 47
        assert result["pagination"]["has_more"] is False

    def test_paginate_server_side_empty_results(self):
        """Test server-side pagination with empty results."""
        items: list[dict] = []
        result = paginate_server_side(items, limit=25, offset=0, total_count=0)

        assert result["data"] == []
        assert result["pagination"]["returned_count"] == 0
        assert result["pagination"]["total_count"] == 0
        assert result["pagination"]["has_more"] is False

    def test_paginate_server_side_single_item(self):
        """Test server-side pagination with single item."""
        items = [{"id": 1, "name": "Task 1"}]
        result = paginate_server_side(items, limit=25, offset=0, total_count=1)

        assert result["data"] == items
        assert result["pagination"]["returned_count"] == 1
        assert result["pagination"]["total_count"] == 1
        assert result["pagination"]["has_more"] is False

    def test_paginate_server_side_has_more_calculation(self):
        """Test has_more flag calculation for server-side pagination."""
        # First page - has more
        result1 = paginate_server_side(list(range(1, 26)), limit=25, offset=0, total_count=100)
        assert result1["pagination"]["has_more"] is True

        # Last page - no more
        result2 = paginate_server_side(list(range(76, 101)), limit=25, offset=75, total_count=100)
        assert result2["pagination"]["has_more"] is False

        # Partial last page - no more
        result3 = paginate_server_side(list(range(26, 48)), limit=25, offset=25, total_count=47)
        assert result3["pagination"]["has_more"] is False

    def test_paginate_server_side_metadata_structure(self):
        """Test that server-side pagination metadata has correct structure."""
        items = list(range(1, 11))
        result = paginate_server_side(items, limit=10, offset=0, total_count=50)

        pagination = result["pagination"]
        assert "limit" in pagination
        assert "offset" in pagination
        assert "returned_count" in pagination
        assert "total_count" in pagination
        assert "has_more" in pagination
        assert "pagination_type" in pagination
        assert pagination["pagination_type"] == "server-side"

    def test_paginate_server_side_preserves_data_types(self):
        """Test that server-side pagination preserves complex data types."""
        items = [
            {"TaskId": 1, "Name": "Task 1", "CustomProperties": [{"id": 1}]},
            {"TaskId": 2, "Name": "Task 2", "CustomProperties": []},
        ]
        result = paginate_server_side(items, limit=25, offset=0, total_count=10)

        assert result["data"] == items
        assert result["data"][0]["CustomProperties"] == [{"id": 1}]

    def test_paginate_server_side_limit_larger_than_total(self):
        """Test server-side pagination when limit is larger than total."""
        items = list(range(1, 11))  # 10 items
        result = paginate_server_side(items, limit=100, offset=0, total_count=10)

        assert result["data"] == items
        assert result["pagination"]["returned_count"] == 10
        assert result["pagination"]["has_more"] is False


class TestPaginationComparison:
    """Tests comparing client-side and server-side pagination."""

    def test_both_return_same_structure(self):
        """Test that both pagination functions return same structure."""
        items = list(range(1, 26))

        client_result = paginate_client_side(items, limit=25, offset=0)
        server_result = paginate_server_side(items, limit=25, offset=0, total_count=25)

        # Both should have same keys
        assert set(client_result.keys()) == set(server_result.keys())
        assert set(client_result["pagination"].keys()) == set(server_result["pagination"].keys())

    def test_pagination_type_differs(self):
        """Test that pagination_type correctly identifies implementation."""
        items = list(range(1, 26))

        client_result = paginate_client_side(items, limit=25, offset=0)
        server_result = paginate_server_side(items, limit=25, offset=0, total_count=25)

        assert client_result["pagination"]["pagination_type"] == "client-side"
        assert server_result["pagination"]["pagination_type"] == "server-side"

    def test_both_handle_empty_lists(self):
        """Test that both functions handle empty lists correctly."""
        client_result = paginate_client_side([], limit=25, offset=0)
        server_result = paginate_server_side([], limit=25, offset=0, total_count=0)

        assert client_result["data"] == []
        assert server_result["data"] == []
        assert client_result["pagination"]["has_more"] is False
        assert server_result["pagination"]["has_more"] is False

    def test_both_calculate_has_more_correctly(self):
        """Test that both functions calculate has_more flag correctly."""
        items = list(range(1, 26))

        # When there are more items
        client_result1 = paginate_client_side(list(range(1, 101)), limit=25, offset=0)
        server_result1 = paginate_server_side(items, limit=25, offset=0, total_count=100)

        assert client_result1["pagination"]["has_more"] is True
        assert server_result1["pagination"]["has_more"] is True

        # When there are no more items
        client_result2 = paginate_client_side(items, limit=25, offset=0)
        server_result2 = paginate_server_side(items, limit=25, offset=0, total_count=25)

        assert client_result2["pagination"]["has_more"] is False
        assert server_result2["pagination"]["has_more"] is False


class TestPaginationEdgeCases:
    """Tests for edge cases in pagination."""

    def test_client_side_very_large_offset(self):
        """Test client-side pagination with very large offset."""
        items = list(range(1, 11))
        result = paginate_client_side(items, limit=25, offset=1000000)

        assert result["data"] == []
        assert result["pagination"]["returned_count"] == 0
        assert result["pagination"]["has_more"] is False

    def test_client_side_very_large_limit(self):
        """Test client-side pagination with very large limit."""
        items = list(range(1, 11))
        result = paginate_client_side(items, limit=1000000, offset=0)

        assert result["data"] == items
        assert result["pagination"]["returned_count"] == 10
        assert result["pagination"]["has_more"] is False

    def test_server_side_returned_count_matches_items_length(self):
        """Test that server-side returned_count always matches items length."""
        test_cases: list[tuple[list[int], int, int, int]] = [
            (list(range(1, 26)), 25, 0, 100),
            (list(range(1, 11)), 25, 0, 10),
            ([1], 25, 0, 1),
            ([], 25, 0, 0),
        ]

        for items, limit, offset, total in test_cases:
            result = paginate_server_side(items, limit, offset, total)
            assert result["pagination"]["returned_count"] == len(items)

    def test_pagination_with_none_values_in_data(self):
        """Test pagination with None values in data."""
        items = [{"id": 1, "value": None}, {"id": 2, "value": "test"}]

        client_result = paginate_client_side(items, limit=25, offset=0)
        server_result = paginate_server_side(items, limit=25, offset=0, total_count=2)

        assert client_result["data"][0]["value"] is None
        assert server_result["data"][0]["value"] is None

    def test_pagination_with_nested_structures(self):
        """Test pagination with deeply nested data structures."""
        items = [{"id": 1, "nested": {"level1": {"level2": {"level3": ["a", "b", "c"]}}}}]

        result = paginate_client_side(items, limit=25, offset=0)

        assert result["data"][0]["nested"]["level1"]["level2"]["level3"] == ["a", "b", "c"]
