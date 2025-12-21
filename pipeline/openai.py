from pathlib import Path
import os
import requests
import json


def upload_pdf_to_openai(pdf_path: Path, timeout: int = 30) -> str:
    """
    Lädt eine PDF-Datei zu OpenAI hoch und gibt die file_id zurück.

    Erwartet:
      - OPENAI_API_KEY ist als Environment Variable gesetzt
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY fehlt in der Environment")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF nicht gefunden: {pdf_path}")

    resp = requests.post(
        "https://api.openai.com/v1/files",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        files={
            "file": (pdf_path.name, pdf_path.open("rb"), "application/pdf")
        },
        data={
            # bei /v1/files ist "assistants" (oder "user_data" je nach API-Stand) üblich.
            # Wir lassen es wie bisher, damit dein Setup weiterhin läuft.
            "purpose": "assistants"
        },
        timeout=timeout
    )

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        raise RuntimeError(f"OpenAI upload error {resp.status_code}: {resp.text}")

    file_id = resp.json()["id"]
    print("✅ Upload OK, file_id:", file_id)
    return file_id




def run_prompt_with_file(
    file_id: str,
    model: str = "gpt-4.1-mini",
    prompt_file: Path | None = None,
    prompt_text: str | None = None,
    timeout: int = 60,
) -> str:
    """
    Ruft den OpenAI Responses-Endpunkt mit Prompt und einem File Attachment auf.

    - Prompt kommt entweder direkt als prompt_text
      oder wird aus prompt_file gelesen.
    - OPENAI_API_KEY wird aus der Environment gelesen.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY fehlt in der Environment")

    if prompt_text is None:
        if prompt_file is None:
            raise RuntimeError("prompt_file oder prompt_text muss gesetzt sein")

        if not prompt_file.exists():
            raise RuntimeError(f"Prompt-Datei fehlt: {prompt_file}")

        prompt_text = prompt_file.read_text(encoding="utf-8").strip()

    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt_text},
                        {"type": "input_file", "file_id": file_id}
                    ]
                }
            ]
        }),
        timeout=timeout,
    )

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")

    data = resp.json()

    out_text = ""
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                out_text += c.get("text", "")

    return out_text.strip()
