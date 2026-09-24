import copy
import json
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Iterator, Optional

import requests
from txscript import TxScript
from txscript.datapoint import MultivalueDatapointField


@dataclass
class Settings:
    datapoints_to_save: list[str]
    collection_name: str
    unique_natural_key: Optional[list[str]] = field(default_factory=list)
    convert_dates: Optional[bool] = False
    unwind: Optional[str] = None
    keep_first_record: Optional[list[str]] = field(default_factory=list)
    skip_record_insert: Optional[list[dict]] = field(default_factory=list)
    annotation_id: Optional[int] = None
    long_timestamp: Optional[int] = None
    skip_automated_annotations: Optional[bool] = False

    def __post_init__(self):
        for f in fields(self):
            value = getattr(self, f.name)
            if "list[str]" in str(f.type) or "list[dict]" in str(f.type):
                if not isinstance(value, list):
                    raise ValidationError(f"Expected {f.name} to be {f.type}")
            elif not isinstance(value, f.type):
                raise ValidationError(f"Expected {f.name} to be {f.type}")
        self.long_timestamp = int(datetime.now().timestamp() * 1000)

    def set_annotation_id(self, value):
        self.annotation_id = value


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RossumClient:
    def __init__(self, payload: dict) -> None:
        self.base_url = payload["base_url"]
        self.auth_token = payload["rossum_authorization_token"]
        self.headers = self._build_headers()

    def _build_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.auth_token}"}

    def call(self, method: str, endpoint: str, **kwargs) -> dict:
        if endpoint.startswith("https://"):
            url = endpoint
        else:
            url = f"{self.base_url}/api/v1/{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()


class MongoClient:
    def __init__(self, rossum) -> None:
        self.rossum = rossum
        self.ds_url = f"{rossum.base_url + '/svc/data-storage/api/v1/'}"

    def insert_many(self, payload):
        return self.rossum.call("POST", f"{self.ds_url}data/insert_many", data=json.dumps(payload))

    def delete_many(self, payload):
        return self.rossum.call("POST", f"{self.ds_url}data/delete_many", json=payload)

    def find(self, payload):
        return self.rossum.call("POST", f"{self.ds_url}data/find", data=json.dumps(payload))


def rossum_hook_request_handler(payload) -> dict:
    if (
        payload["event"] == "annotation_status"
        and payload["action"] in ("changed")
        and payload["annotation"]["status"] in ("confirmed", "exported")
    ):
        settings = Settings(**payload["settings"])
        settings.set_annotation_id(payload["annotation"]["id"])
        rossum_client = RossumClient(payload)

        if settings.skip_automated_annotations and payload["annotation"].get("automated"):
            return {
                "messages": [{"content": "Automated document, skipping.", "type": "info", "id": None}],
                "operations": [],
            }

        # fool the txscript that its dealing with supported event
        content = rossum_client.call("GET", payload["annotation"]["content"], timeout=20)["content"]
        payload["annotation"]["content"] = content
        payload["event"] = "annotation_content"
        t_payload = TxScript.from_payload(payload)
        mongo_client = MongoClient(rossum_client)
        documents = create_documents_from_annotation(t_payload=t_payload, settings=settings)
        if not documents:
            return t_payload.hook_response()
        process_documents(documents=documents, settings=settings, mongo_client=mongo_client, t_payload=t_payload)

        return t_payload.hook_response()
    else:
        return {
            "messages": [
                {
                    "content": "Runs only on status_change - confirmed/exported statuses.",
                    "type": "info",
                    "id": None,
                }
            ],
            "operations": [],
        }


def process_documents(documents: list, settings: Settings, mongo_client: MongoClient, t_payload: TxScript) -> None:
    skip_insert = remove_existing_objects(documents=documents, mongo=mongo_client, settings=settings)
    if not skip_insert:
        results = mongo_client.find(
            {"collectionName": settings.collection_name, "query": {"annotation_id": settings.annotation_id}}
        )
        if results.get("result"):
            mongo_client.delete_many(
                {"collectionName": settings.collection_name, "filter": {"annotation_id": settings.annotation_id}}
            )
        create_records_in_ds(documents=documents, t_payload=t_payload, mongo_client=mongo_client, settings=settings)
    return


