"""Safe failure details: never expose provider response bodies or resume contents."""
from groq import APIStatusError, APITimeoutError, APIConnectionError
from pydantic import ValidationError


def provider_code(error: Exception) -> str | None:
    body = getattr(error, 'body', None)
    if not isinstance(body, dict):
        return None
    details = body.get('error', body)
    code = details.get('code') if isinstance(details, dict) else None
    if isinstance(code, str) and len(code) < 100 and all(c.isalnum() or c in '_-' for c in code):
        return code
    return None


def analysis_error_message(error: Exception) -> str:
    if isinstance(error, APITimeoutError):
        return 'Groq timed out while generating the analysis. Please retry.'
    if isinstance(error, APIConnectionError):
        return 'Unable to connect to Groq. Check the backend connection and retry.'
    if isinstance(error, APIStatusError):
        if error.status_code == 429:
            return 'Groq rate limit reached. Please wait before starting another analysis.'
        if error.status_code in {401, 403}:
            return 'Groq denied access. Check the backend API key and model permissions.'
        if provider_code(error) == 'json_validate_failed':
            return 'Groq could not generate a complete structured report. Please retry.'
        if error.status_code == 400:
            return 'Groq rejected the analysis request. Check the backend model settings and error log.'
        return 'Groq is unavailable. Please retry later.'
    if isinstance(error, ValidationError):
        for item in error.errors(include_input=False, include_context=False):
            if item['loc'] == ('requirements',):
                reason = {
                    'missing': 'omitted the requirements list',
                    'too_short': 'returned an empty requirements list',
                    'list_type': 'returned requirements in the wrong format',
                }.get(item['type'])
                if reason:
                    return f'The model {reason}. Please retry.'
        return 'The model returned an incomplete or inconsistent report. Please retry.'
    return 'Analysis could not be completed. Please retry.'


def analysis_error_context(error: Exception) -> dict:
    context = {'type': type(error).__name__}
    if isinstance(error, APIStatusError):
        context.update(status=error.status_code, code=provider_code(error), request_id=error.response.headers.get('x-request-id'))
    if isinstance(error, ValidationError):
        issues = error.errors(include_input=False, include_context=False)[:10]
        context['invalid_fields'] = ['.'.join(str(part) for part in item['loc']) for item in issues]
        context['validation_errors'] = [
            {'field': '.'.join(str(part) for part in item['loc']), 'code': item['type']}
            for item in issues
        ]
    return context
