def extract_text(response_json):
    out = []
    for item in response_json.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                out.append(c.get("text", ""))
    return "\n".join(out)

print(extract_text(resp.json()))
