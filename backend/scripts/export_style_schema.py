"""把 Pydantic StyleSchema 導出成 JSON Schema，寫到 stdout。

Makefile:
  make sync-schema
Direct:
  python scripts/export_style_schema.py > ../shared/style_schema.json
"""

import json
import sys

from app.schemas.style import StyleSchema


def main() -> None:
    schema = StyleSchema.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://renderstudio.internal/schemas/style.json"
    schema["x-source-of-truth"] = "backend/app/schemas/style.py"
    json.dump(schema, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
