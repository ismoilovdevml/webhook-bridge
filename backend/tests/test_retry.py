"""Tests for retry logic with exponential backoff."""

import pytest
import asyncio
from app.utils.retry import retry_with_backoff
from app.config import settings


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_success_first_attempt(self):
        """Test successful operation on first attempt."""
        call_count = 0

        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        success, result = await retry_with_backoff(
            successful_func, max_attempts=3, initial_delay=0.01
        )

        assert success is True
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_retry(self):
        """Test successful operation after retries."""
        call_count = 0

        async def retry_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        success, result = await retry_with_backoff(
            retry_then_success, max_attempts=3, initial_delay=0.01
        )

        assert success is True
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_failure_max_attempts(self):
        """Test failure after max attempts."""
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        success, result = await retry_with_backoff(
            always_fails, max_attempts=3, initial_delay=0.01
        )

        assert success is False
        assert isinstance(result, ValueError)
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_delay(self):
        """Test exponential backoff delay increases."""
        call_times = []

        async def track_timing():
            call_times.append(asyncio.get_event_loop().time())
            raise ValueError("Fail")

        await retry_with_backoff(
            track_timing, max_attempts=3, initial_delay=0.1, exponential_base=2.0
        )

        # Check that delays increase exponentially
        assert len(call_times) == 3
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.09  # ~0.1s

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= 0.18  # ~0.2s

    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        """Test max delay cap is respected."""
        call_times = []

        async def track_timing():
            call_times.append(asyncio.get_event_loop().time())
            raise ValueError("Fail")

        await retry_with_backoff(
            track_timing,
            max_attempts=5,
            initial_delay=1.0,
            max_delay=1.5,
            exponential_base=2.0,
        )

        # Check delays don't exceed max_delay
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i - 1]
            assert delay <= 1.6  # Max delay + small buffer

    @pytest.mark.asyncio
    async def test_retry_disabled(self):
        """Test retry when RETRY_ENABLED is False."""
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Error")

        original_enabled = settings.RETRY_ENABLED
        settings.RETRY_ENABLED = False

        try:
            success, result = await retry_with_backoff(
                failing_func, max_attempts=3
            )

            assert success is False
            assert call_count == 1  # Only called once, no retry
        finally:
            settings.RETRY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_retry_with_description(self):
        """Test retry with custom description."""
        async def failing_func():
            raise ValueError("Test error")

        success, result = await retry_with_backoff(
            failing_func,
            max_attempts=2,
            initial_delay=0.01,
            description="test operation",
        )

        assert success is False

    @pytest.mark.asyncio
    async def test_default_settings_used(self):
        """Test that default settings from config are used."""
        call_count = 0

        async def count_calls():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fail")

        # Use defaults from settings
        success, result = await retry_with_backoff(count_calls)

        # Should use RETRY_MAX_ATTEMPTS from settings (default 3)
        assert call_count == settings.RETRY_MAX_ATTEMPTS
