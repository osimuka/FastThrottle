# FastThrottle

An efficient and easy-to-integrate rate limiter for FastAPI applications. Protect your API endpoints without compromising speed.

### Applying Rate Limiting

An example of how to apply the throttle
using the decorator, specify ` max_requests` and `window`

```python
@app.get("/some-path")
@rate_limit_async(max_rquests=50, window=60)
async def some_path(request: Request):
  return {"message": "Not throttled"}
```
