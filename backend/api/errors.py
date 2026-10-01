"""Translate evaluator failures without repeating try/except in every route."""
import logging
from contextlib import contextmanager

from fastapi import HTTPException

logger = logging.getLogger(__name__)


@contextmanager
def evaluation_errors(message: str, *, validation_errors: bool = True):
    try:
        yield
    except HTTPException:
        raise
    except Exception as error:
        if validation_errors and isinstance(error, ValueError):
            raise HTTPException(status_code=400, detail=str(error)) from error
        logger.exception(message)
        raise HTTPException(status_code=500, detail=message) from error
