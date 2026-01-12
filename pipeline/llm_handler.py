from pathlib import Path
import os
import requests
import json
import time
from google import genai
from google.genai import types

def upload_pdf(pdf_path: Path, cfg: dict, timeout: int = 30) -> str:
    provider = cfg["llm"]["provider"]

    if provider == "openai":
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

    if provider == "google":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY fehlt")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF nicht gefunden: {pdf_path}")

        client = genai.Client(api_key=api_key)

        print(f"Uploading {pdf_path.name} to Google Gemini...")
        
        # KORREKTUR: Das Argument heißt 'file', nicht 'path'
        gemini_file = client.files.upload(file=str(pdf_path))

        # Warten, bis die Datei verarbeitet ist
        while gemini_file.state == "PROCESSING":
            time.sleep(2)
            gemini_file = client.files.get(name=gemini_file.name)

        if gemini_file.state == "FAILED":
            raise RuntimeError(f"Google File processing failed: {gemini_file.name}")

        print("✅ Upload OK, file_name:", gemini_file.name)
        return gemini_file.name

    raise RuntimeError(f"Unbekannter Provider: {provider}")



def run_prompt_with_file(
    file_id: str, # Bei Google ist dies der 'name' (z.B. files/abc)
    cfg: dict,
    prompt_file: Path | None = None,
    prompt_text: str | None = None,
    timeout: int = 60,
    response_schema: dict | None = None # Neu für striktes JSON
) -> str:
    provider = cfg["llm"]["provider"]
    model_name = cfg[provider]["model"]

    if provider == "openai":
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
                "model": model_name,
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

    if provider == "google":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)

        if prompt_text is None:
            if prompt_file:
                prompt_text = prompt_file.read_text(encoding="utf-8").strip()
            else:
                raise RuntimeError("Prompt fehlt")

        config = {
            "temperature": 0,
            "response_mime_type": "application/json",
        }
        if response_schema:
            config["response_schema"] = response_schema

        # KORREKTUR: Im neuen SDK nutzen wir types.Part(file_data=...)
        # file_id ist der Name (z.B. 'files/abc123')
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part(
                    file_data=types.FileData(
                        file_uri=f"https://generativelanguage.googleapis.com/v1beta/{file_id}",
                        mime_type="application/pdf"
                    )
                ),
                prompt_text
            ],
            config=config
        )

        return response.text.strip()
    raise RuntimeError(f"Unbekannter Provider: {provider}")