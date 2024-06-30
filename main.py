from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError
from typing import List, Type
from enum import Enum
from tester import Tester
from spec.fix import FixTester
from typing import List, Dict, Any, get_args, get_origin
import logging

app = FastAPI()

templates = Jinja2Templates(directory="templates")

testers = [
    {"name": "FIX", "class": FixTester},
]

index = 0
database = {}


def pydantic_to_json_map(model: BaseModel) -> List[Dict[str, Any]]:
    fields = model.model_fields
    json_map = []

    for field_name, field_info in fields.items():
        field_type = field_info.annotation
        field_dict = {"name": field_name}

        if get_origin(field_type) is Enum or issubclass(field_type, Enum):
            field_dict["type"] = "enum"
            field_dict["options"] = [e.value for e in field_type]
        else:
            field_dict["type"] = field_type.__name__

        json_map.append(field_dict)

    return json_map


@app.get("/")
async def root(request: Request):
    config_types = []
    parameters_types = []

    if request.query_params.get("tester"):
        tester: Tester = next(
            (
                t["class"]
                for t in testers
                if t["name"] == request.query_params.get("tester")
            ),
            None,
        )
        if tester is not None:
            config_types = pydantic_to_json_map(tester.get_config_model())
            parameters_types = pydantic_to_json_map(tester.get_parameter_model())

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "testers": [t["name"] for t in testers],
            "config_types": config_types,
            "parameters_types": parameters_types,
        },
    )


@app.post("/tester")
async def create_tester(request: Request):
    form = await request.form()
    tester_name = form.get("tester")

    tester = next(
        (t["class"] for t in testers if t["name"] == tester_name),
        None,
    )

    config_model = tester.get_config_model()

    try:
        config = config_model.parse_obj(form)
        database[index] = {
            "config": config,
            "tester": tester,
            "logger": logging.getLogger(f"Tester{index}"),
        }
        database[index]["instance"] = tester(config, database[index]["logger"])
    except ValidationError as e:
        return {"success": False, "errors": e.errors()}

    return {"success": True, "index": index}


@app.get("/tester/{index}")
async def run_tester(index: int, request: Request):
    form = await request.form()
    database[index]["instance"].run_test(form)
    return {"success": True}