def create_documents_from_annotation(t_payload: TxScript, settings: Settings) -> list:
    # simplify raw annotation payload based datapoints_to_save settings, optionally unwind or remove invalid records as defined by skip_record_insert
    simplified_content = simplify_content(t_payload, settings)
    if settings.unwind:
        simplified_content = unwind(simplified_object=simplified_content[0], paths=[settings.unwind])
        simplified_content = deduplicate_objects(objects=simplified_content)
    if settings.skip_record_insert:
        simplified_content = remove_documents(simplified_content=simplified_content, settings=settings)
    return simplified_content


def deduplicate_objects(objects: list) -> list:
    unique_strs = set(json.dumps(obj) for obj in objects)
    return [json.loads(jsonstr) for jsonstr in unique_strs]


def remove_documents(simplified_content: list, settings: Settings) -> list:
    if not settings.skip_record_insert:
        return simplified_content

    included_documents = []
    for doc in simplified_content:
        skip_document = check_document_conditions(conditions=settings.skip_record_insert, doc=doc)
        distinct = set(skip_document)
        if True not in distinct:
            included_documents.append(doc)
    return included_documents


def check_document_conditions(conditions: list, doc: dict) -> Iterator[bool]:
    for condition in conditions:
        yield check_document_condition(condition=condition, doc=doc)


def check_document_condition(condition: dict, doc: dict) -> bool:
    for key in condition:
        if condition[key] != get_value(document=doc, paths=key.split(".")):
            return False
    return True


def get_value(document: dict, paths: list) -> Any:
    paths.reverse()
    path = paths.pop()
    if path in document and paths:
        value = get_value(document=document[path], paths=paths)
    elif path in document:
        value = document[path]
    else:
        value = ""
    return value


def simplify_content(t_payload: TxScript, settings: Settings) -> list:
    # all the values need to be cast to primitive types because txscript field overloaded class cannot be easily deep copied ...
    def get_and_cast_value(
        datapoint, schema_definition: dict, settings: Settings, value_type: str = None
    ) -> datetime | str | int:
        value_type = value_type if value_type else (schema_definition.get("enum_value_type") if schema_definition.get("enum_value_type") else schema_definition.get("type"))
        if value_type == "date" and not settings.convert_dates:
            value = datapoint.attr.normalized_value
        elif value_type == "date" and settings.convert_dates:
            value = datetime.strptime(datapoint, "%Y-%m-%d")
        elif value_type == "number":
            value = round(datapoint, 5)
        else:
            value = datapoint.value
        return value

    simplified_object = {}
    for key in settings.datapoints_to_save:
        key = key.split(".")[-1]
        datapoint = getattr(t_payload.field, key)
        if isinstance(datapoint.attr._field, MultivalueDatapointField):
            datapoints = datapoint.all_values
            # parent = datapoint.parent.attrs["schema_id"]
            parent = datapoint.attr._field.schema.get("parent")
            if parent == settings.unwind:
                for index, datapoint in enumerate(datapoints):
                    value = get_and_cast_value(
                        datapoint=datapoint, schema_definition=datapoint.attr._field.schema, settings=settings
                    )
                    if parent in simplified_object:
                        if len(simplified_object[parent]) - 1 >= index:
                            simplified_object[parent][index][key] = value
                        else:
                            simplified_object[parent].append({key: value})
                    else:
                        simplified_object[parent] = []
                        simplified_object[parent].append({key: value})
        else:
            value = get_and_cast_value(
                datapoint=datapoint, schema_definition=datapoint.attr._field.schema, settings=settings
            )
            simplified_object[key] = value
    return [simplified_object]


