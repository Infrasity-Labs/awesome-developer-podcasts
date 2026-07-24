import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests


DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1
DEFAULT_MAX_BACKOFF = 30


def _retry_after_seconds(value):
    if not value:
        return None

    try:
        return max(0, int(value))
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0, int((retry_at - datetime.now(timezone.utc)).total_seconds()))
    except (TypeError, ValueError):
        return None


def _backoff_seconds(attempt, backoff_factor, max_backoff):
    return min(max_backoff, backoff_factor * (2 ** (attempt - 1)))


def retry_on_rate_limit(func):
    def wrapper(method, url, **kwargs):
        max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
        backoff_factor = kwargs.pop("backoff_factor", DEFAULT_BACKOFF_FACTOR)
        max_backoff = kwargs.pop("max_backoff", DEFAULT_MAX_BACKOFF)

        for attempt in range(1, max_retries + 1):
            response = func(method, url, **kwargs)
            if response.status_code != 429 or attempt == max_retries:
                return response

            retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
            delay = retry_after
            if delay is None:
                delay = _backoff_seconds(attempt, backoff_factor, max_backoff)

            print(f"Rate limited by {url}. Retrying in {delay}s ({attempt}/{max_retries})...")
            time.sleep(delay)

        return response

    return wrapper


@retry_on_rate_limit
def request_with_backoff(method, url, **kwargs):
    return requests.request(method, url, **kwargs)


def get_with_backoff(url, **kwargs):
    return request_with_backoff("GET", url, **kwargs)


def post_with_backoff(url, **kwargs):
    return request_with_backoff("POST", url, **kwargs)
