from pathlib import Path
from pipeline.openai import upload_pdf_to_openai, run_prompt_with_file
from pipeline.classify import classify_file_id
from pipeline.registry import REGISTRY

def process(pdf_path: Path, output_dir: Path) -> Path:
    # 1) Upload einmal
    file_id = upload_pdf_to_openai(pdf_path)

    # 2) Klassifizieren anhand des hochgeladenen Files
    doc_type = classify_file_id(file_id)
    print(f"🏷️ classify: {doc_type}")
    entry = REGISTRY[doc_type]

    # 3) Prompt aus Registry laufen lassen
    result_text = run_prompt_with_file(
        file_id=file_id,
        prompt_file=entry["prompt"]
    )

    json_path = pdf_path.with_suffix(".json")
    json_path.write_text(result_text, encoding="utf-8")

    output_pdf = output_dir / pdf_path.name
    entry["renderer"](json_path, output_pdf)
    return output_pdf