def unwind(simplified_object: dict, paths: list) -> list:
    def create_unwind_copy(template_copy, element, paths) -> dict:
        last_path = paths.pop()
        for path in paths:
            template_copy = template_copy[path]
        template_copy[last_path] = element
        return template_copy

    def delete_key(simplified_object, paths):
        for path in paths:
            if len(paths) == 1:
                del simplified_object[path]
                return
            else:
                del paths[0]
                delete_key(simplified_object[path], paths)

    transformed_objects = []
    template_object = copy.deepcopy(simplified_object)
    for path in paths:
        if path not in simplified_object:
            raise Exception("Unwind of non existent key defined. Change the key value or remove the setting.")
        elif isinstance(simplified_object[path], list):
            delete_key(template_object, copy.deepcopy(paths))
            for elem in simplified_object[path]:
                template_copy = copy.deepcopy(template_object)
                create_unwind_copy(template_copy, elem, copy.deepcopy(paths))
                transformed_objects.append(template_copy)
        elif isinstance(simplified_object[path], dict):
            simplified_object = simplified_object[path]
        else:
            raise Exception("Unwind of primitive values defined.")
    return transformed_objects


def remove_existing_objects(documents: list, mongo: MongoClient, settings: Settings) -> bool | None:
    # this function is making sure no duplicates are in the collection if unique natural key is defined and/or if also keep first record is
    # defined. it either deltes all existing records with the same natural key or it preserves the record with oldest insertion date and removes all
    # remaining newer records with the same natural key as long as the primary key is the same as is of the oldest record
    for doc in documents:
        filter_cond = None
        if settings.unique_natural_key:
            filter_cond = create_filter_query(document=doc, natural_key=settings.unique_natural_key)
        if settings.keep_first_record and filter_cond:
            results = mongo.find(
                {"collectionName": settings.collection_name, "query": filter_cond, "sort": {"created_at": -1}}
            )
            if len(results["result"]) > 1:
                oids = []
                # only want to keep the oldest record if the primary key did not change, otherwise replace them all
                oldest_record = results["result"][0]
                for pk in settings.keep_first_record:
                    if oldest_record.get(pk, "") != get_value(document=doc, paths=pk.split(".")):
                        oids.append({"_id": oldest_record["_id"]})
                        break
                # get ids of all records sharing the same natural key except the oldest one
                for res in results["result"][1:]:
                    oids.append({"_id": res["_id"]})
                filter_cond = {"$or": oids}
                mongo.delete_many({"collectionName": settings.collection_name, "filter": filter_cond})
                return True
            elif len(results["result"]) == 1:
                return True
            return False
        elif filter_cond:
            mongo.delete_many({"collectionName": settings.collection_name, "filter": filter_cond})
            return False


def create_filter_query(document: dict, natural_key: list[str]) -> dict:
    query = {}
    for key in natural_key:
        query[key] = get_value(document=document, paths=key.split("."))
    return query


def create_records_in_ds(documents: list, t_payload: TxScript, mongo_client: MongoClient, settings: Settings) -> None:
    for doc in documents:
        doc["annotation_id"] = settings.annotation_id
        doc["created_at"] = {"$date": {"$numberLong": settings.long_timestamp}}
    mongo_client.insert_many({"collectionName": settings.collection_name, "documents": documents})
    t_payload.show_info(f"Document(s) inserted for annotation {settings.annotation_id}")
    return


def find_by_schema_id(content: dict, schema_id: str) -> list:
    accumulator = []
    for node in content:
        if node["schema_id"] == schema_id:
            accumulator.append(node)
        elif "children" in node:
            accumulator.extend(find_by_schema_id(node["children"], schema_id))
    return accumulator


def find_by_datapoint_id(content, datapoint_id) -> dict | list | None:
    for node in content:
        if node["id"] == datapoint_id:
            return node
        elif "children" in node:
            result = find_by_datapoint_id(node["children"], datapoint_id)
            if result:
                return result
            else:
                continue
    return None


def get_schema_field_by_id(content: dict | list, schema_id: str) -> dict | list | None:
    if not isinstance(content, list):
        return get_schema_field_by_id([content], schema_id)
    for datapoint in content:
        if "id" in datapoint and datapoint["id"] == schema_id:
            return datapoint
        else:
            if "children" in datapoint:
                datapoint = get_schema_field_by_id(datapoint["children"], schema_id)
                if datapoint is not None:
                    return datapoint
    return None